"""Comprehensive tests for the Raleigh civic-data CLI."""
# ruff: noqa: E402

from __future__ import annotations

import csv
import importlib.machinery
import io
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from contextlib import redirect_stderr, redirect_stdout
from datetime import date
from email.message import Message
from unittest.mock import MagicMock, patch

# Ensure raleighlib is importable when the test file is loaded directly.
_SCRIPT_DIR = pathlib.Path(__file__).parents[1] / "scripts"
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import raleighlib.core as core
import raleighlib.hub as hub
import raleighlib.arcgis as arcgis
import raleighlib.imagery as imagery
import raleighlib.geocode as geocode
import raleighlib.transit as transit
from raleighlib import gtfs_realtime_pb2
import raleighlib.development as development
import raleighlib.civic as civic
import raleighlib.meetings as meetings
from raleighlib import cli as cli_lib

CLI_SCRIPT = _SCRIPT_DIR / "raleigh"
cli = importlib.machinery.SourceFileLoader("raleigh_cli", str(CLI_SCRIPT)).load_module()


class CoreTests(unittest.TestCase):
    def test_allowed_hosts_are_case_insensitive(self):
        self.assertTrue(core.is_allowed_host("https://data.raleighnc.gov/foo"))
        self.assertTrue(core.is_allowed_host("https://DATA.RALEIGHNC.GOV/foo"))
        self.assertFalse(core.is_allowed_host("https://evil.example.com/foo"))

    def test_json_request_rejects_unlisted_hosts(self):
        with self.assertRaises(core.SecurityError):
            core.json_request("https://evil.example.com/data.json")

    def test_raw_request_rejects_unlisted_hosts(self):
        with self.assertRaises(core.SecurityError):
            core.raw_request("https://evil.example.com/data.bin")

    def test_cache_read_write_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.environ["RALEIGH_CACHE"] = tmp
            try:
                core.write_cache("test-key", {"hello": "world"})
                self.assertEqual(core.read_cache("test-key"), {"hello": "world"})
                self.assertIsNone(core.read_cache("missing"))
                # Fresh read within max_age returns value.
                self.assertEqual(
                    core.read_cache("test-key", max_age_seconds=60), {"hello": "world"}
                )
                # Stale read returns None.
                path = core.cache_path("test-key")
                old_mtime = path.stat().st_mtime - 7200
                os.utime(path, (old_mtime, old_mtime))
                self.assertIsNone(core.read_cache("test-key", max_age_seconds=60))
            finally:
                os.environ.pop("RALEIGH_CACHE", None)

    def test_clear_cache_removes_entries(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.environ["RALEIGH_CACHE"] = tmp
            try:
                core.write_cache("a", 1)
                core.write_cache("b", 2)
                core.clear_cache()
                self.assertIsNone(core.read_cache("a"))
                self.assertIsNone(core.read_cache("b"))
            finally:
                os.environ.pop("RALEIGH_CACHE", None)


class HubTests(unittest.TestCase):
    def setUp(self):
        self.sample_records = [
            {
                "id": "item-1",
                "properties": {
                    "type": "FeatureServer",

                    "title": "Raleigh Dog Parks",
                    "description": "Dog park locations with amenities",
                    "tags": ["parks", "dogs"],
                    "categories": ["Parks & Recreation"],
                    "owner": "CityOfRaleigh",
                    "access": "public",
                    "license": "Public Domain",
                    "url": "https://services.arcgis.com/v400IkDOw1ad7Yad/arcgis/rest/services/DogParkLocations_Existing_PUBLIC/FeatureServer",
                    "extent": {"coordinates": [[-78.9, 35.7], [-78.4, 36.0]]},
                    "created": 1609459200000,
                    "modified": 1609459200000,
                },
            },
            {
                "id": "item-2",
                "properties": {
                    "type": "MapServer",
                    "title": "Food Inspections",
                    "description": "Restaurant inspection results",
                    "tags": ["health"],
                    "categories": ["Food & Health"],
                    "owner": "WakeCounty",
                    "access": "public",
                    "license": None,
                    "url": "https://maps.wake.gov/arcgis/rest/services/Inspections/RestaurantInspectionsOpenData/MapServer/1",
                    "extent": {"coordinates": [[-78.9, 35.7], [-78.4, 36.0]]},
                    "created": 1609459200000,
                    "modified": 1609459200000,
                },
            },
            {
                "id": "item-3",
                "properties": {
                    "type": "ImageServer",
                    "title": "Evening Temperature",
                    "description": "Evening temperature imagery",
                    "tags": ["environment"],
                    "categories": ["Environment"],
                    "owner": "CityOfRaleigh",
                    "access": "public",
                    "license": None,
                    "url": "https://services.arcgis.com/v400IkDOw1ad7Yad/arcgis/rest/services/Evening_Temperature/ImageServer",
                    "extent": {"coordinates": [[-78.9, 35.7], [-78.4, 36.0]]},
                    "created": 1609459200000,
                    "modified": 1609459200000,
                },
            },
        ]

    def test_normalize_record_preserved_required_fields(self):
        norm = hub.normalize_record(self.sample_records[0])
        self.assertEqual(norm["id"], "item-1")
        self.assertEqual(norm["title"], "Raleigh Dog Parks")
        self.assertEqual(norm["type"], "FeatureServer")
        self.assertEqual(norm["url"], self.sample_records[0]["properties"]["url"])
        self.assertEqual(norm["category"], "Parks & Recreation")
        self.assertIsNone(norm["has_geometry"])

    def test_normalize_record_image_server_has_no_layer_suffix(self):
        norm = hub.normalize_record(self.sample_records[2])
        self.assertEqual(norm["type"], "ImageServer")
        self.assertNotIn("/0", norm["url"])

    def test_search_matches_description_and_tags(self):
        catalog = [hub.normalize_record(r) for r in self.sample_records]
        results = hub.search_catalog("restaurant", catalog=catalog, limit=10)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Food Inspections")

    def test_search_is_case_insensitive(self):
        catalog = [hub.normalize_record(r) for r in self.sample_records]
        results = hub.search_catalog("DOG", catalog=catalog, limit=10)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Raleigh Dog Parks")

    def test_resolve_by_id(self):
        catalog = [hub.normalize_record(r) for r in self.sample_records]
        item = hub.resolve_item("item-2", catalog=catalog)
        self.assertEqual(item["title"], "Food Inspections")

    def test_resolve_by_title_prefers_exact(self):
        catalog = [hub.normalize_record(r) for r in self.sample_records]
        item = hub.resolve_item("Raleigh Dog Parks", catalog=catalog)
        self.assertEqual(item["id"], "item-1")

    def test_resolve_missing_raises(self):
        catalog = [hub.normalize_record(r) for r in self.sample_records]
        with self.assertRaises(hub.CatalogError):
            hub.resolve_item("missing", catalog=catalog)

    def test_resolve_duplicate_title_is_ambiguous(self):
        catalog = [hub.normalize_record(r) for r in self.sample_records]
        duplicate = dict(catalog[0])
        duplicate["id"] = "item-dup"
        catalog.append(duplicate)
        with self.assertRaises(hub.CatalogError):
            hub.resolve_item("Raleigh Dog Parks", catalog=catalog)

    @patch("raleighlib.hub.fetch_collection")
    def test_fetch_all_records_paginates(self, mock_fetch):
        page1 = {
            "features": [self.sample_records[0]],
            "numberReturned": 1,
            "numberMatched": 3,
        }
        page2 = {
            "features": [self.sample_records[1]],
            "numberReturned": 1,
            "numberMatched": 3,
        }
        page3 = {
            "features": [self.sample_records[2]],
            "numberReturned": 1,
            "numberMatched": 3,
        }

        def side_effect(collection, start_index=1, num=100):
            if start_index == 1:
                return page1
            if start_index == 2:
                return page2
            if start_index == 3:
                return page3
            return {"features": [], "numberReturned": 0, "numberMatched": 3}

        mock_fetch.side_effect = side_effect
        records = hub.fetch_all_records("dataset", max_records=10)
        self.assertEqual(len(records), 3)
        mock_fetch.assert_called()

    @patch("raleighlib.hub.fetch_all_records")
    @patch("raleighlib.core.read_cache")
    @patch("raleighlib.core.write_cache")
    def test_catalog_from_cache_or_live_uses_cache_when_fresh(
        self, mock_write, mock_read, mock_fetch
    ):
        cached = [hub.normalize_record(r) for r in self.sample_records]
        mock_read.return_value = cached
        result = hub.catalog_from_cache_or_live(max_age_seconds=3600)
        self.assertEqual(len(result), 3)
        mock_fetch.assert_not_called()
        mock_write.assert_not_called()


class ArcGISTests(unittest.TestCase):
    def test_query_layer_builds_url(self):
        url = "https://services.arcgis.com/v400IkDOw1ad7Yad/arcgis/rest/services/DogParkLocations_Existing_PUBLIC/FeatureServer/0"
        with patch("raleighlib.arcgis.core.json_request") as mock_req:
            mock_req.return_value = {"features": []}
            arcgis.query_layer(url, where="SCORE<70", out_fields="NAME", return_geometry=False)
            called_url = mock_req.call_args[0][0]
            self.assertIn("where=SCORE%3C70", called_url)
            self.assertIn("outFields=NAME", called_url)
            self.assertIn("returnGeometry=false", called_url)

    def test_query_layer_raises_arcgis_error(self):
        url = "https://services.arcgis.com/example/arcgis/rest/services/Test/FeatureServer/0"
        response = {"error": {"code": 400, "message": "Invalid query", "details": ["Bad WHERE clause"]}}
        with patch("raleighlib.arcgis.core.json_request", return_value=response):
            with self.assertRaisesRegex(ValueError, "Invalid query.*Bad WHERE clause"):
                arcgis.query_layer(url, where="INVALID")

    def test_query_all_pages_collects_multiple_pages(self):
        url = "https://services.arcgis.com/v400IkDOw1ad7Yad/arcgis/rest/services/DogParkLocations_Existing_PUBLIC/FeatureServer/0"

        def mock_response(query_url):
            self.assertIn(url, query_url)
            offset = 0
            if "resultOffset=100" in query_url:
                offset = 100
            elif "resultOffset=200" in query_url:
                offset = 200
            features = [
                {"attributes": {"OBJECTID": i}, "geometry": {"x": -78.0, "y": 35.8}}
                for i in range(offset, min(offset + 100, 250))
            ]
            return {"features": features, "exceededTransferLimit": offset + 100 < 250}

        with patch("raleighlib.arcgis.core.json_request", side_effect=mock_response):
            records = arcgis.query_all_pages(url, max_records=250, page_size=100)
        self.assertEqual(len(records), 250)

    def test_geometry_from_record_extracts_point(self):
        record = {"geometry": {"x": -78.0, "y": 35.8}}
        geom = arcgis.geometry_from_record(record)
        self.assertEqual(geom, {"type": "Point", "coordinates": [-78.0, 35.8]})

    def test_geometry_from_record_missing_returns_none(self):
        self.assertIsNone(arcgis.geometry_from_record({"attributes": {}}))

    def test_geometry_from_record_multipoint(self):
        record = {"geometry": {"points": [[-78.0, 35.8], [-78.1, 35.9]]}}
        geom = arcgis.geometry_from_record(record)
        self.assertEqual(geom["type"], "MultiPoint")
        self.assertEqual(geom["coordinates"], [[-78.0, 35.8], [-78.1, 35.9]])

    def test_geometry_from_record_linestring(self):
        record = {"geometry": {"paths": [[[-78.0, 35.8], [-78.1, 35.9]]]}}
        geom = arcgis.geometry_from_record(record)
        self.assertEqual(geom["type"], "LineString")
        self.assertEqual(geom["coordinates"], [[-78.0, 35.8], [-78.1, 35.9]])

    def test_geometry_from_record_multilinestring(self):
        record = {"geometry": {"paths": [[[-78.0, 35.8], [-78.1, 35.9]], [[-78.2, 36.0], [-78.3, 36.1]]]}}
        geom = arcgis.geometry_from_record(record)
        self.assertEqual(geom["type"], "MultiLineString")
        self.assertEqual(len(geom["coordinates"]), 2)

    def test_geometry_from_record_polygon(self):
        record = {"geometry": {"rings": [[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]]}}
        geom = arcgis.geometry_from_record(record)
        self.assertEqual(geom["type"], "Polygon")
        self.assertEqual(len(geom["coordinates"]), 1)

    def test_geometry_from_record_polygon_preserves_z_coordinates(self):
        ring = [[0, 0, 5], [0, 1, 6], [1, 1, 7], [1, 0, 8], [0, 0, 5]]
        geom = arcgis.geometry_from_record({"geometry": {"rings": [ring]}})
        self.assertEqual(geom["type"], "Polygon")
        self.assertEqual({point[2] for point in geom["coordinates"][0]}, {5, 6, 7, 8})

    def test_geometry_from_record_polygon_with_hole(self):
        outer = [[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]]
        inner = [[2, 2], [8, 2], [8, 8], [2, 8], [2, 2]]
        record = {"geometry": {"rings": [outer, inner]}}
        geom = arcgis.geometry_from_record(record)
        self.assertEqual(geom["type"], "Polygon")
        self.assertEqual(len(geom["coordinates"]), 2)

    def test_geometry_from_record_multipolygon(self):
        outer1 = [[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]
        outer2 = [[10, 10], [10, 11], [11, 11], [11, 10], [10, 10]]
        record = {"geometry": {"rings": [outer1, outer2]}}
        geom = arcgis.geometry_from_record(record)
        self.assertEqual(geom["type"], "MultiPolygon")
        self.assertEqual(len(geom["coordinates"]), 2)

    def test_csv_from_records_handles_attributes(self):
        records = [
            {"attributes": {"NAME": "A", "SCORE": 90}},
            {"attributes": {"NAME": "B", "SCORE": 80}},
        ]
        csv_text = arcgis.csv_from_records(records)
        self.assertIn("NAME,SCORE", csv_text)
        self.assertIn("A,90", csv_text)

    def test_csv_from_records_unions_keys(self):
        records = [
            {"attributes": {"NAME": "A"}},
            {"attributes": {"NAME": "B", "SCORE": 80}},
        ]
        csv_text = arcgis.csv_from_records(records)
        self.assertIn("NAME,SCORE", csv_text)
        self.assertIn("A,", csv_text)
        self.assertIn("B,80", csv_text)

    def test_csv_from_records_prevents_formula_injection(self):
        records = [
            {"attributes": {"NAME": "=cmd|' /C calc'!A0", "SCORE": 90}},
            {"attributes": {"NAME": "+123456", "SCORE": "@evil"}},
        ]
        csv_text = arcgis.csv_from_records(records)
        self.assertIn("'=cmd|' /C calc'!A0", csv_text)
        self.assertIn("'+123456", csv_text)
        self.assertIn("'@evil", csv_text)

    def test_geojson_from_records(self):
        records = [
            {
                "attributes": {"NAME": "A"},
                "geometry": {"x": -78.0, "y": 35.8},
            }
        ]
        gj = arcgis.geojson_from_records(records)
        self.assertEqual(gj["type"], "FeatureCollection")
        self.assertEqual(len(gj["features"]), 1)
        self.assertEqual(gj["features"][0]["geometry"]["type"], "Point")


class ImageryTests(unittest.TestCase):
    def test_list_services_recurses_folders(self):
        root = {
            "folders": ["Ortho"],
            "services": [{"name": "Base/Image", "type": "ImageServer"}],
        }
        folder = {"services": [{"name": "Ortho/2025", "type": "ImageServer"}]}

        def mock_response(url):
            if "Ortho" in url:
                return folder
            return root

        with patch("raleighlib.imagery.core.json_request", side_effect=mock_response):
            services = imagery.list_services()
        names = {s["name"] for s in services}
        self.assertIn("Base/Image", names)
        self.assertIn("Ortho/2025", names)

    def test_supports_capability(self):
        info = {"capabilities": "Catalog,Image,Metadata"}
        self.assertTrue(imagery.supports_capability(info, "Image"))
        self.assertFalse(imagery.supports_capability(info, "Edit"))

    def test_export_image_url_construction(self):
        with patch("raleighlib.imagery.core.raw_request") as mock_req:
            mock_req.return_value = b"\xff\xd8\xff"
            result = imagery.export_image(
                "https://maps.raleighnc.gov/images/rest/services/Orthos2025/ImageServer",
                bbox=(-78.7, 35.7, -78.6, 35.8),
                size=(400, 400),
            )
            called_url = mock_req.call_args[0][0]
            self.assertIn("bbox=-78.7%2C35.7%2C-78.6%2C35.8", called_url)
            self.assertIn("size=400%2C400", called_url)
            self.assertIn("format=jpgpng", called_url)
            self.assertEqual(result, b"\xff\xd8\xff")

    def test_identify_requires_image_capability(self):
        with patch("raleighlib.imagery.service_info") as mock_info:
            mock_info.return_value = {"capabilities": "Metadata"}
            with self.assertRaises(imagery.CapabilityError):
                imagery.identify(
                    "https://maps.raleighnc.gov/images/rest/services/Orthos2025/ImageServer",
                    point=(-78.65, 35.75),
                )

    def test_export_image_rejects_oversized_request(self):
        with patch("raleighlib.imagery.service_info") as mock_info:
            mock_info.return_value = {"capabilities": "Image", "maxImageWidth": 1000, "maxImageHeight": 1000}
            with self.assertRaises(imagery.CapabilityError):
                imagery.export_image(
                    "https://maps.raleighnc.gov/images/rest/services/Orthos2025/ImageServer",
                    bbox=(-78.7, 35.7, -78.6, 35.8),
                    size=(2000, 2000),
                )


class GeocodeTests(unittest.TestCase):
    def test_find_address_candidates_parses_response(self):
        response = {
            "candidates": [
                {
                    "address": "222 W Hargett St, Raleigh, NC",
                    "location": {"x": -78.64, "y": 35.78},
                    "score": 100,
                    "attributes": {"Loc_name": "Raleigh_Address"},
                }
            ]
        }
        with patch("raleighlib.geocode.core.json_request", return_value=response):
            candidates = geocode.find_address_candidates("222 W Hargett St")
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]["score"], 100)

    def test_filter_candidates_by_score(self):
        candidates = [{"score": 95}, {"score": 70}, {"score": 60}]
        self.assertEqual(len(geocode.filter_candidates(candidates, min_score=80)), 1)
        self.assertEqual(len(geocode.filter_candidates(candidates, min_score=60)), 3)

    def test_reverse_geocode_url(self):
        with patch("raleighlib.geocode.core.json_request") as mock_req:
            mock_req.return_value = {"address": {"Address": "222 W Hargett St"}}
            geocode.reverse_geocode(35.78, -78.64)
            called_url = mock_req.call_args[0][0]
            self.assertIn("location=%7B%22x%22%3A", called_url)
            self.assertIn("spatialReference", called_url)
            self.assertIn("4326", called_url)
            self.assertIn("-78.64", called_url)
            self.assertIn("35.78", called_url)

    def test_reverse_geocode_raises_arcgis_error(self):
        response = {"error": {"message": "Unable to find address"}}
        with patch("raleighlib.geocode.core.json_request", return_value=response):
            with self.assertRaisesRegex(ValueError, "Unable to find address"):
                geocode.reverse_geocode(35.78, -78.64)

    def test_suggest_parses(self):
        response = {"suggestions": [{"text": "222 W Hargett St", "magicKey": "abc"}]}
        with patch("raleighlib.geocode.core.json_request", return_value=response):
            suggestions = geocode.suggest("222 W Har")
        self.assertEqual(suggestions[0]["text"], "222 W Hargett St")

    def test_geocode_addresses_uses_post_and_preserves_row_identity(self):
        response = {
            "locations": [
                {
                    "attributes": {"ResultID": 1, "Score": 98, "Match_addr": "222 W Hargett St"},
                    "location": {"x": -78.64, "y": 35.78},
                }
            ]
        }
        with patch("raleighlib.geocode.core.json_request", return_value=response) as mock_req:
            results = geocode.geocode_addresses([{"OBJECTID": 1, "SingleLine": "222 W Hargett St"}])
        self.assertEqual(mock_req.call_args.kwargs.get("method"), "POST")
        self.assertIn("application/x-www-form-urlencoded", str(mock_req.call_args.kwargs.get("headers", {})))
        form = urllib.parse.parse_qs(mock_req.call_args.kwargs["data"].decode("utf-8"))
        payload = json.loads(form["addresses"][0])
        self.assertEqual(payload["records"][0]["attributes"]["OBJECTID"], 1)
        self.assertEqual(results[0]["input_id"], 1)
        self.assertEqual(results[0]["score"], 98)
        self.assertEqual(results[0]["status"], "matched")

    def test_geocode_addresses_preserves_unmatched_rows(self):
        response = {
            "locations": [
                {
                    "attributes": {"ResultID": 1, "Score": 98, "Match_addr": "222 W Hargett St"},
                    "location": {"x": -78.64, "y": 35.78},
                }
            ]
        }
        with patch("raleighlib.geocode.core.json_request", return_value=response):
            results = geocode.geocode_addresses([
                {"OBJECTID": 1, "SingleLine": "222 W Hargett St"},
                {"OBJECTID": 2, "SingleLine": "asdfghjkl"},
            ])
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["status"], "matched")
        self.assertEqual(results[1]["status"], "unmatched")
        self.assertIsNone(results[1]["score"])

    def test_geocode_addresses_caps_batch_size(self):
        with self.assertRaises(ValueError):
            geocode.geocode_addresses([{"OBJECTID": i, "SingleLine": "x"} for i in range(geocode.MAX_BATCH_SIZE + 1)])

    def test_geocode_with_magic_key(self):
        response = {
            "candidates": [
                {"address": "222 W Hargett St", "location": {"x": -78.64, "y": 35.78}, "score": 100}
            ]
        }
        with patch("raleighlib.geocode.core.json_request", return_value=response) as mock_req:
            candidates = geocode.geocode_with_magic_key("222 W Har", "abc123")
        self.assertEqual(len(candidates), 1)
        called_url = mock_req.call_args[0][0]
        self.assertIn("magicKey=abc123", called_url)


class TransitTests(unittest.TestCase):
    def _make_gtfs_zip(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr(
                "agency.txt",
                "agency_id,agency_name,agency_url,agency_timezone\n"
                "GOR,GoRaleigh,https://goraleigh.org,America/New_York\n",
            )
            zf.writestr(
                "routes.txt",
                "route_id,route_short_name,route_long_name,route_type\n"
                "R1,1,North Hills,3\nR2,2,GPU,3\n",
            )
            zf.writestr(
                "stops.txt",
                "stop_id,stop_name,stop_lat,stop_lon\n"
                "S1,Main St & Hargett St,35.78,-78.64\nS2,Capital Blvd,35.79,-78.63\n",
            )
            zf.writestr(
                "trips.txt",
                "route_id,service_id,trip_id,direction_id\n"
                "R1,WEEK,T1,0\nR1,WEEK,T2,1\n",
            )
            zf.writestr(
                "stop_times.txt",
                "trip_id,stop_id,stop_sequence,arrival_time,departure_time\n"
                "T1,S1,1,08:00:00,08:00:00\nT1,S2,2,08:15:00,08:15:00\n"
                "T2,S2,1,09:00:00,09:00:00\n",
            )
            zf.writestr(
                "calendar.txt",
                "service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date\n"
                "WEEK,1,1,1,1,1,0,0,20260101,20261231\n",
            )
        return buf.getvalue()

    def test_parse_gtfs_zip_reads_routes_and_stops(self):
        data = self._make_gtfs_zip()
        feed = transit.parse_gtfs_zip(data)
        self.assertEqual(len(feed["routes"]), 2)
        self.assertEqual(feed["routes"][0]["route_short_name"], "1")
        self.assertEqual(len(feed["stops"]), 2)
        with self.assertRaisesRegex(ValueError, "malformed"):
            transit.parse_gtfs_zip(b"not-a-zip")

    def test_get_routes(self):
        data = self._make_gtfs_zip()
        feed = transit.parse_gtfs_zip(data)
        routes = transit.get_routes(feed)
        self.assertEqual([r["route_id"] for r in routes], ["R1", "R2"])

    def test_get_schedule_for_route(self):
        data = self._make_gtfs_zip()
        feed = transit.parse_gtfs_zip(data)
        with patch("raleighlib.transit._today_date", return_value="20260723"):
            schedule = transit.get_schedule_for_route("R1", feed=feed)
        self.assertEqual(len(schedule), 3)
        self.assertEqual(schedule[0]["trip_id"], "T1")

    def test_get_arrivals_for_stop(self):
        data = self._make_gtfs_zip()
        feed = transit.parse_gtfs_zip(data)
        arrivals = transit.get_arrivals_for_stop("S2", feed=feed)
        self.assertEqual(len(arrivals), 2)

    def test_enrich_realtime_with_static(self):
        data = self._make_gtfs_zip()
        feed = transit.parse_gtfs_zip(data)
        entities = [
            {"vehicle": {"trip": {"trip_id": "T1"}, "vehicle": {"id": "V1"}}},
            {"trip_update": {"trip": {"trip_id": "T2"}, "stop_time_update": []}},
        ]
        enriched = transit.enrich_realtime_with_static(entities, feed)
        self.assertEqual(enriched[0]["route_id"], "R1")
        self.assertEqual(enriched[1]["route_id"], "R1")

    @patch("raleighlib.transit.core.raw_request")
    def test_fetch_realtime_decodes_protobuf(self, mock_raw):
        data = (pathlib.Path(__file__).parent / "fixtures" / "gtfs-realtime.bin").read_bytes()
        mock_raw.return_value = data
        with patch("raleighlib.transit._load_feed_with_cache", return_value={}):
            alerts = transit.get_alerts()
        self.assertEqual(len(alerts["entities"]), 1)
        self.assertEqual(alerts["entities"][0]["id"], "alert-1")
        self.assertIn("feed_timestamp", alerts)

    def test_parse_gtfs_zip_fixture(self):
        data = (pathlib.Path(__file__).parent / "fixtures" / "gtfs.zip").read_bytes()
        feed = transit.parse_gtfs_zip(data)
        self.assertEqual(len(feed["routes"]), 1)
        self.assertEqual(feed["routes"][0]["route_short_name"], "1")

    def test_fetch_realtime_empty_feed(self):
        data = (pathlib.Path(__file__).parent / "fixtures" / "gtfs-realtime-empty.bin").read_bytes()
        with patch("raleighlib.transit.core.raw_request", return_value=data), patch(
            "raleighlib.transit._load_feed_with_cache", return_value={}
        ):
            alerts = transit.get_alerts()
        self.assertEqual(alerts["entities"], [])
        self.assertIn("feed_timestamp", alerts)
        self.assertIn("staleness_seconds", alerts)

    def test_fetch_realtime_malformed_feed(self):
        data = (pathlib.Path(__file__).parent / "fixtures" / "gtfs-realtime-malformed.bin").read_bytes()
        with patch("raleighlib.transit.core.raw_request", return_value=data):
            with self.assertRaisesRegex(ValueError, "malformed"):
                transit.get_alerts()

    def test_fetch_realtime_stale_feed(self):
        data = (pathlib.Path(__file__).parent / "fixtures" / "gtfs-realtime-stale-alert.bin").read_bytes()
        with patch("raleighlib.transit.core.raw_request", return_value=data), patch(
            "raleighlib.transit._load_feed_with_cache", return_value={}
        ):
            alerts = transit.get_alerts()
        self.assertGreater(alerts["staleness_seconds"], 0)


class DevelopmentTests(unittest.TestCase):
    def test_adapter_can_be_disabled_independently(self):
        with patch.dict(os.environ, {"RALEIGH_DISABLE_DEVELOPMENT": "1"}):
            with self.assertRaises(development.UnsupportedEndpointError):
                development.fetch_criteria()

    @patch("raleighlib.development.core.json_request")
    def test_public_search_uses_guest_url(self, mock_req):
        criteria = {"Result": {"PermitCriteria": {}, "PermitSortList": []}}
        search_result = {"Result": {"EntityResults": [{"RecordNumber": "BP-2024-001"}], "TotalFound": 1}}
        mock_req.side_effect = [criteria, search_result]
        result = development.public_search("permit", query="2024-001", limit=7)
        called_url = mock_req.call_args[0][0]
        self.assertIn("raleighnc-energovpub.tylerhost.net", called_url)
        self.assertIn("/api/energov/search", called_url)
        payload = json.loads(mock_req.call_args.kwargs["data"])
        self.assertEqual(payload["Keyword"], "2024-001")
        self.assertTrue(payload["ExactMatch"])
        self.assertEqual(payload["SearchModule"], 1)
        self.assertEqual(payload["FilterModule"], 2)
        self.assertEqual(payload["PageNumber"], 1)
        self.assertEqual(payload["PageSize"], 7)
        self.assertTrue(payload["SortAscending"])
        self.assertEqual(payload["PermitCriteria"], {})
        self.assertEqual(result["results"][0]["RecordNumber"], "BP-2024-001")
        self.assertEqual(result["total"], 1)

    def test_public_search_handles_empty_results(self):
        criteria = {"Result": {"PermitCriteria": {}}}
        response = {"Result": {"EntityResults": [], "TotalFound": 0}}
        with patch("raleighlib.development.core.json_request", side_effect=[criteria, response]):
            result = development.public_search("permit")
        self.assertEqual(result, {"results": [], "total": 0})

    def test_public_search_rejects_schema_change(self):
        with patch("raleighlib.development.core.json_request", side_effect=[{"Result": {}}, {}]):
            with self.assertRaisesRegex(ValueError, "does not advertise"):
                development.public_search("permit")

    def test_public_search_surfaces_rate_limit_timeout_and_access_denied(self):
        criteria = {"Result": {"PermitCriteria": {}}}
        failures = [
            urllib.error.HTTPError(development.SEARCH_URL, 429, "Too Many Requests", Message(), None),
            TimeoutError("timed out"),
            urllib.error.HTTPError(development.SEARCH_URL, 403, "Forbidden", Message(), None),
        ]
        for failure in failures:
            with self.subTest(failure=type(failure).__name__, detail=str(failure)):
                with patch("raleighlib.development.fetch_criteria", return_value=criteria), patch(
                    "raleighlib.development.core.json_request", side_effect=failure
                ):
                    with self.assertRaises(type(failure)):
                        development.public_search("permit")

    def test_permit_detail_resolves_uuid(self):
        test_uuid = "d4701697-8a5b-49ed-bb16-5334fad23d08"
        with patch("raleighlib.development.core.json_request") as mock_req:
            mock_req.return_value = {"Success": True, "Result": {"PermitId": test_uuid}}
            result = development.permit_detail(test_uuid)
        self.assertEqual(result["PermitId"], test_uuid)
        called_url = mock_req.call_args[0][0]
        self.assertIn(f"/api/energov/permits/{test_uuid}", called_url)

    def test_permit_detail_resolves_record_number(self):
        test_uuid = "d4701697-8a5b-49ed-bb16-5334fad23d08"
        criteria = {"Result": {"PermitCriteria": {}, "PermitSortList": []}}
        search_result = {"Result": {"EntityResults": [{"CaseNumber": "BP-2024-001", "CaseId": test_uuid}], "TotalFound": 1}}
        detail_result = {"Success": True, "Result": {"PermitId": test_uuid}}
        with patch("raleighlib.development.core.json_request", side_effect=[criteria, search_result, detail_result]) as mock_req:
            result = development.permit_detail("bp-2024-001")
        self.assertEqual(result["PermitId"], test_uuid)
        self.assertEqual(mock_req.call_count, 3)

    def test_permit_detail_rejects_ambiguous_record_number(self):
        test_uuid1 = "d4701697-8a5b-49ed-bb16-5334fad23d08"
        test_uuid2 = "11111111-1111-1111-1111-111111111111"
        criteria = {"Result": {"PermitCriteria": {}, "PermitSortList": []}}
        search_result = {"Result": {"EntityResults": [
            {"RecordNumber": "BP-2024-001", "Id": test_uuid1},
            {"RecordNumber": "BP-2024-001", "Id": test_uuid2},
        ], "TotalFound": 2}}
        with patch("raleighlib.development.core.json_request", side_effect=[criteria, search_result]):
            with self.assertRaises(ValueError):
                development.permit_detail("BP-2024-001")

    def test_inspections_for_record_posts_contract(self):
        test_uuid = "d4701697-8a5b-49ed-bb16-5334fad23d08"
        criteria = {"Result": {"PermitCriteria": {}, "PermitSortList": []}}
        search_result = {"Result": {"EntityResults": [{"RecordNumber": "BP-2024-001", "Id": test_uuid}], "TotalFound": 1}}
        inspection_result = {"Result": [{
            "InspectionId": "i1",
            "PrimaryInspector": "Public Inspector",
            "PrimaryInspectorEmail": "not-returned@example.invalid",
        }]}
        with patch("raleighlib.development.core.json_request", side_effect=[criteria, search_result, inspection_result]) as mock_req:
            results = development.inspections_for_record("BP-2024-001", limit=5)
        self.assertEqual(len(results), 1)
        self.assertNotIn("PrimaryInspectorEmail", results[0])
        called_url = mock_req.call_args_list[2][0][0]
        payload = json.loads(mock_req.call_args_list[2].kwargs["data"])
        self.assertIn("/api/energov/entity/inspections/search/search", called_url)
        self.assertEqual(payload["EntityId"], test_uuid)
        self.assertEqual(payload["PageSize"], 5)

    def test_inspections_dict_wrapper_is_field_allowlisted(self):
        test_uuid = "d4701697-8a5b-49ed-bb16-5334fad23d08"
        inspection_result = {"Result": {"Results": [{
            "InspectionId": "i1",
            "PrimaryInspector": "Public Inspector",
            "PrimaryInspectorEmail": "private@example.invalid",
        }]}}
        with patch("raleighlib.development._resolve_uuid", return_value=test_uuid), patch(
            "raleighlib.development.core.json_request", return_value=inspection_result
        ):
            results = development.inspections_for_record(test_uuid)
        self.assertEqual(results[0]["InspectionId"], "i1")
        self.assertNotIn("PrimaryInspectorEmail", results[0])


class CivicTests(unittest.TestCase):
    def test_allowed_resource_types_do_not_include_admin(self):
        self.assertIn("node--news", civic.ALLOWED_RESOURCE_TYPES)
        self.assertNotIn("user--user", civic.ALLOWED_RESOURCE_TYPES)
        self.assertNotIn("webform_submission", civic.ALLOWED_RESOURCE_TYPES)

    def test_fetch_jsonapi_uses_node_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.environ["RALEIGH_CACHE"] = tmp
            try:
                with patch("raleighlib.civic.core.json_request") as mock_req:
                    mock_req.return_value = {"data": []}
                    civic.fetch_jsonapi("node--news", limit=5)
                    called_url = mock_req.call_args[0][0]
                    self.assertIn("raleighnc.gov/jsonapi/node/news", called_url)
                    self.assertNotIn("/index/", called_url)
                    self.assertIn("filter%5Bstatus%5D=1", called_url)
                    self.assertNotIn("fulltext", called_url)
            finally:
                os.environ.pop("RALEIGH_CACHE", None)

    def test_fetch_jsonapi_discovers_paths_from_index(self):
        index = {"links": {"node--news": {"href": "https://raleighnc.gov/jsonapi/node/news"}}}
        with tempfile.TemporaryDirectory() as tmp:
            os.environ["RALEIGH_CACHE"] = tmp
            try:
                with patch("raleighlib.civic.core.json_request", side_effect=[index, {"data": []}]) as mock_req:
                    civic.fetch_jsonapi("node--news", limit=5)
                    called_url = mock_req.call_args_list[1][0][0]
                    self.assertIn("/jsonapi/node/news", called_url)
                    self.assertIn("filter%5Bstatus%5D=1", called_url)
            finally:
                os.environ.pop("RALEIGH_CACHE", None)

    def test_fetch_jsonapi_rejects_disallowed_resource(self):
        with patch("raleighlib.civic.core.json_request") as mock_req:
            mock_req.return_value = {"data": []}
            with self.assertRaises(civic.ResourceError):
                civic.fetch_jsonapi("user--user", limit=5)
            mock_req.assert_not_called()

    def test_fetch_jsonapi_paginates_until_limit(self):
        page1 = {
            "data": [
                {"type": "node--news", "id": "n1", "attributes": {"status": True, "title": "One"}},
            ],
            "links": {"next": {"href": "https://raleighnc.gov/jsonapi/node/news?page[offset]=1"}},
        }
        page2 = {
            "data": [
                {"type": "node--news", "id": "n2", "attributes": {"status": True, "title": "Two"}},
            ],
        }
        with patch("raleighlib.civic.core.json_request", side_effect=[page1, page2]) as mock_req:
            results = civic.fetch_jsonapi("node--news", limit=2)
        self.assertEqual(len(results), 2)
        self.assertEqual(mock_req.call_count, 2)
        self.assertEqual(results[1]["title"], "Two")

    def test_fetch_jsonapi_client_side_search(self):
        data = {
            "data": [
                {"type": "node--news", "id": "n1", "attributes": {"status": True, "title": "Apple News"}},
                {"type": "node--news", "id": "n2", "attributes": {"status": True, "title": "Banana News"}},
            ],
        }
        with patch("raleighlib.civic.core.json_request", return_value=data):
            results = civic.fetch_jsonapi("node--news", limit=5, search="apple")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Apple News")

    def test_fetch_jsonapi_client_side_date_filter(self):
        data = {
            "data": [
                {"type": "node--event", "id": "e1", "attributes": {"status": True, "title": "Old", "field_event_date": {"value": "2025-01-01"}}},
                {"type": "node--event", "id": "e2", "attributes": {"status": True, "title": "New", "field_event_date": {"value": "2026-07-01"}}},
            ],
        }
        with patch("raleighlib.civic.core.json_request", return_value=data):
            results = civic.fetch_events(limit=5, date_from="2026-01-01")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "New")

    def test_fetch_jsonapi_uses_path_alias_url(self):
        data = {
            "data": [
                {
                    "type": "node--news",
                    "id": "n1",
                    "attributes": {"status": True, "title": "One", "path": {"alias": "/news/one"}},
                }
            ],
        }
        with patch("raleighlib.civic.core.json_request", return_value=data):
            results = civic.fetch_jsonapi("node--news", limit=1)
        self.assertEqual(results[0]["url"], "https://raleighnc.gov/news/one")

    def test_fetch_jsonapi_extracts_link_href(self):
        data = {
            "data": [
                {
                    "type": "node--news",
                    "id": "n1",
                    "attributes": {"status": True, "title": "One"},
                    "links": {"canonical": {"href": "https://raleighnc.gov/news/one"}},
                }
            ],
        }
        with patch("raleighlib.civic.core.json_request", return_value=data):
            results = civic.fetch_jsonapi("node--news", limit=1)
        self.assertIsInstance(results[0]["url"], str)
        self.assertEqual(results[0]["url"], "https://raleighnc.gov/news/one")

    def test_fetch_jsonapi_skips_unpublished(self):
        data = {
            "data": [
                {"type": "node--news", "id": "n1", "attributes": {"title": "One", "status": False}},
                {"type": "node--news", "id": "n2", "attributes": {"title": "Two", "status": True}},
            ],
        }
        with patch("raleighlib.civic.core.json_request", return_value=data):
            results = civic.fetch_jsonapi("node--news", limit=5)
        self.assertEqual([item["id"] for item in results], ["n2"])

    def test_fetch_jsonapi_filters_relationship_identifier(self):
        data = {
            "data": [
                {
                    "type": "node--news",
                    "id": "n1",
                    "attributes": {"status": True, "title": "District Two"},
                    "relationships": {
                        "field_district": {"data": {"type": "taxonomy_term--district", "id": "d2"}}
                    },
                },
                {
                    "type": "node--news",
                    "id": "n2",
                    "attributes": {"status": True, "title": "District Three"},
                    "relationships": {
                        "field_district": {"data": {"type": "taxonomy_term--district", "id": "d3"}}
                    },
                },
            ]
        }
        with patch("raleighlib.civic.core.json_request", return_value=data):
            results = civic.fetch_jsonapi(
                "node--news", limit=5, relationship="field_district=d2"
            )
        self.assertEqual([item["id"] for item in results], ["n1"])

    def test_fetch_jsonapi_rejects_invalid_relationship_expression(self):
        with patch("raleighlib.civic.core.json_request", return_value={"data": []}):
            with self.assertRaisesRegex(ValueError, "FIELD=ID"):
                civic.fetch_jsonapi("node--news", relationship="field_district")

    def test_fetch_news_parses_data(self):
        data = {
            "data": [
                {
                    "type": "node--news",
                    "id": "news-1",
                    "attributes": {"status": True, "title": "Test News", "created": "2026-07-01T00:00:00+00:00"},
                }
            ],
        }
        with patch("raleighlib.civic.core.json_request", return_value=data):
            results = civic.fetch_news(limit=1)
        self.assertEqual(results[0]["title"], "Test News")

    @patch("raleighlib.civic.core.raw_request")
    def test_fetch_rss_parses_items(self, mock_raw):
        mock_raw.return_value = b"""<?xml version="1.0"?>
<rss version="2.0">
<channel>
  <item><title>News A</title><link>https://raleighnc.gov/a</link><pubDate>Mon, 01 Jul 2026 00:00:00 GMT</pubDate></item>
</channel>
</rss>
"""
        results = civic.fetch_rss(limit=5)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "News A")

    @patch("raleighlib.civic.core.raw_request")
    def test_fetch_rss_deduplicates_unchanged_items(self, mock_raw):
        mock_raw.return_value = b"""<rss><channel>
        <item><guid>same</guid><title>News A</title><link>https://raleighnc.gov/a</link></item>
        <item><guid>same</guid><title>News A updated rendering</title><link>https://raleighnc.gov/a</link></item>
        </channel></rss>"""
        results = civic.fetch_rss(limit=5)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "News A")

    def test_fetch_rss_new_only_persists_seen_guids(self):
        feed = b"""<rss><channel>
        <item><guid>same</guid><title>News A</title><link>https://raleighnc.gov/a</link></item>
        </channel></rss>"""
        state: list[str] = []

        def save(_key, values):
            state[:] = values

        with patch("raleighlib.civic.core.raw_request", return_value=feed), patch(
            "raleighlib.civic.core.read_cache", side_effect=lambda _key: list(state)
        ), patch("raleighlib.civic.core.write_cache", side_effect=save):
            first = civic.fetch_rss(limit=5, new_only=True)
            second = civic.fetch_rss(limit=5, new_only=True)
        self.assertEqual([item["title"] for item in first], ["News A"])
        self.assertEqual(second, [])


class MeetingsTests(unittest.TestCase):
    def test_list_upcoming_parses_html(self):
        html = (pathlib.Path(__file__).parent / "fixtures" / "escribe-listing.html").read_bytes()
        with patch("raleighlib.meetings.core.raw_request", return_value=html):
            meetings_list = meetings.list_upcoming()
        self.assertEqual(len(meetings_list), 1)
        self.assertEqual(meetings_list[0]["title"], "City Council Meeting - Third Tuesday")
        self.assertEqual(meetings_list[0]["date"], "Tuesday, July 23, 2026 @ 11:30 AM")


    def test_meeting_detail_parses_documents(self):
        html = (pathlib.Path(__file__).parent / "fixtures" / "escribe-agenda.html").read_bytes()
        with patch("raleighlib.meetings.core.raw_request", return_value=html), patch(
            "raleighlib.meetings._find_past_meeting_record", return_value=None
        ):
            detail = meetings.meeting_detail("550e8400-e29b-41d4-a716-446655440000")
        self.assertEqual(detail["title"], "Budget Meeting")
        self.assertEqual(detail["agenda"], "https://pub-raleighnc.escribemeetings.com/doc/101/agenda.pdf")
        self.assertEqual(detail["minutes"], "https://pub-raleighnc.escribemeetings.com/doc/101/minutes.pdf")
        self.assertEqual(detail["video"], "https://video.example.com/101")

    def test_meeting_detail_uses_page_method_document_links(self):
        record = {
            "Id": "550e8400-e29b-41d4-a716-446655440000",
            "MeetingType": "City Council",
            "FormattedStart": "Tuesday, October 14, 2025 @ 6:00 PM",
            "LocationName": "Council Chamber",
            "Cancelled": False,
            "MeetingLinks": [
                {"Type": "AgendaCover", "Format": ".pdf", "Title": "Agenda (PDF)", "Url": "/FileStream.ashx?DocumentId=1"},
                {"Type": "Agenda", "Format": ".pdf", "Title": "Agenda Package (PDF)", "Url": "/FileStream.ashx?DocumentId=2"},
                {"Type": "Minutes", "Format": ".pdf", "Title": "Minutes (PDF)", "Url": "/FileStream.ashx?DocumentId=3"},
            ],
        }
        with patch("raleighlib.meetings.core.raw_request", return_value=b"<h1>Fallback</h1><time datetime='2025-10-14'>October 14</time>"), patch(
            "raleighlib.meetings._find_past_meeting_record", return_value=record
        ):
            detail = meetings.meeting_detail(record["Id"])
        self.assertEqual(detail["title"], "City Council")
        self.assertTrue(detail["agenda"].endswith("DocumentId=1"))
        self.assertTrue(detail["agenda_package"].endswith("DocumentId=2"))
        self.assertTrue(detail["minutes"].endswith("DocumentId=3"))

    def test_meeting_detail_handles_cancellation_and_missing_documents(self):
        record = {
            "Id": "550e8400-e29b-41d4-a716-446655440000",
            "MeetingType": "Cancelled Hearing",
            "FormattedStart": "Tuesday, October 14, 2025 @ 6:00 PM",
            "LocationName": "Council Chamber",
            "Cancelled": True,
            "MeetingLinks": [],
        }
        with patch("raleighlib.meetings.core.raw_request", return_value=b"<h1>Fallback</h1><time datetime='2025-10-14'>October 14</time>"), patch(
            "raleighlib.meetings._find_past_meeting_record", return_value=record
        ):
            detail = meetings.meeting_detail(record["Id"])
        self.assertTrue(detail["cancelled"])
        self.assertIsNone(detail["agenda"])
        self.assertIsNone(detail["minutes"])
        self.assertIsNone(detail["agenda_package"])
        self.assertIsNone(detail["video"])

    def test_download_document_rejects_non_allowlisted_host(self):
        with self.assertRaises(core.SecurityError):
            meetings.download_document("https://evil.example.com/doc.pdf", "/tmp/doc.pdf")

    def test_extract_meetings_raises_on_unparseable_page(self):
        html = (pathlib.Path(__file__).parent / "fixtures" / "escribe-empty.html").read_text()
        with self.assertRaises(meetings.CompatibilityError):
            meetings._extract_meeting_rows(html)

    def test_list_meetings_uses_year_archive(self):
        archived = [{
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "title": "Council Meeting",
            "date": "Tuesday, January 14, 2025 @ 10:00 AM",
            "body": "City Council",
        }]
        with patch("raleighlib.meetings._fetch_past_meetings", return_value=archived) as mock_fetch:
            rows = meetings.list_meetings(body="Council", year=2025, limit=1)
        self.assertEqual(rows, archived)
        mock_fetch.assert_called_once_with(2025, body="Council", limit=1)

    def test_fetch_past_meetings_uses_verified_page_method(self):
        listing = '<div class="MeetingTypeContainer" MeetingType="City Council &amp; Budget"></div>'
        response = {"d": {"TotalCount": 1, "Meetings": [{
            "Id": "550e8400-e29b-41d4-a716-446655440000",
            "MeetingType": "City Council & Budget",
            "FormattedStart": "Tuesday, January 14, 2025 @ 10:00 AM",
            "LocationName": "Council Chamber",
            "Cancelled": False,
        }]}}
        with patch("raleighlib.meetings.core.raw_request", return_value=listing.encode()), patch(
            "raleighlib.meetings.core.json_request", return_value=response
        ) as mock_request:
            rows = meetings._fetch_past_meetings(2025)
        self.assertEqual(rows[0]["location"], "Council Chamber")
        called_url = mock_request.call_args.args[0]
        payload = json.loads(mock_request.call_args.kwargs["data"])
        self.assertIn("/MeetingsCalendarView.aspx/PastMeetings", called_url)
        self.assertIn("Year=2025", called_url)
        self.assertEqual(payload, {"type": "City Council & Budget", "pageNumber": 1})

    def test_fetch_past_meetings_rejects_missing_total_count(self):
        listing = '<div MeetingType="City Council"></div>'
        response = {"d": {"Meetings": [{"Id": "1"}]}}
        with patch("raleighlib.meetings.core.raw_request", return_value=listing.encode()), patch(
            "raleighlib.meetings.core.json_request", return_value=response
        ):
            with self.assertRaises(meetings.CompatibilityError):
                meetings._fetch_past_meetings(2025)

    def test_list_upcoming_excludes_past_section(self):
        html_text = """
        <a aria-label="Share Future Meeting Tuesday, August 18, 2026 @ 10:00 AM"
           href="/Meeting.aspx?Id=550e8400-e29b-41d4-a716-446655440000&lang=English"></a>
        <h2>Past Meetings</h2>
        <a aria-label="Share Past Meeting Tuesday, January 14, 2025 @ 10:00 AM"
           href="/Meeting.aspx?Id=650e8400-e29b-41d4-a716-446655440000&lang=English"></a>
        """
        with patch("raleighlib.meetings.core.raw_request", return_value=html_text.encode()):
            rows = meetings.list_upcoming(today=date(2026, 7, 23))
        self.assertEqual([row["title"] for row in rows], ["Future Meeting"])

    def test_search_meetings_filters_historical_rows(self):
        rows = [
            {"id": "1", "title": "Budget Work Session", "body": "City Council", "date": "2025"},
            {"id": "2", "title": "Planning Meeting", "body": "Planning Commission", "date": "2025"},
        ]
        with patch("raleighlib.meetings.list_meetings", return_value=rows) as mock_list:
            results = meetings.search_meetings("budget", body="Council", year=2025, limit=1)
        self.assertEqual([row["id"] for row in results], ["1"])
        mock_list.assert_called_once_with(body="Council", year=2025)


class CliTests(unittest.TestCase):
    def run_cli(self, arguments):
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            try:
                result = cli.main(arguments)
            except SystemExit as exc:
                return exc.code, stdout.getvalue(), stderr.getvalue()
        return result, stdout.getvalue(), stderr.getvalue()

    def test_catalog_subcommand_exists(self):
        with patch("raleighlib.cli.hub.catalog_from_cache_or_live") as mock_catalog:
            mock_catalog.return_value = [{"id": "x", "title": "Test", "type": "FeatureServer", "access": "public"}]
            code, out, err = self.run_cli(["catalog", "--json"])
        self.assertEqual(code, 0, err)
        self.assertIn("Test", out)

    def test_search_subcommand_exists(self):
        with patch("raleighlib.cli.hub.catalog_from_cache_or_live") as mock_catalog:
            mock_catalog.return_value = [{"id": "x", "title": "Dog Parks", "type": "FeatureServer", "access": "public"}]
            code, out, err = self.run_cli(["search", "dog", "--json"])
        self.assertEqual(code, 0, err)
        self.assertIn("Dog Parks", out)

    def test_imagery_catalog_subcommand(self):
        with patch("raleighlib.cli.imagery.list_services") as mock_list:
            mock_list.return_value = [{"name": "Orthos2025", "type": "ImageServer"}]
            code, out, err = self.run_cli(["imagery", "catalog", "--json"])
        self.assertEqual(code, 0, err)
        self.assertIn("Orthos2025", out)

    def test_imagery_export_rejects_invalid_size_concisely(self):
        code, out, err = self.run_cli([
            "imagery", "export", "Orthos2025",
            "--bbox=-78.7,35.7,-78.6,35.8", "--size", "400",
            "-o", "unused.jpg",
        ])
        self.assertNotEqual(code, 0)
        self.assertIn("size must be width,height", err)
        self.assertNotIn("Traceback", err)

    def test_geocode_subcommand(self):
        with patch("raleighlib.cli.geocode.find_address_candidates") as mock_geo:
            mock_geo.return_value = [{"address": "222 W Hargett St", "score": 100}]
            code, out, err = self.run_cli(["geocode", "222 W Hargett St", "--json"])
        self.assertEqual(code, 0, err)
        self.assertIn("222 W Hargett St", out)

    def test_transit_routes_subcommand(self):
        with patch("raleighlib.cli.transit.get_routes") as mock_routes:
            mock_routes.return_value = [{"route_id": "R1", "route_short_name": "1"}]
            code, out, err = self.run_cli(["transit", "routes", "--json"])
        self.assertEqual(code, 0, err)
        self.assertIn("R1", out)

    def test_transit_trip_updates_subcommand(self):
        with patch("raleighlib.cli.transit.get_trip_updates") as mock_trips:
            mock_trips.return_value = [{"id": "trip-1", "staleness_seconds": 2}]
            code, out, err = self.run_cli(["transit", "trip-updates", "--limit", "1", "--json"])
        self.assertEqual(code, 0, err)
        self.assertIn("trip-1", out)
        mock_trips.assert_called_once_with(route=None, limit=1)

    def test_development_inspections_limit(self):
        with patch("raleighlib.cli.development.inspections_for_record") as mock_inspections:
            mock_inspections.return_value = [{"InspectionId": "i1"}]
            code, out, err = self.run_cli([
                "development", "inspections", "--record", "record-1", "--limit", "2", "--json"
            ])
        self.assertEqual(code, 0, err)
        mock_inspections.assert_called_once_with("record-1", limit=2)

    def test_suggest_limit_alias(self):
        with patch("raleighlib.cli.geocode.suggest") as mock_suggest:
            mock_suggest.return_value = [{"text": "222 W Hargett", "magicKey": "k"}]
            code, out, err = self.run_cli(["suggest", "222 W Har", "--limit", "1", "--json"])
        self.assertEqual(code, 0, err)
        mock_suggest.assert_called_once_with("222 W Har", max_suggestions=1)

    def test_news_subcommand(self):
        with patch("raleighlib.cli.civic.fetch_news") as mock_news:
            mock_news.return_value = [{"title": "News Item", "url": "https://raleighnc.gov/news/1"}]
            code, out, err = self.run_cli(["news", "--json"])
        self.assertEqual(code, 0, err)
        self.assertIn("News Item", out)

    def test_meetings_upcoming_subcommand(self):
        with patch("raleighlib.cli.meetings.list_upcoming") as mock_upcoming:
            mock_upcoming.return_value = [{"id": "100", "title": "Council"}]
            code, out, err = self.run_cli(["meetings", "upcoming", "--json"])
        self.assertEqual(code, 0, err)
        self.assertIn("Council", out)

    def test_catalog_check_snapshot_samples(self):
        catalog = [{"id": "x", "title": "Test", "type": "FeatureServer", "url": "https://services.arcgis.com/x/FeatureServer/0"}]
        with patch("raleighlib.cli.hub.catalog_from_cache_or_live", return_value=catalog), \
             patch("raleighlib.cli.arcgis.service_metadata", return_value={"serviceDescription": "ok"}):
            code, out, err = self.run_cli(["catalog-check", "--snapshot", "--json"])
        self.assertEqual(code, 0, err)
        data = json.loads(out)
        self.assertEqual(data["checked"], 1)
        self.assertEqual(data["failures"], [])

    def test_catalog_check_filters_by_type(self):
        catalog = [
            {"id": "f", "title": "F", "type": "FeatureServer", "url": "https://services.arcgis.com/x/FeatureServer/0"},
            {"id": "i", "title": "I", "type": "ImageServer", "url": "https://services.arcgis.com/x/ImageServer"},
        ]
        with patch("raleighlib.cli.hub.catalog_from_cache_or_live", return_value=catalog), \
             patch("raleighlib.cli.imagery.service_info", return_value={"serviceDescription": "ok"}):
            code, out, err = self.run_cli(["catalog-check", "--snapshot", "--type", "ImageServer", "--json"])
        self.assertEqual(code, 0, err)
        data = json.loads(out)
        self.assertEqual(data["checked"], 1)
        self.assertEqual(data["failures"], [])

    def test_catalog_check_skips_non_service_records(self):
        catalog = [
            {"id": "doc", "title": "Document", "type": "Document Link", "url": "https://example.invalid/file.pdf"},
            {"id": "f", "title": "F", "type": "FeatureServer", "url": "https://services3.arcgis.com/x/FeatureServer/0"},
        ]
        with patch("raleighlib.cli.hub.catalog_from_cache_or_live", return_value=catalog), \
             patch("raleighlib.cli.arcgis.service_metadata", return_value={"serviceDescription": "ok"}) as mock_metadata:
            code, out, err = self.run_cli(["catalog-check", "--snapshot", "--full", "--json"])
        self.assertEqual(code, 0, err)
        data = json.loads(out)
        self.assertEqual(data["checked"], 1)
        self.assertEqual(data["failures"], [])
        mock_metadata.assert_called_once_with("https://services3.arcgis.com/x/FeatureServer/0")

    def test_catalog_check_failure_returns_non_zero(self):
        catalog = [{"id": "x", "title": "Test", "type": "FeatureServer", "url": "https://services.arcgis.com/x/FeatureServer/0"}]
        with patch("raleighlib.cli.hub.catalog_from_cache_or_live", return_value=catalog), \
             patch("raleighlib.cli.arcgis.service_metadata", return_value={"error": "timeout"}):
            code, out, err = self.run_cli(["catalog-check", "--snapshot", "--json"])
        self.assertEqual(code, 1)
        data = json.loads(out)
        self.assertEqual(data["checked"], 1)
        self.assertEqual(data["failures"][0]["id"], "x")


class CharacterizationTests(unittest.TestCase):
    def run_cli(self, arguments):
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            try:
                result = cli.main(arguments)
            except SystemExit as exc:
                return exc.code, stdout.getvalue(), stderr.getvalue()
        return result, stdout.getvalue(), stderr.getvalue()

    def test_query_json_returns_feature_collection(self):
        catalog = [
            {
                "id": "x",
                "title": "Test",
                "type": "FeatureServer",
                "access": "public",
                "url": "https://services.arcgis.com/x/FeatureServer/0",
                "tags": [],
                "categories": [],
                "category": "Other",
            }
        ]
        with patch("raleighlib.cli.hub.catalog_from_cache_or_live", return_value=catalog), \
             patch("raleighlib.cli.arcgis.resolve_queryable_layer", return_value="https://services.arcgis.com/x/FeatureServer/0"), \
             patch("raleighlib.cli.arcgis.layer_has_geometry", return_value=True), \
             patch("raleighlib.cli.arcgis.query_all_pages") as mock_query:
            mock_query.return_value = [{"attributes": {"NAME": "A"}, "geometry": {"x": 1.0, "y": 2.0}}]
            code, out, err = self.run_cli(["query", "Test", "--json"])
        self.assertEqual(code, 0, err)
        data = json.loads(out)
        self.assertEqual(data["type"], "FeatureCollection")
        self.assertEqual(len(data["features"]), 1)
        self.assertEqual(data["features"][0]["type"], "Feature")
        self.assertEqual(data["features"][0]["properties"]["NAME"], "A")
        self.assertEqual(data["features"][0]["geometry"]["type"], "Point")

    def test_info_json_returns_dataset_fields_sample(self):
        catalog = [
            {
                "id": "x",
                "title": "Test",
                "type": "FeatureServer",
                "access": "public",
                "url": "https://services.arcgis.com/x/FeatureServer/0",
                "tags": [],
                "categories": [],
                "category": "Other",
            }
        ]
        with patch("raleighlib.cli.hub.catalog_from_cache_or_live", return_value=catalog), \
             patch("raleighlib.cli.arcgis.resolve_queryable_layer", return_value="https://services.arcgis.com/x/FeatureServer/0"), \
             patch("raleighlib.cli.arcgis.layer_fields") as mock_fields, \
             patch("raleighlib.cli.arcgis.sample_features") as mock_sample:
            mock_fields.return_value = [{"name": "OBJECTID", "type": "esriFieldTypeOID"}]
            mock_sample.return_value = [{"attributes": {"OBJECTID": 1}, "geometry": {"x": 1.0, "y": 2.0}}]
            code, out, err = self.run_cli(["info", "Test", "--json"])
        self.assertEqual(code, 0, err)
        data = json.loads(out)
        self.assertIn("dataset", data)
        self.assertIn("fields", data)
        self.assertIn("sample", data)
        self.assertEqual(data["sample"]["type"], "FeatureCollection")
        self.assertEqual(len(data["sample"]["features"]), 1)

    def test_catalog_json_returns_top_level_array(self):
        with patch("raleighlib.cli.hub.catalog_from_cache_or_live") as mock_catalog:
            mock_catalog.return_value = [{"id": "x", "title": "Test", "type": "FeatureServer", "access": "public"}]
            code, out, err = self.run_cli(["catalog", "--json"])
        self.assertEqual(code, 0, err)
        data = json.loads(out)
        self.assertIsInstance(data, list)

    def test_search_json_returns_top_level_array(self):
        with patch("raleighlib.cli.hub.catalog_from_cache_or_live") as mock_catalog:
            mock_catalog.return_value = [{"id": "x", "title": "Test", "type": "FeatureServer", "access": "public"}]
            code, out, err = self.run_cli(["search", "test", "--json"])
        self.assertEqual(code, 0, err)
        data = json.loads(out)
        self.assertIsInstance(data, list)

    def test_categories_json_returns_top_level_array(self):
        with patch("raleighlib.cli.hub.catalog_from_cache_or_live") as mock_catalog:
            mock_catalog.return_value = [{"id": "x", "title": "Test", "type": "FeatureServer", "category": "Parks"}]
            code, out, err = self.run_cli(["categories", "--json"])
        self.assertEqual(code, 0, err)
        data = json.loads(out)
        self.assertIsInstance(data, list)


class ServiceRootResolutionTests(unittest.TestCase):
    def test_resolve_featureserver_root_to_first_layer(self):
        root_meta = {
            "layers": [{"id": 0, "name": "Dog Parks"}],
            "tables": [],
        }
        with patch("raleighlib.arcgis.core.json_request", return_value=root_meta):
            url = arcgis.resolve_queryable_layer(
                "https://services.arcgis.com/v400IkDOw1ad7Yad/arcgis/rest/services/DogParkLocations_Existing_PUBLIC/FeatureServer"
            )
        self.assertEqual(url, "https://services.arcgis.com/v400IkDOw1ad7Yad/arcgis/rest/services/DogParkLocations_Existing_PUBLIC/FeatureServer/0")

    def test_resolve_mapserver_root_to_first_layer(self):
        root_meta = {
            "layers": [{"id": 1, "name": "Inspections"}],
            "tables": [],
        }
        with patch("raleighlib.arcgis.core.json_request", return_value=root_meta):
            url = arcgis.resolve_queryable_layer(
                "https://maps.wake.gov/arcgis/rest/services/Inspections/RestaurantInspectionsOpenData/MapServer"
            )
        self.assertEqual(url, "https://maps.wake.gov/arcgis/rest/services/Inspections/RestaurantInspectionsOpenData/MapServer/1")

    def test_resolve_preserves_direct_layer_url(self):
        layer_url = "https://maps.wake.gov/arcgis/rest/services/Inspections/RestaurantInspectionsOpenData/MapServer/1"
        with patch("raleighlib.arcgis.core.json_request") as mock_req:
            url = arcgis.resolve_queryable_layer(layer_url)
            mock_req.assert_not_called()
        self.assertEqual(url, layer_url)

    def test_has_geometry_read_from_layer_metadata(self):
        layer_url = "https://services.arcgis.com/v400IkDOw1ad7Yad/arcgis/rest/services/DogParkLocations_Existing_PUBLIC/FeatureServer/0"
        with patch("raleighlib.arcgis.core.json_request", return_value={"geometryType": "esriGeometryPoint"}):
            self.assertTrue(arcgis.layer_has_geometry(layer_url))
        with patch("raleighlib.arcgis.core.json_request", return_value={"type": "Table"}):
            self.assertFalse(arcgis.layer_has_geometry(layer_url))


class EnerGovContractTests(unittest.TestCase):
    def test_public_search_posts_json(self):
        criteria = {
            "Result": {
                "Keyword": "",
                "ExactMatch": False,
                "SearchModule": 1,
                "FilterModule": 0,
                "SearchMainAddress": False,
                "PageNumber": 0,
                "PageSize": 0,
                "PermitCriteria": {"PermitNumber": None},
            }
        }
        search_result = {"Result": {"EntityResults": [{"RecordNumber": "BP-2024-001"}], "TotalFound": 1}}
        with patch("raleighlib.development.core.json_request", side_effect=[criteria, search_result]) as mock_req:
            result = development.public_search("permit", query="2024-001")
        calls = mock_req.call_args_list
        called_url = calls[1][0][0]
        payload = json.loads(calls[1].kwargs.get("data", b"").decode("utf-8"))
        self.assertIn("/api/energov/search/search", called_url)
        self.assertEqual(calls[1].kwargs.get("method"), "POST")
        self.assertIn("RaleighNCProd", str(calls[1].kwargs.get("headers", {})))
        self.assertEqual(payload["Keyword"], "2024-001")
        self.assertEqual(payload["ExactMatch"], True)
        self.assertEqual(payload["FilterModule"], 2)
        self.assertEqual(payload["SearchModule"], 1)
        self.assertEqual(payload["PageNumber"], 1)
        self.assertEqual(payload["PageSize"], 20)
        self.assertEqual(payload["SortAscending"], True)
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["results"][0]["RecordNumber"], "BP-2024-001")

    def test_unsupported_endpoint_error_still_available(self):
        # UnsupportedEndpointError is retained for future guest-public boundaries.
        self.assertTrue(issubclass(development.UnsupportedEndpointError, Exception))


class EscribeRegressionTests(unittest.TestCase):
    def test_fetch_uses_user_agent(self):
        with patch.object(core._OPENER, "open") as mock_open:
            mock_resp = MagicMock()
            mock_resp.geturl.return_value = "https://pub-raleighnc.escribemeetings.com/?MeetingViewId=2"
            mock_resp.read.side_effect = [
                b"<html><title>eSCRIBE Published Meetings</title><body>No upcoming meetings</body></html>",
                b"",
            ]
            mock_open.return_value.__enter__.return_value = mock_resp
            mock_open.return_value.__exit__.return_value = False
            meetings.list_upcoming()
            req = mock_open.call_args[0][0]
            agent = req.get_header("User-agent")
            self.assertIsNotNone(agent)
            self.assertIn("RaleighCivicDataCLI", agent)

    def test_meeting_detail_parses_uuid_id(self):
        html = """
        <html><body>
        <h1>Budget Meeting</h1>
        <time datetime="2025-10-14">October 14, 2025</time>
        <a class="download-link" href="Meeting.aspx?Id=550e8400-e29b-41d4-a716-446655440000&lang=English">Agenda</a>
        </body></html>
        """
        with patch("raleighlib.meetings.core.raw_request", return_value=html.encode()), patch(
            "raleighlib.meetings._find_past_meeting_record", return_value=None
        ):
            detail = meetings.meeting_detail("550e8400-e29b-41d4-a716-446655440000")
        self.assertEqual(detail["id"], "550e8400-e29b-41d4-a716-446655440000")
        self.assertIn("Meeting.aspx", detail["agenda"])


class GlobalFlagTests(unittest.TestCase):
    def test_global_flags_after_subcommand(self):
        with patch("raleighlib.cli.hub.catalog_from_cache_or_live") as mock_catalog:
            mock_catalog.return_value = [{"id": "x", "title": "Test", "type": "FeatureServer", "access": "public"}]
            code, out, err = self.run_cli(["search", "test", "--json"])
        self.assertEqual(code, 0, err)
        self.assertIn("Test", out)

    def test_global_flags_after_nested_subcommand(self):
        with patch("raleighlib.cli.imagery.list_services") as mock_list:
            mock_list.return_value = [{"name": "Orthos2025", "type": "ImageServer"}]
            code, out, err = self.run_cli(["imagery", "catalog", "--json", "--limit", "1"])
        self.assertEqual(code, 0, err)
        self.assertIn("Orthos2025", out)

    def test_global_flags_before_subcommand(self):
        with patch("raleighlib.cli.hub.catalog_from_cache_or_live") as mock_catalog:
            mock_catalog.return_value = [{"id": "x", "title": "Test", "type": "FeatureServer", "access": "public"}]
            code, out, err = self.run_cli(["--json", "search", "test"])
        self.assertEqual(code, 0, err)
        self.assertIn("Test", out)

    def run_cli(self, arguments):
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            try:
                result = cli.main(arguments)
            except SystemExit as exc:
                return exc.code, stdout.getvalue(), stderr.getvalue()
        return result, stdout.getvalue(), stderr.getvalue()


class ConciseErrorTests(unittest.TestCase):
    def test_security_error_exits_without_traceback(self):
        with patch("raleighlib.cli.meetings.meeting_detail") as mock_detail:
            mock_detail.return_value = {"agenda": "https://evil.example.com/agenda.pdf"}
            code, out, err = self.run_cli(["meetings", "download-agenda", "550e8400-e29b-41d4-a716-446655440000", "-o", "/tmp/agenda.pdf"])
        self.assertNotEqual(code, 0)
        self.assertNotIn("Traceback", err)
        self.assertIn("not allowlisted", err)

    def test_catalog_error_exits_without_traceback(self):
        with patch("raleighlib.cli.hub.catalog_from_cache_or_live", side_effect=hub.CatalogError("unavailable")):
            code, out, err = self.run_cli(["catalog"])
        self.assertNotEqual(code, 0)
        self.assertNotIn("Traceback", err)
        self.assertIn("unavailable", err)

    def run_cli(self, arguments):
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            try:
                result = cli.main(arguments)
            except SystemExit as exc:
                return exc.code, stdout.getvalue(), stderr.getvalue()
        return result, stdout.getvalue(), stderr.getvalue()


class CacheFallbackTests(unittest.TestCase):
    def test_catalog_falls_back_to_stale_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.environ["RALEIGH_CACHE"] = tmp
            try:
                core.write_cache("hub-catalog.json", [{"id": "stale", "title": "Stale", "access": "public"}])
                path = core.cache_path("hub-catalog.json")
                old_mtime = path.stat().st_mtime - 7200
                os.utime(path, (old_mtime, old_mtime))
                with patch("raleighlib.hub.fetch_catalog", side_effect=RuntimeError("network down")):
                    catalog = hub.catalog_from_cache_or_live(max_age_seconds=60)
                self.assertEqual(catalog[0]["id"], "stale")
                self.assertTrue(catalog[0].get("_stale"))
                self.assertIn("network down", catalog[0].get("_stale_reason", ""))
            finally:
                os.environ.pop("RALEIGH_CACHE", None)

    def test_cache_write_is_atomic(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.environ["RALEIGH_CACHE"] = tmp
            try:
                core.write_cache("atomic-test.json", {"value": 1})
                path = core.cache_path("atomic-test.json")
                self.assertTrue(path.exists())
                # Ensure no temp file remains.
                self.assertFalse(path.with_suffix(".json.tmp").exists())
            finally:
                os.environ.pop("RALEIGH_CACHE", None)

    def test_cache_write_ignores_predictable_temp_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.environ["RALEIGH_CACHE"] = tmp
            try:
                target = pathlib.Path(tmp) / "target.json"
                target.write_text("sentinel")
                (pathlib.Path(tmp) / "atomic-test.json.tmp").symlink_to(target)
                core.write_cache("atomic-test.json", {"value": 1})
                self.assertEqual(target.read_text(), "sentinel")
                self.assertEqual(core.read_cache("atomic-test.json"), {"value": 1})
            finally:
                os.environ.pop("RALEIGH_CACHE", None)

    def test_safe_write_ignores_predictable_temp_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            target = root / "target.txt"
            target.write_text("sentinel")
            destination = root / "output.txt"
            destination.with_suffix(".txt.tmp").symlink_to(target)
            core.safe_write(destination, "result")
            self.assertEqual(target.read_text(), "sentinel")
            self.assertEqual(destination.read_text(), "result")


class UrlSafetyTests(unittest.TestCase):
    def test_rejects_http(self):
        self.assertFalse(core.is_allowed_host("http://data.raleighnc.gov/foo"))

    def test_rejects_redirect_to_evil_host(self):
        self.assertFalse(core.is_allowed_host("https://data.raleighnc.gov.evil.example.com/foo"))

    def test_redirect_reapplies_post_path_policy(self):
        source = "https://raleighnc-energovpub.tylerhost.net/apps/selfservice/api/energov/search/search"
        destination = "https://raleighnc-energovpub.tylerhost.net/apps/selfservice/api/admin/write"
        request = urllib.request.Request(source, data=b"{}", method="POST")
        with self.assertRaises(core.RequestPolicyError):
            core.AllowlistRedirectHandler().redirect_request(
                request, None, 307, "redirect", {}, destination
            )

    def test_redirect_rejects_cross_origin_post_body(self):
        source = "https://raleighnc-energovpub.tylerhost.net/apps/selfservice/api/energov/search/search"
        destination = "https://services1.arcgis.com/example/arcgis/rest/services/Test/FeatureServer/0/query"
        request = urllib.request.Request(source, data=b"{}", method="POST")
        with self.assertRaises(core.SecurityError):
            core.AllowlistRedirectHandler().redirect_request(
                request, None, 307, "redirect", {}, destination
            )

    def test_escribe_post_policy_is_host_scoped(self):
        path = "/MeetingsCalendarView.aspx/PastMeetings"
        core._enforce_method_policy(
            "POST", f"https://pub-raleighnc.escribemeetings.com{path}"
        )
        with self.assertRaises(core.RequestPolicyError):
            core._enforce_method_policy("POST", f"https://raleighnc.gov{path}")


class RealtimeFilterTests(unittest.TestCase):
    def test_realtime_enrichment_uses_route_from_static_trip(self):
        feed = {
            "routes": [
                {"route_id": "R1", "route_short_name": "1", "route_long_name": "North Hills"}
            ],
            "trips": [{"trip_id": "T1", "route_id": "R1"}],
            "stops": [],
        }
        entities = [{"vehicle": {"trip": {"trip_id": "T1"}}}]
        result = transit.enrich_realtime_with_static(entities, feed)
        self.assertEqual(result[0]["route_id"], "R1")
        self.assertEqual(result[0]["route_short_name"], "1")
        self.assertEqual(result[0]["route_long_name"], "North Hills")

    def test_vehicle_positions_filters_by_route(self):
        feed = {
            "routes": [{"route_id": "R1", "route_short_name": "1"}],
            "trips": [{"trip_id": "T1", "route_id": "R1"}, {"trip_id": "T2", "route_id": "R2"}],
            "stops": [],
        }
        entities = [
            {"vehicle": {"trip": {"trip_id": "T1"}, "vehicle": {"id": "V1"}}},
            {"vehicle": {"trip": {"trip_id": "T2"}, "vehicle": {"id": "V2"}}},
        ]
        filtered = transit.filter_vehicle_positions(entities, feed, route="R1")
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["trip_id"], "T1")


class SubprocessCliTests(unittest.TestCase):
    def test_cli_subprocess_help(self):
        result = subprocess.run(
            [sys.executable, str(CLI_SCRIPT), "--help"],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("catalog", result.stdout)

    def test_cli_subprocess_flag_after_nested_subcommand(self):
        result = subprocess.run(
            [sys.executable, str(CLI_SCRIPT), "imagery", "catalog", "--help"],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--limit", result.stdout)
        # --json is a parent parser flag.
        result_parent = subprocess.run(
            [sys.executable, str(CLI_SCRIPT), "--help"],
            capture_output=True, text=True, timeout=30,
        )
        self.assertIn("--json", result_parent.stdout)

    def test_cli_subprocess_flag_before_nested_subcommand(self):
        result = subprocess.run(
            [sys.executable, str(CLI_SCRIPT), "--json", "imagery", "catalog", "--help"],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--limit", result.stdout)

    def test_cli_subprocess_failure_returns_nonzero_no_traceback(self):
        result = subprocess.run(
            [sys.executable, str(CLI_SCRIPT), "info", "DoesNotExist"],
            capture_output=True, text=True, timeout=30,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("Traceback", result.stderr)
        self.assertIn("not found", result.stderr)

    def test_cli_imagery_identify_subprocess(self):
        result = subprocess.run(
            [sys.executable, str(CLI_SCRIPT), "imagery", "identify", "Orthos2025", "--point=-78.65,35.75", "--json"],
            capture_output=True, text=True, timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertIn("location", data)

    def test_cli_imagery_statistics_subprocess(self):
        result = subprocess.run(
            [sys.executable, str(CLI_SCRIPT), "imagery", "statistics", "Orthos2025", "--bbox=-78.7,35.7,-78.6,35.8", "--json"],
            capture_output=True, text=True, timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertIn("statistics", data)

    def test_cli_imagery_identify_error_is_concise(self):
        result = subprocess.run(
            [sys.executable, str(CLI_SCRIPT), "imagery", "identify", "NonexistentService", "--point=-78.65,35.75", "--json"],
            capture_output=True, text=True, timeout=30,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("Traceback", result.stderr)


class FinalReviewRegressionTests(unittest.TestCase):
    def test_civic_inclusive_end_date_accepts_timestamp_on_that_date(self):
        record = {"attributes": {"field_event_date": {"value": "2026-07-31T23:59:59-04:00"}}}
        self.assertTrue(civic._matches_date_range(record, None, "2026-07-31", "field_event_date"))
        self.assertFalse(civic._matches_date_range(record, None, "2026-07-30", "field_event_date"))

    def test_imagery_export_rejects_http_200_non_image_body(self):
        with patch("raleighlib.imagery.service_info", return_value={"capabilities": "Image"}), patch(
            "raleighlib.imagery.core.raw_request", return_value=b"<html>not an image</html>"
        ):
            with self.assertRaisesRegex(imagery.CapabilityError, "non-image"):
                imagery.export_image("https://maps.raleighnc.gov/x/ImageServer", (0, 0, 1, 1))

    def test_imagery_service_path_is_url_encoded(self):
        self.assertEqual(
            cli_lib._resolve_imagery_url("Hosted/Evening Temperature"),
            f"{imagery.IMAGE_ROOT}/Hosted/Evening%20Temperature/ImageServer",
        )

    def test_batch_geocode_preserves_arbitrary_source_id_and_row(self):
        response = {"locations": [{
            "attributes": {"ResultID": 42, "Score": 99, "Match_addr": "Match"},
            "location": {"x": -78.6, "y": 35.8},
        }]}
        source = {"OBJECTID": 42, "SingleLine": "1 Main St", "case_id": "alpha"}
        with patch("raleighlib.geocode.core.json_request", return_value=response):
            result = geocode.geocode_addresses([source])[0]
        self.assertEqual(result["input_id"], 42)
        self.assertEqual(result["source"], source)
        self.assertEqual(result["status"], "matched")

        string_source = {"OBJECTID": "case-alpha", "SingleLine": "2 Main St"}
        string_response = {"locations": [{
            "attributes": {"ResultID": 1, "Score": 97, "Match_addr": "2 Main St"},
            "location": {"x": -78.7, "y": 35.7},
        }]}
        with patch("raleighlib.geocode.core.json_request", return_value=string_response):
            string_result = geocode.geocode_addresses([string_source])[0]
        self.assertEqual(string_result["input_id"], "case-alpha")
        self.assertEqual(string_result["source"], string_source)
        self.assertEqual(string_result["status"], "matched")

    def test_batch_geocode_cli_preserves_original_csv_columns(self):
        with tempfile.TemporaryDirectory() as td:
            source = pathlib.Path(td) / "in.csv"
            destination = pathlib.Path(td) / "out.csv"
            source.write_text("=column,address,status\n=CMD(),1 Main St,original\n", encoding="utf-8")
            response = {"locations": [{
                "attributes": {"ResultID": 1, "Score": 99, "Match_addr": "1 Main St"},
                "location": {"x": -78.6, "y": 35.8},
            }]}
            with patch("raleighlib.geocode.core.json_request", return_value=response), redirect_stdout(io.StringIO()):
                code = cli_lib.main(["geocode-batch", str(source), "-o", str(destination)])
            self.assertEqual(code, 0)
            with destination.open(encoding="utf-8") as stream:
                row = next(csv.DictReader(stream))
            self.assertEqual(row["'=column"], "'=CMD()")
            self.assertEqual(row["status"], "original")
            self.assertEqual(row["geocode_status"], "matched")

    def test_gtfs_cache_preserves_validated_zip_and_provenance(self):
        archive = TransitTests()._make_gtfs_zip()
        with tempfile.TemporaryDirectory() as td, patch.dict(os.environ, {"RALEIGH_CACHE": td}), patch(
            "raleighlib.transit.download_gtfs", return_value=archive
        ) as download:
            first = transit._load_feed_with_cache()
            second = transit._load_feed_with_cache()
            self.assertEqual(first["routes"], second["routes"])
            self.assertEqual(download.call_count, 1)
            self.assertEqual((pathlib.Path(td) / "gtfs-feed.zip").read_bytes(), archive)
            metadata = json.loads((pathlib.Path(td) / "gtfs-feed-metadata.json").read_text())
            self.assertEqual(metadata["source_url"], transit.STATIC_FEED)
            self.assertTrue(metadata["validated"])
            self.assertIn("retrieved_at", metadata)
            (pathlib.Path(td) / "gtfs-feed.zip").write_bytes(b"not-a-zip")
            recovered = transit._load_feed_with_cache()
            self.assertEqual(download.call_count, 2)
            self.assertEqual(recovered["routes"], first["routes"])

    def test_alert_relationships_are_enriched(self):
        feed = {
            "routes": [{"route_id": "R1", "route_short_name": "1", "route_long_name": "Main"}],
            "trips": [{"trip_id": "T1", "route_id": "R1", "trip_headsign": "Downtown"}],
            "stops": [{"stop_id": "S1", "stop_name": "Main St"}],
        }
        entity = {"alert": {"informed_entity": [{
            "route_id": "R1", "trip": {"trip_id": "T1"}, "stop_id": "S1"
        }]}}
        informed = transit.enrich_realtime_with_static([entity], feed)[0]["alert"]["informed_entity"][0]
        self.assertEqual(informed["route_short_name"], "1")
        self.assertEqual(informed["trip_headsign"], "Downtown")
        self.assertEqual(informed["stop_name"], "Main St")

    def test_malformed_realtime_cli_reports_error_without_traceback(self):
        malformed = (pathlib.Path(__file__).parent / "fixtures" / "gtfs-realtime-malformed.bin").read_bytes()
        stderr = io.StringIO()
        with patch("raleighlib.transit.core.raw_request", return_value=malformed), redirect_stderr(stderr):
            code = cli_lib.main(["--json", "transit", "alerts"])
        self.assertEqual(code, 1)
        self.assertIn("malformed", stderr.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())

    def test_development_schema_errors_and_runtime_project_discovery(self):
        stderr = io.StringIO()
        with patch("raleighlib.development.core.json_request", return_value={"Result": []}), redirect_stderr(stderr):
            code = cli_lib.main(["development", "search", "permit"])
        self.assertEqual(code, 1)
        self.assertIn("schema", stderr.getvalue())
        criteria = {"Result": {"PermitCriteria": {}}}
        malformed_results = [
            {"Result": {"EntityResults": {}, "TotalFound": 0}},
            {"Result": {"EntityResults": ["not-an-object"], "TotalFound": 1}},
            {"Result": {"EntityResults": [], "TotalFound": "0"}},
        ]
        for malformed in malformed_results:
            with self.subTest(malformed=malformed), patch(
                "raleighlib.development.core.json_request", side_effect=[criteria, malformed]
            ):
                with self.assertRaises(development.UnsupportedEndpointError):
                    development.public_search("permit")
        criteria = {"Result": {"ProjectCriteria": {}}}
        response = {"Result": {"EntityResults": [], "TotalFound": 0}}
        with patch("raleighlib.development.core.json_request", side_effect=[criteria, response]), redirect_stdout(io.StringIO()):
            code = cli_lib.main(["--json", "development", "search", "project"])
        self.assertEqual(code, 0)

    def test_escribe_rejects_excessive_meeting_types_before_posting(self):
        listing = "".join(
            f'<div class="MeetingTypeContainer" MeetingType="Type {index}"></div>'
            for index in range(meetings.MAX_PAST_MEETING_TYPES + 1)
        )
        with patch("raleighlib.meetings._fetch_html", return_value=listing), patch(
            "raleighlib.meetings.core.json_request"
        ) as request:
            with self.assertRaisesRegex(meetings.CompatibilityError, "meeting types"):
                list(meetings._past_meeting_items(2025))
        request.assert_not_called()

        bounded_listing = "".join(
            f'<div class="MeetingTypeContainer" MeetingType="Type {index}"></div>'
            for index in range(meetings.MAX_PAST_MEETING_TYPES)
        )
        def meeting_page(*_args, **kwargs):
            payload = json.loads(kwargs["data"])
            return {"d": {"Meetings": [{"Id": f"{payload['type']}-{payload['pageNumber']}"}], "TotalCount": 5}}

        with patch("raleighlib.meetings._fetch_html", return_value=bounded_listing), patch(
            "raleighlib.meetings.core.json_request", side_effect=meeting_page
        ) as request:
            with self.assertRaisesRegex(meetings.CompatibilityError, "request budget"):
                list(meetings._past_meeting_items(2025))
        self.assertEqual(request.call_count, meetings.MAX_PAST_REQUESTS)

    def test_csv_formula_safety_covers_headers_and_control_prefixes(self):
        for value in (
            "=1+1",
            "+1",
            "-1",
            "@x",
            "\t=1+1",
            "\r=1+1",
            "\n=1+1",
            "\v=1+1",
            "\f=1+1",
            "\u00a0=1+1",
            "\ufeff=1+1",
            "  =1+1",
        ):
            with self.subTest(value=value):
                self.assertTrue(arcgis.csv_safe_value(value).startswith("'"))
        rendered = arcgis.csv_from_records([{"attributes": {"=header": "\t=1+1"}}])
        rows = list(csv.reader(io.StringIO(rendered)))
        self.assertEqual(rows[0][0], "'=header")
        self.assertEqual(rows[1][0], "'\t=1+1")

    def test_gtfs_semantic_validation_and_download_gate(self):
        empty = io.BytesIO()
        with zipfile.ZipFile(empty, "w"):
            pass
        with self.assertRaisesRegex(ValueError, "missing non-empty agency"):
            transit.parse_gtfs_zip(empty.getvalue())

        malformed = io.BytesIO()
        with zipfile.ZipFile(malformed, "w") as zf:
            zf.writestr("agency.txt", "agency_name,agency_url,agency_timezone\nGoRaleigh,,America/New_York\n")
        with self.assertRaisesRegex(ValueError, "missing required values"):
            transit.parse_gtfs_zip(malformed.getvalue())

        with tempfile.TemporaryDirectory() as td:
            destination = pathlib.Path(td) / "feed.zip"
            with patch("raleighlib.transit.download_gtfs", return_value=empty.getvalue()), redirect_stderr(io.StringIO()):
                code = cli_lib.main(["transit", "download-gtfs", "-o", str(destination)])
            self.assertEqual(code, 1)
            self.assertFalse(destination.exists())

    def test_realtime_rejects_parseable_uninitialized_message(self):
        with self.assertRaisesRegex(ValueError, "required fields"):
            transit._decode_realtime(b"")

    def test_development_detail_and_inspection_schemas_fail_explicitly(self):
        test_uuid = "d4701697-8a5b-49ed-bb16-5334fad23d08"
        with patch("raleighlib.development._resolve_uuid", return_value=test_uuid), patch(
            "raleighlib.development.core.json_request", return_value={"Result": []}
        ):
            with self.assertRaises(development.UnsupportedEndpointError):
                development.permit_detail(test_uuid)
        malformed_inspections = (
            {"Result": {"unexpected": []}},
            {"Result": ["not-an-object"]},
            {"Result": 1},
        )
        for payload in malformed_inspections:
            with self.subTest(payload=payload), patch(
                "raleighlib.development._resolve_uuid", return_value=test_uuid
            ), patch("raleighlib.development.core.json_request", return_value=payload):
                with self.assertRaises(development.UnsupportedEndpointError):
                    development.inspections_for_record(test_uuid)

    def test_upcoming_meetings_rejects_unrecognized_empty_markup(self):
        with patch("raleighlib.meetings._fetch_html", return_value="<html><title>maintenance</title></html>"):
            with self.assertRaisesRegex(meetings.CompatibilityError, "identity"):
                meetings.list_upcoming()
        recognized_empty = "<html><title>eSCRIBE Published Meetings</title><body>No upcoming meetings</body></html>"
        with patch("raleighlib.meetings._fetch_html", return_value=recognized_empty):
            self.assertEqual(meetings.list_upcoming(), [])

    def test_jsonapi_pagination_stays_on_expected_origin_and_path(self):
        current = "https://raleighnc.gov/jsonapi/node/news?page%5Blimit%5D=50"
        self.assertEqual(
            civic._validated_jsonapi_next("?page[offset]=50", current),
            "https://raleighnc.gov/jsonapi/node/news?page[offset]=50",
        )
        for href in (
            "https://example.com/jsonapi/node/news",
            "https://raleighnc.gov/admin",
            "https://raleighnc.gov/jsonapi/user/user?page[offset]=50",
            "https://raleighnc.gov:8443/jsonapi/node/news",
        ):
            with self.subTest(href=href), self.assertRaises(civic.ResourceError):
                civic._validated_jsonapi_next(href, current)

    def test_jsonapi_discovered_collection_path_must_match_resource_type(self):
        with patch(
            "raleighlib.civic._discover_resource_paths",
            return_value={"node--news": "https://raleighnc.gov/jsonapi/user/user"},
        ):
            with self.assertRaisesRegex(civic.ResourceError, "invalid path"):
                civic._resource_type_to_path("node--news")

    def test_jsonapi_rejects_non_object_top_level_document(self):
        with patch("raleighlib.civic._discover_resource_paths", return_value={}), patch(
            "raleighlib.civic.core.json_request", return_value=[]
        ):
            with self.assertRaisesRegex(civic.ResourceError, "non-object document"):
                civic.fetch_news(limit=1)

    def test_hub_rejects_premature_empty_page_before_number_matched(self):
        pages = [
            {"features": [{"id": "one", "properties": {}}], "numberMatched": 2},
            {"features": [], "numberMatched": 2},
        ]
        with patch("raleighlib.hub.fetch_collection", side_effect=pages):
            with self.assertRaisesRegex(hub.CatalogError, "ended before"):
                hub.fetch_all_records("dataset")

    def test_development_search_slices_untrusted_upstream_page_to_limit(self):
        criteria = {"Result": {"PermitCriteria": {}}}
        response = {
            "Result": {
                "EntityResults": [
                    {"CaseId": {"Id": str(index)}} for index in range(3)
                ],
                "TotalFound": 3,
            }
        }
        with patch("raleighlib.development.fetch_criteria", return_value=criteria), patch(
            "raleighlib.development.core.json_request", return_value=response
        ):
            result = development.public_search("permit", limit=2)
        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["total"], 3)

    def test_development_inspections_slices_untrusted_upstream_page_to_limit(self):
        response = {
            "Result": [
                {"InspectionId": {"Id": str(index)}} for index in range(3)
            ]
        }
        with patch(
            "raleighlib.development._resolve_uuid", return_value="record-uuid"
        ), patch("raleighlib.development.core.json_request", return_value=response):
            result = development.inspections_for_record("record-uuid", limit=1)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["InspectionId"], "0")

    def test_meetings_reject_duplicate_historical_ids(self):
        listing = '<div MeetingType="Council"></div>'
        page = {
            "d": {
                "Meetings": [{"Id": "same"}, {"Id": "same"}],
                "TotalCount": 2,
            }
        }
        with patch("raleighlib.meetings._fetch_html", return_value=listing), patch(
            "raleighlib.meetings.core.json_request", return_value=page
        ):
            with self.assertRaisesRegex(meetings.CompatibilityError, "repeated"):
                list(meetings._past_meeting_items(2025))

    def test_realtime_entities_require_exactly_one_present_payload(self):
        message = gtfs_realtime_pb2.FeedMessage()
        message.header.gtfs_realtime_version = "2.0"
        message.entity.add().id = "missing-payload"
        with self.assertRaisesRegex(ValueError, "exactly one payload"):
            transit._decode_realtime(message.SerializeToString())

        valid = gtfs_realtime_pb2.FeedMessage()
        valid.header.gtfs_realtime_version = "2.0"
        entity = valid.entity.add()
        entity.id = "vehicle"
        entity.vehicle.SetInParent()
        decoded = transit._decode_realtime(valid.SerializeToString())
        self.assertEqual(set(decoded["entity"][0]), {"id", "vehicle"})

    def test_rss_limit_is_global_across_channels(self):
        feed = b"""<rss><channel><item><guid>a</guid><title>A</title></item></channel>
        <channel><item><guid>b</guid><title>B</title></item></channel></rss>"""
        with patch("raleighlib.civic.core.raw_request", return_value=feed):
            self.assertEqual(len(civic.fetch_rss(limit=1)), 1)

    def test_catalog_truncation_guidance_names_workable_limit(self):
        catalog = [
            {"id": str(index), "title": f"Item {index}", "type": "FeatureServer", "url": "https://example.invalid"}
            for index in range(101)
        ]
        args = cli_lib.build_parser().parse_args(["catalog"])
        with patch("raleighlib.cli._ensure_catalog", return_value=catalog), redirect_stdout(io.StringIO()) as stdout:
            self.assertEqual(cli_lib.cmd_catalog(args), 0)
        self.assertIn("--limit 101 --json", stdout.getvalue())

    def test_imagery_catalog_caps_upstream_folder_fanout(self):
        root = {
            "services": [],
            "folders": [f"folder-{index}" for index in range(imagery.MAX_IMAGE_FOLDERS + 1)],
        }
        with patch("raleighlib.imagery.core.json_request", return_value=root) as request:
            with self.assertRaisesRegex(imagery.CapabilityError, "folders"):
                imagery.list_services()
        self.assertEqual(request.call_count, 1)

    def test_imagery_catalog_caps_aggregate_services(self):
        root = {
            "services": [
                {"name": f"service-{index}", "type": "ImageServer"}
                for index in range(imagery.MAX_IMAGE_SERVICES)
            ],
            "folders": ["extra"],
        }
        folder = {"services": [{"name": "overflow", "type": "ImageServer"}]}
        with patch(
            "raleighlib.imagery.core.json_request", side_effect=[root, folder]
        ) as request:
            with self.assertRaisesRegex(imagery.CapabilityError, "services"):
                imagery.list_services()
        self.assertEqual(request.call_count, 2)

    def test_vehicle_positions_honor_stop_filter(self):
        entities = [
            {"vehicle": {"trip": {"trip_id": "T1"}, "stop_id": "S2"}}
        ]
        feed = {"trips": [{"trip_id": "T1", "route_id": "R1"}], "routes": []}
        self.assertEqual(
            transit.filter_vehicle_positions(entities, feed, stop="S1"),
            [],
        )
        self.assertEqual(
            len(transit.filter_vehicle_positions(entities, feed, stop="S2")),
            1,
        )

    def test_adapters_reject_non_object_top_level_json(self):
        with patch("raleighlib.arcgis.core.json_request", return_value=[]):
            with self.assertRaisesRegex(ValueError, "non-object"):
                arcgis.query_layer("https://maps.raleighnc.gov/arcgis/rest/services/X/FeatureServer/0")
        with patch("raleighlib.imagery.core.json_request", return_value=[]):
            with self.assertRaisesRegex(ValueError, "non-object"):
                imagery.list_services()
        with patch("raleighlib.geocode.core.json_request", return_value=[]):
            with self.assertRaisesRegex(ValueError, "non-object"):
                geocode.suggest("Main")
        with patch("raleighlib.development.fetch_criteria", return_value={"Result": {"PermitCriteria": {}}}), patch(
            "raleighlib.development.core.json_request", return_value=[]
        ):
            with self.assertRaisesRegex(ValueError, "non-object"):
                development.public_search("permit")
        listing = '<div MeetingType="Council"></div>'
        with patch("raleighlib.meetings._fetch_html", return_value=listing), patch(
            "raleighlib.meetings.core.json_request", return_value=[]
        ):
            with self.assertRaisesRegex(ValueError, "non-object"):
                list(meetings._past_meeting_items(2025))

    def test_public_library_limits_reject_nonpositive_values_before_io(self):
        for limit in (0, -1):
            with self.subTest(adapter="civic", limit=limit), patch(
                "raleighlib.civic.core.json_request"
            ) as request:
                with self.assertRaisesRegex(ValueError, "positive"):
                    civic.fetch_news(limit=limit)
                request.assert_not_called()
            with self.subTest(adapter="development", limit=limit), patch(
                "raleighlib.development.fetch_criteria"
            ) as criteria:
                with self.assertRaisesRegex(ValueError, "positive"):
                    development.public_search("permit", limit=limit)
                criteria.assert_not_called()

    def test_nondefault_https_port_is_rejected(self):
        self.assertFalse(core.is_allowed_host("https://data.raleighnc.gov:8443/api"))

    def test_same_host_cross_port_redirect_is_rejected(self):
        request = urllib.request.Request("https://data.raleighnc.gov/source")
        with self.assertRaises(core.SecurityError):
            core.AllowlistRedirectHandler().redirect_request(
                request, None, 307, "redirect", {}, "https://data.raleighnc.gov:8443/target"
            )

    def test_body_without_explicit_method_is_treated_as_post(self):
        with self.assertRaises(core.RequestPolicyError):
            core.json_request("https://raleighnc.gov/jsonapi/node/news", data=b"payload")

    def test_arcgis_post_path_is_host_scoped(self):
        fake = "https://raleighnc.gov/arcgis/rest/services/Fake/FeatureServer/0/query"
        with self.assertRaises(core.RequestPolicyError):
            core._enforce_method_policy("POST", fake)

    def test_safe_write_does_not_clobber_racing_destination(self):
        with tempfile.TemporaryDirectory() as tmp:
            destination = pathlib.Path(tmp) / "output.txt"
            original_link = os.link

            def racing_link(source, target):
                pathlib.Path(target).write_text("racer")
                return original_link(source, target)

            with patch("raleighlib.core.os.link", side_effect=racing_link):
                with self.assertRaises(FileExistsError):
                    core.safe_write(destination, "agent")
            self.assertEqual(destination.read_text(), "racer")

    def test_arcgis_client_limit_survives_server_overreturn(self):
        features = [{"attributes": {"OBJECTID": i}} for i in range(100)]
        with patch("raleighlib.arcgis.query_layer", return_value={"features": features}):
            rows = arcgis.query_all_pages("https://services.arcgis.com/x/FeatureServer/0", max_records=10)
        self.assertEqual(len(rows), 10)

    def test_arcgis_repeated_page_fails_closed(self):
        page = {"features": [{"attributes": {"OBJECTID": 1}}], "exceededTransferLimit": True}
        with patch("raleighlib.arcgis.query_layer", return_value=page):
            with self.assertRaisesRegex(ValueError, "repeated"):
                arcgis.query_all_pages("https://services.arcgis.com/x/FeatureServer/0", page_size=1)

    def test_geocoder_rejects_http_200_error(self):
        with patch("raleighlib.geocode.core.json_request", return_value={"error": {"message": "bad locator", "details": ["detail"]}}):
            with self.assertRaisesRegex(ValueError, "bad locator.*detail"):
                geocode.find_address_candidates("test")

    def test_image_export_rejects_json_error_bytes(self):
        with patch("raleighlib.imagery.service_info", return_value={"capabilities": "Image"}), patch(
            "raleighlib.imagery.core.raw_request",
            return_value=b'{"error":{"message":"export failed"}}',
        ):
            with self.assertRaisesRegex(ValueError, "export failed"):
                imagery.export_image("https://maps.raleighnc.gov/x/ImageServer", (0, 0, 1, 1))

    def test_civic_requires_exact_public_status(self):
        for status in (None, 0, "0", "1"):
            attributes: dict[str, object] = {"title": "hidden"}
            if status is not None:
                attributes["status"] = status
            with self.subTest(status=status), patch(
                "raleighlib.civic.core.json_request",
                return_value={"data": [{"type": "node--news", "id": "x", "attributes": attributes}]},
            ):
                self.assertEqual(civic.fetch_news(limit=1), [])

    def test_hub_rejects_unknown_and_private_access(self):
        catalog = [
            {"id": "unknown", "title": "Unknown", "access": ""},
            {"id": "private", "title": "Private", "access": "private"},
        ]
        with self.assertRaises(hub.CatalogError):
            hub.resolve_item("private", catalog=catalog)
        self.assertEqual(hub.search_catalog("unknown", catalog=catalog), [])

    def test_development_nested_values_are_reduced_to_public_scalars(self):
        record = development._normalize_search_record({
            "CaseType": {"Name": "Building", "Email": "private@example.test"},
            "Address": {"FullAddress": "1 Main St", "Phone": "555-0100"},
        })
        self.assertEqual(record["RecordType"], "Building")
        self.assertEqual(record["Address"], "1 Main St")
        self.assertNotIn("private@example.test", json.dumps(record))
        self.assertNotIn("555-0100", json.dumps(record))

    def test_development_detail_and_inspection_drop_nested_contacts(self):
        record_id = "550e8400-e29b-41d4-a716-446655440000"
        permit_response = {"Result": {
            "PermitId": record_id,
            "PermitType": {"Name": "Building", "Email": "hidden@example.test"},
            "MainAddress": {"FullAddress": "1 Main St", "Phone": "555-0100"},
        }}
        with patch("raleighlib.development.core.json_request", return_value=permit_response):
            detail = development.permit_detail(record_id)
        self.assertEqual(detail["PermitType"], "Building")
        self.assertNotIn("hidden@example.test", json.dumps(detail))
        self.assertNotIn("555-0100", json.dumps(detail))

        inspection_response = {"Result": [{
            "InspectionId": "i1",
            "PrimaryInspector": {"Name": "Inspector", "Email": "hidden@example.test"},
        }]}
        with patch("raleighlib.development.core.json_request", return_value=inspection_response):
            rows = development.inspections_for_record(record_id)
        self.assertEqual(rows[0]["PrimaryInspector"], "Inspector")
        self.assertNotIn("hidden@example.test", json.dumps(rows))

    def test_escribe_empty_page_before_total_fails_closed(self):
        listing = b'<div class="MeetingTypeContainer" MeetingType="Council"></div>'
        responses = [
            {"d": {"TotalCount": 2, "Meetings": [{"Id": "one"}]}},
            {"d": {"TotalCount": 2, "Meetings": []}},
        ]
        with patch("raleighlib.meetings.core.raw_request", return_value=listing), patch(
            "raleighlib.meetings.core.json_request", side_effect=responses
        ):
            with self.assertRaisesRegex(meetings.CompatibilityError, "before TotalCount"):
                list(meetings._past_meeting_items(2025))

    def test_escribe_detail_ignores_unrelated_page_year(self):
        html = b'<footer>Copyright 2026</footer><time datetime="2025-10-14">meeting</time>'
        with patch("raleighlib.meetings.core.raw_request", return_value=html), patch(
            "raleighlib.meetings._find_past_meeting_record", return_value=None
        ) as lookup:
            meetings.meeting_detail("550e8400-e29b-41d4-a716-446655440000")
        lookup.assert_called_once_with("550e8400-e29b-41d4-a716-446655440000", 2025)

    def test_cli_rejects_invalid_numeric_domains(self):
        parser = cli_lib.build_parser()
        invalid = [
            ["--timeout", "0", "catalog"],
            ["query", "x", "--limit", "-1"],
            ["catalog", "--limit", "100001"],
            ["query", "x", "--offset", "-1"],
            ["reverse-geocode", "--lat", "nan", "--lon", "0"],
            ["imagery", "statistics", "x", "--bbox", "1,1,0,0"],
            ["events", "--from", "not-a-date"],
        ]
        for arguments in invalid:
            with self.subTest(arguments=arguments), self.assertRaises(SystemExit):
                parser.parse_args(arguments)


if __name__ == "__main__":
    unittest.main()
