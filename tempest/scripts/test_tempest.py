"""Offline test suite for the bundled tempest CLI.

All HTTP is mocked at the client seam (TempestClient._get is replaced by a
FakeTransport that records paths/params and returns canned REST documents),
and UDP paths are tested by feeding CANNED DATAGRAM BYTES to the pure
handle_datagram()/decode_message() decoders — no socket is ever created or
bound (the suite never touches socket.socket). The suite is fully offline and
passes the proxy-trap rerun. Tempest is a keyed API, so there are deliberately
NO live-call test cases (the AGENTS.md network policy is mock-everything for
keyed APIs).

Covers the four contract behavior classes: --help output, argument-error
paths, --dry-run plans, and mocked-client logic — plus the documented
multi-step pipelines (stations -> current, stations -> forecast with unit
conversion, obs day history) and every UDP message family (obs_st UDP 18
positions vs REST 22, obs_air, obs_sky, rapid_wind's single "ob" array,
evt_precip/evt_strike's single "evt" arrays, hub_status/device_status named
fields) dispatched by type.
"""

import contextlib
import importlib.machinery
import importlib.util
import io
import json
import pathlib
import sys
import unittest
from unittest.mock import patch

SCRIPT = pathlib.Path(__file__).resolve().parent / "tempest"
LOADER = importlib.machinery.SourceFileLoader("tempest_cli", str(SCRIPT))
SPEC = importlib.util.spec_from_loader(LOADER.name, LOADER)
ts = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = ts  # so unittest.mock.patch("tempest_cli....") resolves
LOADER.exec_module(ts)

# ---------------------------------------------------------------------------
# Canned UDP datagrams (bytes, exactly as the hub broadcasts them).
# obs_st uses the documented 18-position UDP record; REST returns 22.
# ---------------------------------------------------------------------------

OBS_ST_DATAGRAM = (
    b'{"serial_number":"ST-00000512","type":"obs_st","hub_sn":"HB-00013030",'
    b'"obs":[[1588948614,0.18,0.22,0.27,144,6,1017.57,22.37,50.26,328,0.03,3,'
    b'0.0,0,0,0,2.410,1]],"firmware_revision":129}'
)
RAPID_WIND_DATAGRAM = (
    b'{"serial_number":"SK-00008453","type":"rapid_wind","hub_sn":"HB-00000001",'
    b'"ob":[1493322445,2.3,128]}'
)
EVT_PRECIP_DATAGRAM = (
    b'{"serial_number":"SK-00008453","type":"evt_precip","hub_sn":"HB-00000001",'
    b'"evt":[1493322445]}'
)
EVT_STRIKE_DATAGRAM = (
    b'{"serial_number":"AR-00004049","type":"evt_strike","hub_sn":"HB-00000001",'
    b'"evt":[1493322445,27,3848]}'
)
HUB_STATUS_DATAGRAM = (
    b'{"serial_number":"HB-00000001","type":"hub_status","firmware_revision":"35",'
    b'"uptime":1670133,"rssi":-62,"timestamp":1495724691,"reset_flags":"BOR,PIN,POR",'
    b'"seq":48,"fs":[1,0,15675411,524288],"radio_stats":[2,1,0,3,2839],"mqtt_stats":[1,0]}'
)
DEVICE_STATUS_DATAGRAM = (
    b'{"serial_number":"AR-00004049","type":"device_status","hub_sn":"HB-00000001",'
    b'"timestamp":1510855923,"uptime":2189,"voltage":3.50,"firmware_revision":17,'
    b'"rssi":-17,"hub_rssi":-87,"sensor_status":0,"debug":0}'
)
OBS_AIR_DATAGRAM = (
    b'{"serial_number":"AR-00004049","type":"obs_air","hub_sn":"HB-00000001",'
    b'"obs":[[1493164835,835.0,10.0,45,0,0,3.46,1]],"firmware_revision":17}'
)
OBS_SKY_DATAGRAM = (
    b'{"serial_number":"SK-00008453","type":"obs_sky","hub_sn":"HB-00000001",'
    b'"obs":[[1493321340,9000,10,0.0,2.6,4.6,7.4,187,3.12,1,130,null,0,3]],'
    b'"firmware_revision":29}'
)
GARBAGE_DATAGRAM = b"\x00\x01not-json-at-all"


def run_main(argv):
    """Run the CLI main() with patched stdout; returns (exit_code, stdout).

    SystemExit is caught and converted to a code so error paths can assert
    on exit codes without exception plumbing.
    """
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
        try:
            ts.main(["tempest"] + argv)
            code = 0
        except SystemExit as exc:
            code = exc.code if isinstance(exc.code, int) else (0 if exc.code is None else 1)
    return code, out.getvalue()


def run_main_err(argv):
    """Like run_main but also captures stderr: (exit_code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            ts.main(["tempest"] + argv)
            code = 0
        except SystemExit as exc:
            code = exc.code if isinstance(exc.code, int) else (0 if exc.code is None else 1)
    return code, out.getvalue(), err.getvalue()


# ---------------------------------------------------------------------------
# Fake REST transport: records requests, replays canned documents
# ---------------------------------------------------------------------------

STATION_DOC = {
    "status": {"status_code": 0, "status_message": "SUCCESS"},
    "stations": [{
        "station_id": 12799, "name": "Home", "public_name": "Home",
        "latitude": 42.37, "longitude": -71.06,
        "timezone": "America/New_York", "timezone_offset_minutes": -300,
        "station_meta": {"elevation": 1567.65, "share_with_wf": True, "share_with_wu": True},
        "is_local_mode": False,
        "devices": [
            {"device_id": 60526, "serial_number": "ST-00012345", "device_type": "ST",
             "hardware_revision": "3", "firmware_revision": "165",
             "device_meta": {"agl": 2.2, "name": "Backyard", "environment": "outdoor"}},
            {"device_id": 60500, "serial_number": "HB-00000001", "device_type": "HB",
             "hardware_revision": "3", "firmware_revision": "35",
             "device_meta": {"name": "Hub"}},
            {"device_id": 60599, "serial_number": None, "device_type": "SK",
             "hardware_revision": "2", "firmware_revision": "29",
             "device_meta": {"name": "Old Sky"}},
        ],
        "station_items": [],
    }],
}


class FakeTransport:
    """Replaces TempestClient._get; records every request, replays canned docs."""

    def __init__(self, responses=None):
        self.requests = []
        self.responses = responses or {}

    def __call__(self, path, params=None):
        self.requests.append({"path": path, "params": dict(params or {})})
        if path in self.responses:
            return self.responses[path]
        if path.startswith("/observations/device/"):
            return {"obs": [OBS_ROW_ST], "type": "obs_st"}
        if path == "/better_forecast":
            return FORECAST_DOC
        if path == "/stations":
            return STATION_DOC
        raise AssertionError(f"unexpected path {path}")


# Canned REST documents
OBS_ROW_ST = [1650843455, 0.18, 0.22, 0.27, 144, 6, 1017.57, 22.37, 50.26, 328,
              0.03, 3, 0.0, 0, 0, 0, 2.410, 1, 5.2, 4.8, 5.2, 1]
FORECAST_DOC = {
    "status": {"status_code": 0, "status_message": "SUCCESS"},
    "current_conditions": {"air_temperature": 18.2, "conditions": "Mostly Clear",
                           "icon": "partly-cloudy-day", "relative_humidity": 61,
                           "station_pressure": 1015.4, "wind_avg": 2.1,
                           "wind_direction": 225, "wind_direction_cardinal": "SW",
                           "feels_like": 18.2},
    "forecast": {
        "daily": [
            {"day_start_local": 1778385600, "air_temp_high": 25.4, "air_temp_low": 15.1,
             "conditions": "Partly cloudy", "precip_probability": 10, "precip_type": "rain",
             "sunrise": 1778378400, "sunset": 1778425200},
            {"day_start_local": 1778472000, "air_temp_high": 22.0, "air_temp_low": 12.0,
             "conditions": "Rainy", "precip_probability": 80, "precip_type": "rain"},
        ],
        "hourly": [
            {"time": 1778388000, "local_hour": 10, "local_day": 10, "air_temperature": 19.8,
             "precip_probability": 5, "conditions": "Sunny"},
            {"time": 1778391600, "local_hour": 11, "local_day": 10, "air_temperature": 20.4,
             "precip_probability": 45, "conditions": "Cloudy"},
        ],
    },
    "units": {"units_temp": "c", "units_wind": "mps", "units_precip": "mm",
              "units_pressure": "mb", "units_distance": "km"},
    "latitude": 42.37, "longitude": -71.06,
    "timezone": "America/New_York", "timezone_offset_minutes": -300,
}
FORECAST_DOC_F = json.loads(json.dumps(FORECAST_DOC))
FORECAST_DOC_F["units"] = {"units_temp": "f", "units_wind": "mph", "units_precip": "in",
                           "units_pressure": "inhg", "units_distance": "mi"}
FORECAST_DOC_F["current_conditions"]["air_temperature"] = 64.8
FORECAST_DOC_F["forecast"]["daily"][0]["air_temp_high"] = 77.7

STATIONS_ONLY = {"/stations": STATION_DOC}


def patch_token(token="tok-test"):
    return patch.object(ts, "resolve_token", return_value=token)


class CliTestCase(unittest.TestCase):
    """Base: fresh GLOBAL_FLAGS per test, stdout captured via run_main."""

    def setUp(self):
        ts.GLOBAL_FLAGS.clear()
        ts.GLOBAL_FLAGS.update(
            {"json": False, "dry_run": False, "force": False, "quiet": False, "verbose": False})
        ts.QUIET = False


# ---------------------------------------------------------------------------
# Class 1: --help output
# ---------------------------------------------------------------------------

class HelpTests(CliTestCase):
    def test_help_lists_all_subcommands(self):
        code, out = run_main(["--help"])
        self.assertEqual(code, 0)
        for noun in ("stations", "current", "obs", "forecast", "udp"):
            self.assertIn(noun, out)

    def test_udp_help_documents_listen(self):
        code, out = run_main(["udp", "--help"])
        self.assertEqual(code, 0)
        self.assertIn("listen", out)
        self.assertIn("50222", out + ts.build_parser().format_help())

    def test_forecast_help_shows_flags(self):
        code, out = run_main(["forecast", "--help"])
        self.assertEqual(code, 0)
        self.assertIn("--station-id", out)
        self.assertIn("--days", out)

    def test_main_help_epilog_documents_global_flag_positions(self):
        code, out = run_main(["--help"])
        self.assertEqual(code, 0)
        self.assertIn("anywhere", out)


# ---------------------------------------------------------------------------
# Class 2: argument-error paths
# ---------------------------------------------------------------------------

class ArgumentErrorsTests(CliTestCase):
    def test_no_command_prints_help_and_exits_1(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            with self.assertRaises(SystemExit) as ctx:
                ts.main(["tempest"])
        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("usage", out.getvalue())

    def test_udp_without_subcommand_is_an_error(self):
        code, _, err = run_main_err(["udp"])
        self.assertEqual(code, 2)
        self.assertIn("udp requires a subcommand", err)

    def test_obs_requires_device_id(self):
        code, _, err = run_main_err(["obs"])
        self.assertEqual(code, 2)
        self.assertIn("--device-id", err)

    def test_missing_token_dies_with_guidance(self):
        with patch_token(""):
            code, _, err = run_main_err(["stations"])
        self.assertEqual(code, 1)
        self.assertIn("TEMPEST_TOKEN not set", err)

    def test_missing_token_is_fine_for_dry_run(self):
        with patch_token(""):
            code, out = run_main(["stations", "--dry-run", "--json"])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["dry_run"], True)

    def test_unknown_station_id_exits_1(self):
        fake = FakeTransport(STATIONS_ONLY)
        with patch_token(), patch.object(ts.TempestClient, "_get", fake):
            code, _, err = run_main_err(["current", "--station-id", "99999999"])
        self.assertEqual(code, 1)
        self.assertIn("99999999 not found", err)


# ---------------------------------------------------------------------------
# Class 3: --dry-run behavior (plans are JSON, exit 0, zero network)
# ---------------------------------------------------------------------------

class DryRunTests(CliTestCase):
    def test_current_dry_run_plan_shape(self):
        code, out = run_main(["current", "--station-id", "12799", "--device-id", "60526",
                              "--dry-run", "--json"])
        self.assertEqual(code, 0)
        plan = json.loads(out)
        self.assertEqual(plan["dry_run"], True)
        self.assertEqual(plan["command"], "current")
        self.assertEqual(plan["station_id"], 12799)
        self.assertEqual(plan["device_id"], 60526)

    def test_forecast_dry_run_plan_shape(self):
        code, out = run_main(["forecast", "--station-id", "12799", "--days", "3",
                              "--dry-run", "--json"])
        self.assertEqual(code, 0)
        plan = json.loads(out)
        self.assertEqual(plan["command"], "forecast")
        self.assertEqual(plan["days"], 3)

    def test_obs_dry_run_plan_shape(self):
        code, out = run_main(["obs", "--device-id", "60526", "--days", "2", "--dry-run", "--json"])
        self.assertEqual(code, 0)
        plan = json.loads(out)
        self.assertEqual(plan["command"], "obs")
        self.assertEqual(plan["device_id"], 60526)
        self.assertEqual(plan["days"], 2)

    def test_stations_dry_run_plan_shape(self):
        code, out = run_main(["stations", "--dry-run", "--json"])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["command"], "stations")


# ---------------------------------------------------------------------------
# Class 4: mocked REST client logic (no real network anywhere)
# ---------------------------------------------------------------------------

class RestClientTests(CliTestCase):
    def test_stations_json_unwraps_stationset_wrapper(self):
        fake = FakeTransport(STATIONS_ONLY)
        with patch_token(), patch.object(ts.TempestClient, "_get", fake):
            code, out = run_main(["stations", "--json"])
        self.assertEqual(code, 0)
        doc = json.loads(out)
        self.assertEqual(doc["stations"][0]["station_id"], 12799)
        self.assertEqual(len(doc["stations"][0]["devices"]), 3)

    def test_current_pipeline_stations_then_latest_observation(self):
        fake = FakeTransport(STATIONS_ONLY)
        with patch_token(), patch.object(ts.TempestClient, "_get", fake):
            code, out = run_main(["current", "--json"])
        self.assertEqual(code, 0)
        doc = json.loads(out)
        # auto-selection picked the ST device and skipped the HB hub
        self.assertEqual(doc["device_id"], 60526)
        self.assertEqual(doc["type"], "obs_st")
        obs = doc["observation"]
        self.assertIsInstance(obs["air_temperature"], (int, float))
        self.assertEqual(obs["air_temperature"], 22.37)
        self.assertEqual(obs["air_temperature_unit"], "C")
        self.assertEqual(fake.requests[-1]["path"], "/observations/device/60526")
        # latest-only mode sends no day_offset / time range
        self.assertNotIn("day_offset", fake.requests[-1]["params"])

    def test_current_positional_flag_consumption_from_handler_argv(self):
        # handler-owns-flags dispatch: "--device-id 60526" after "current"
        fake = FakeTransport(STATIONS_ONLY)
        with patch_token(), patch.object(ts.TempestClient, "_get", fake):
            code, out = run_main(["current", "--device-id", "60526", "--json"])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["device_id"], 60526)

    def test_obs_pipeline_requests_day_offset_and_decodes_rows(self):
        fake = FakeTransport(STATIONS_ONLY)
        with patch_token(), patch.object(ts.TempestClient, "_get", fake):
            code, out = run_main(["obs", "--device-id", "60526", "--days", "2", "--json"])
        self.assertEqual(code, 0)
        doc = json.loads(out)
        self.assertEqual(doc["count"], 1)
        self.assertEqual(doc["observations"][0]["local_day_rain_accumulation"], 5.2)
        self.assertEqual(fake.requests[-1]["params"]["day_offset"], 2)

    def test_forecast_pipeline_reads_nested_forecast_key(self):
        fake = FakeTransport(STATIONS_ONLY)
        with patch_token(), patch.object(ts.TempestClient, "_get", fake):
            code, out = run_main(["forecast", "--json"])
        self.assertEqual(code, 0)
        doc = json.loads(out)
        self.assertEqual(doc["station_id"], 12799)
        daily = doc["forecast"]["forecast"]["daily"]
        self.assertEqual(daily[0]["air_temp_high"], 25.4)
        self.assertEqual(doc["forecast"]["units"]["units_temp"], "c")

    def test_forecast_human_output_celsius_station_converts_to_f(self):
        fake = FakeTransport(STATIONS_ONLY)
        with patch_token(), patch.object(ts.TempestClient, "_get", fake):
            code, out = run_main(["forecast"])
        self.assertEqual(code, 0)
        # 25.4C * 9/5 + 32 = 77.72 -> displayed as 78 with :.0f
        self.assertIn("78", out)
        # hourly local_hour rendered HH:00
        self.assertIn("10:00", out)

    def test_forecast_human_output_fahrenheit_station_not_double_converted(self):
        fake = FakeTransport({**STATIONS_ONLY, "/better_forecast": FORECAST_DOC_F})
        with patch_token(), patch.object(ts.TempestClient, "_get", fake):
            code, out = run_main(["forecast"])
        self.assertEqual(code, 0)
        # units_temp=f: 77.7 stays 77.7 -> displayed 78; a double conversion
        # would render 172 (77.7*9/5+32), which must not appear.
        self.assertIn("78", out)
        self.assertNotIn("172", out)

    def test_client_sends_token_as_query_parameter(self):
        # Documented auth: token travels as a query parameter (apiKey in:query),
        # never as a header. Verified at the requests.get seam.
        class FakeResp:
            status_code = 200
            text = ""
            def json(self):
                return STATION_DOC
        recorded = {}

        def fake_get(url, params=None, timeout=None):
            recorded["url"] = url
            recorded["params"] = params
            return FakeResp()

        with patch.object(ts.requests, "get", side_effect=fake_get):
            ts.TempestClient(token="tok-query").get_stations()
        self.assertEqual(recorded["params"]["token"], "tok-query")
        self.assertIn("/stations", recorded["url"])
        self.assertIn("swd.weatherflow.com", recorded["url"])

    def test_client_401_message_names_token(self):
        class Err401:
            status_code = 401
            text = ""
        with patch.object(ts.requests, "get", return_value=Err401()):
            client = ts.TempestClient(token="bad")
            with contextlib.redirect_stderr(io.StringIO()) as err:
                with self.assertRaises(SystemExit) as ctx:
                    client._get("/stations")
        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("401", err.getvalue())

    def test_env_file_fallback_token(self):
        with patch.dict("os.environ", {"TEMPEST_TOKEN": ""}), \
             patch.object(ts, "ENV_FILE", "/nonexistent/.tempest.env"):
            self.assertEqual(ts.resolve_token(), "")
        with patch.dict("os.environ", {"TEMPEST_TOKEN": "  "}), \
             patch.object(ts, "ENV_FILE", "/nonexistent/.tempest.env"):
            self.assertEqual(ts.resolve_token(), "")


# ---------------------------------------------------------------------------
# UDP decoding from canned datagram bytes — no sockets, no binds
# ---------------------------------------------------------------------------

class UdpDecoderTests(CliTestCase):
    def test_obs_st_datagram_decodes_all_18_udp_positions(self):
        results = ts.handle_datagram(OBS_ST_DATAGRAM)
        self.assertEqual(len(results), 1)
        _, payload = results[0]
        self.assertEqual(payload["type"], "obs_st")
        self.assertEqual(payload["serial_number"], "ST-00000512")
        obs = payload["observation"]
        self.assertEqual(obs["epoch"], 1588948614)
        self.assertEqual(obs["wind_avg"], 0.22)          # index 2
        self.assertEqual(obs["wind_direction"], 144)      # index 4
        self.assertEqual(obs["station_pressure"], 1017.57)  # index 6 (MB)
        self.assertEqual(obs["air_temperature"], 22.37)   # index 7 (C)
        self.assertEqual(obs["rain_accumulation"], 0.0)   # index 12 (mm)
        self.assertEqual(obs["battery"], 2.410)           # index 16
        self.assertEqual(obs["report_interval"], 1)       # index 17 (last UDP position)
        # UDP record ends at index 17: REST-only Nearcast fields decode as None
        self.assertIsNone(obs["nc_rain_accumulation"])
        self.assertIsNone(obs["precip_analysis_type"])
        # metric-native units preserved on the payload
        self.assertEqual(obs["wind_avg_unit"], "m/s")
        self.assertEqual(obs["air_temperature_unit"], "C")
        self.assertEqual(obs["rain_accumulation_unit"], "mm")

    def test_decode_obs_handles_full_rest_22_position_row(self):
        decoded = ts.decode_obs(OBS_ROW_ST, "obs_st")
        self.assertEqual(decoded["local_day_rain_accumulation"], 5.2)
        self.assertEqual(decoded["nc_rain_accumulation"], 4.8)
        self.assertEqual(decoded["precip_analysis_type"], 1)

    def test_decode_obs_tolerates_short_rows_with_none(self):
        decoded = ts.decode_obs([1588948614, 0.18, 0.22], "obs_st")
        self.assertEqual(decoded["wind_avg"], 0.22)
        self.assertIsNone(decoded["air_temperature"])
        self.assertIsNone(decoded["battery"])

    def test_rapid_wind_single_ob_array_not_iterated_elementwise(self):
        # Regression: the old handler iterated msg["ob"] like an obs row list
        # (TypeError: unsupported operand type(s) for -: 'int' and 'str'-style
        # crash on the epoch number). rapid_wind carries ONE array under "ob".
        results = ts.handle_datagram(RAPID_WIND_DATAGRAM)
        self.assertEqual(len(results), 1)
        _, payload = results[0]
        self.assertEqual(payload["type"], "rapid_wind")
        self.assertEqual(payload["wind_speed_mps"], 2.3)
        self.assertEqual(payload["wind_direction"], 128)
        self.assertIsNotNone(payload["timestamp"])

    def test_evt_precip_single_evt_array(self):
        results = ts.handle_datagram(EVT_PRECIP_DATAGRAM)
        self.assertEqual(len(results), 1)
        _, payload = results[0]
        self.assertEqual(payload["type"], "evt_precip")
        self.assertIsNotNone(payload["timestamp"])

    def test_evt_strike_distance_and_energy(self):
        results = ts.handle_datagram(EVT_STRIKE_DATAGRAM)
        _, payload = results[0]
        self.assertEqual(payload["type"], "evt_strike")
        self.assertEqual(payload["distance_km"], 27)
        self.assertEqual(payload["energy"], 3848)

    def test_hub_status_named_fields_dispatch(self):
        # hub_status carries named fields (no payload array). The old handler
        # printed msg["freq"], which does not exist in the current protocol.
        results = ts.handle_datagram(HUB_STATUS_DATAGRAM, show_all=True)
        self.assertEqual(len(results), 1)
        _, payload = results[0]
        self.assertEqual(payload["type"], "hub_status")
        self.assertEqual(payload["serial_number"], "HB-00000001")
        self.assertEqual(payload["uptime"], 1670133)
        self.assertEqual(payload["reset_flags"], "BOR,PIN,POR")
        self.assertEqual(payload["radio_stats"], [2, 1, 0, 3, 2839])

    def test_hub_status_hidden_by_default(self):
        self.assertEqual(ts.handle_datagram(HUB_STATUS_DATAGRAM), [])

    def test_device_status_named_fields(self):
        results = ts.handle_datagram(DEVICE_STATUS_DATAGRAM, show_all=True)
        _, payload = results[0]
        self.assertEqual(payload["type"], "device_status")
        self.assertEqual(payload["voltage"], 3.50)
        self.assertEqual(payload["sensor_status"], 0)

    def test_obs_air_and_obs_sky_dispatch(self):
        air = ts.handle_datagram(OBS_AIR_DATAGRAM)[0][1]
        self.assertEqual(air["observation"]["station_pressure"], 835.0)
        self.assertEqual(air["observation"]["air_temperature"], 10.0)
        sky = ts.handle_datagram(OBS_SKY_DATAGRAM)[0][1]
        self.assertEqual(sky["observation"]["illuminance"], 9000)
        self.assertIsNone(sky["observation"]["local_day_rain_accumulation"])  # null over UDP

    def test_garbage_datagram_returns_no_results(self):
        self.assertEqual(ts.handle_datagram(GARBAGE_DATAGRAM), [])
        # show_all surfaces a raw preview instead of crashing
        results = ts.handle_datagram(GARBAGE_DATAGRAM, show_all=True)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][1]["type"], "unparseable")

    def test_unknown_type_ignored_by_default_and_listed_with_show_all(self):
        weird = b'{"type":"something_new","serial_number":"XX-1"}'
        self.assertEqual(ts.handle_datagram(weird), [])
        results = ts.handle_datagram(weird, show_all=True)
        self.assertEqual(results[0][1]["type"], "something_new")

    def test_decode_message_dispatches_on_type_before_indexing(self):
        # non-obs families must never be routed into the obs positional decoder
        self.assertEqual(ts.decode_message({"type": "rapid_wind", "ob": [1, 2.3, 128]})[0][1]["wind_speed_mps"], 2.3)
        self.assertEqual(ts.decode_message({"type": "evt_precip", "evt": [1493322445]})[0][1]["type"], "evt_precip")
        self.assertEqual(ts.decode_message({"type": "hub_status", "uptime": 5, "seq": 1}, show_all=True)[0][1]["type"], "hub_status")

    def test_listen_handler_consumes_canned_datagrams_without_sockets(self):
        # udp_listen's socket is fully mocked: canned datagram BYTES are fed
        # to the decoder through a fake recvfrom, so the suite never creates
        # or binds a real socket anywhere.
        canned = [OBS_ST_DATAGRAM, RAPID_WIND_DATAGRAM, EVT_PRECIP_DATAGRAM]
        fake_sock = unittest.mock.MagicMock()
        fake_sock.recvfrom.side_effect = [
            (canned[0], ("127.0.0.1", 50222)),
            (canned[1], ("127.0.0.1", 50222)),
            (canned[2], ("127.0.0.1", 50222)),
            ts.socket.timeout("stop"),
        ]
        out = io.StringIO()
        args = type("A", (), {"port": 50222, "timeout": 1, "show_all": False})()
        with contextlib.redirect_stdout(out):
            with patch.object(ts.socket, "socket", return_value=fake_sock):
                ts.udp_listen(args)
        text = out.getvalue()
        self.assertIn("ST-00000512", text)
        self.assertIn("Rapid Wind", text)
        self.assertIn("Rain started", text)
        fake_sock.close.assert_called_once()

    def test_listen_json_stream_carries_family_payloads(self):
        fake_sock = unittest.mock.MagicMock()
        fake_sock.recvfrom.side_effect = [
            (RAPID_WIND_DATAGRAM, ("127.0.0.1", 50222)),
            ts.socket.timeout("stop"),
        ]
        ts.GLOBAL_FLAGS["json"] = True
        out = io.StringIO()
        args = type("A", (), {"port": 50222, "timeout": 1, "show_all": False})()
        with contextlib.redirect_stdout(out):
            with patch.object(ts.socket, "socket", return_value=fake_sock):
                ts.udp_listen(args)
        doc = json.loads(out.getvalue().strip().splitlines()[-1])
        self.assertEqual(doc["type"], "rapid_wind")
        self.assertEqual(doc["wind_speed_mps"], 2.3)
        fake_sock.close.assert_called_once()


# ---------------------------------------------------------------------------
# Documented pipeline wiring: each stage's output feeds the next
# ---------------------------------------------------------------------------

class PipelineTests(CliTestCase):
    def test_station_ids_from_stations_feed_current(self):
        fake = FakeTransport(STATIONS_ONLY)
        with patch_token(), patch.object(ts.TempestClient, "_get", fake):
            _, stations_out = run_main(["stations", "--json"])
            sid = json.loads(stations_out)["stations"][0]["station_id"]
            did = next(d["device_id"] for d in
                       json.loads(stations_out)["stations"][0]["devices"]
                       if d["device_type"] == "ST")
            self.assertIsInstance(sid, int)
            self.assertIsInstance(did, int)
            _, current_out = run_main(["current", "--station-id", str(sid),
                                       "--device-id", str(did), "--json"])
            doc = json.loads(current_out)
            self.assertEqual(doc["device_id"], did)
            # observation dict carries metric-native numeric types for jq math
            self.assertIsInstance(doc["observation"]["air_temperature"], float)
            self.assertIsInstance(doc["observation"]["rain_accumulation"], (int, float))

    def test_rain_watch_pipeline_obs_day_total_then_evt_precip_stream(self):
        fake = FakeTransport(STATIONS_ONLY)
        with patch_token(), patch.object(ts.TempestClient, "_get", fake):
            _, obs_out = run_main(["obs", "--device-id", "60526", "--days", "1", "--json"])
            doc = json.loads(obs_out)
            self.assertEqual(doc["type"], "obs_st")
            total = doc["observations"][-1]["local_day_rain_accumulation"]
            self.assertEqual(total, 5.2)
        # live half: evt_precip datagram decodes with a timestamp for the stream
        _, payload = ts.handle_datagram(EVT_PRECIP_DATAGRAM)[0]
        self.assertEqual(payload["type"], "evt_precip")
        self.assertIsNotNone(payload["timestamp"])

    def test_forecast_json_fields_are_jq_addressable(self):
        fake = FakeTransport(STATIONS_ONLY)
        with patch_token(), patch.object(ts.TempestClient, "_get", fake):
            _, out = run_main(["forecast", "--json"])
        doc = json.loads(out)
        # documented nesting: .forecast.forecast.daily / .forecast.units.units_temp
        self.assertEqual(doc["forecast"]["units"]["units_temp"], "c")
        self.assertEqual(doc["forecast"]["forecast"]["hourly"][0]["local_hour"], 10)
        self.assertIsInstance(doc["forecast"]["forecast"]["daily"][0]["air_temp_high"], (int, float))


if __name__ == "__main__":
    unittest.main()
