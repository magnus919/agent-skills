#!/usr/bin/env python3
"""Deterministic tests for stripe/scripts/stripe-cli.

Runs the script as a subprocess so the tests exercise the real CLI surface
(--help, --json, --limit, mutation gate, exit codes, JSON payloads). A local
stdlib HTTP server stubs the Stripe API (balance, payment_intents,
subscriptions), so no external network or Stripe account is needed. Also
asserts the read-only-first contract: reads never call write methods, and the
mutation gate refuses to cancel a subscription without --dry-run or --yes.
"""
import json
import os
import subprocess
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "stripe-cli"

BALANCE = {"available": [{"amount": 250000, "currency": "usd"},
                          {"amount": 500, "currency": "jpy"}],
           "pending": [{"amount": 5000, "currency": "usd"},
                       {"amount": 1200, "currency": "jpy"}]}
PAYMENT = {"id": "pi_123", "amount": 4200, "currency": "usd", "status": "succeeded",
           "customer": "cus_1", "created": 1712345678}
PAYMENT_JPY = {"id": "pi_jpy", "amount": 500, "currency": "jpy", "status": "succeeded",
               "customer": "cus_2", "created": 1712345679}
SUBSCRIPTION = {"id": "sub_1", "status": "active", "customer": "cus_1",
                "current_period_end": 1712500000, "cancel_at_period_end": False,
                "items": {"data": [{"id": "si_1",
                                    "price": {"id": "price_1", "unit_amount": 9900,
                                              "currency": "usd",
                                              "recurring": {"interval": "month"}}},
                                    {"id": "si_jpy",
                                     "price": {"id": "price_jpy", "unit_amount": 500,
                                               "currency": "jpy",
                                               "recurring": {"interval": "month"}}}]}}


class StubStripeServer:
    """Minimal stub of the Stripe API surface used by stripe-cli."""

    def __init__(self):
        self.requests = []  # (method, path, form)
        handler = self._make_handler()
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def _make_handler(self):
        stub = self

        class Handler(BaseHTTPRequestHandler):
            def _read_form(self):
                length = int(self.headers.get("Content-Length", "0"))
                raw = self.rfile.read(length)
                import urllib.parse
                return {k: v for k, v in urllib.parse.parse_qsl(raw.decode("utf-8"))}

            def _json(self, payload, status=200):
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(payload).encode("utf-8"))

            def do_GET(self):  # noqa: N802
                stub.requests.append(("GET", self.path, None))
                if self.path == "/balance" or self.path.startswith("/balance?"):
                    self._json(BALANCE)
                elif "/payment_intents" in self.path:
                    self._json({"data": [PAYMENT, PAYMENT_JPY], "has_more": False})
                elif "/subscriptions" in self.path:
                    if self.path.rstrip("/") == "/subscriptions" or "?" in self.path:
                        self._json({"data": [SUBSCRIPTION], "has_more": False})
                    else:
                        self._json(SUBSCRIPTION)
                else:
                    self._json({"error": {"message": "not_found"}}, 404)

            def do_POST(self):  # noqa: N802
                form = self._read_form()
                stub.requests.append(("POST", self.path, form))
                if "/subscriptions/" in self.path:
                    canceled = json.loads(json.dumps(SUBSCRIPTION))
                    canceled["cancel_at_period_end"] = form.get("cancel_at_period_end") == "true"
                    self._json(canceled)
                else:
                    self._json({"error": {"message": "not_found"}}, 404)

            def log_message(self, *args):  # silence stderr
                pass

        return Handler

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *exc):
        self.server.shutdown()
        self.server.server_close()


def run_script(env, *args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        timeout=30,
        env=env,
    )


def base_env(stub):
    env = dict(os.environ)
    env["STRIPE_API_KEY"] = "sk_test_dummy"
    env["STRIPE_API_BASE"] = f"http://127.0.0.1:{stub.port}/"
    return env


def load_json(proc):
    return json.loads(proc.stdout)


class StripeCliTests(unittest.TestCase):
    def test_help_shows_readonly_surface_and_json(self):
        proc = run_script(dict(os.environ), "--help")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("--json", proc.stdout)
        self.assertIn("--limit", proc.stdout)
        for term in ("balance", "payment", "subscription"):
            self.assertIn(term, proc.stdout)

    def test_help_works_without_api_key(self):
        env = dict(os.environ)
        env.pop("STRIPE_API_KEY", None)
        proc = run_script(env, "balance", "show", "--help")
        self.assertEqual(proc.returncode, 0)

    def test_balance_read(self):
        with StubStripeServer() as stub:
            proc = run_script(base_env(stub), "--json", "balance", "show")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = load_json(proc)
        usd, jpy = data["balance"]["available"]
        self.assertEqual((usd["amount"], usd["amount_minor"], usd["currency"]),
                         ("2500.00", 250000, "USD"))
        self.assertEqual((jpy["amount"], jpy["amount_minor"], jpy["currency"]),
                         ("500", 500, "JPY"))

    def test_payments_list(self):
        with StubStripeServer() as stub:
            proc = run_script(base_env(stub), "--json", "--limit", "5", "payments", "list")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = load_json(proc)
        self.assertEqual(data["payments"][0]["id"], "pi_123")
        usd, jpy = data["payments"]
        self.assertEqual((usd["amount"], usd["amount_minor"], usd["currency"]),
                         ("42.00", 4200, "USD"))
        self.assertEqual((jpy["amount"], jpy["amount_minor"], jpy["currency"]),
                         ("500", 500, "JPY"))

    def test_payments_limit_is_bounded_in_request(self):
        with StubStripeServer() as stub:
            run_script(base_env(stub), "--json", "--limit", "3", "payments", "list")
        gets = [path for method, path, _ in stub.requests if method == "GET"]
        self.assertTrue(any("payment_intents" in path and "limit=3" in path for path in gets))

    def test_subscriptions_list(self):
        with StubStripeServer() as stub:
            proc = run_script(base_env(stub), "--json", "subscriptions", "list")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = load_json(proc)
        self.assertEqual(data["subscriptions"][0]["status"], "active")

    def test_subscriptions_get(self):
        with StubStripeServer() as stub:
            proc = run_script(base_env(stub), "--json", "subscriptions", "get", "--id", "sub_1")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = load_json(proc)
        self.assertEqual(data["subscription"]["id"], "sub_1")
        self.assertEqual(data["subscription"]["items"][0]["interval"], "month")
        usd, jpy = data["subscription"]["items"]
        self.assertEqual((usd["amount"], usd["unit_amount_minor"]), ("99.00", 9900))
        self.assertEqual((jpy["amount"], jpy["unit_amount_minor"], jpy["currency"]),
                         ("500", 500, "JPY"))

    def test_currency_special_cases_and_integer_formatting(self):
        import runpy
        formatter = runpy.run_path(str(SCRIPT))["format_stripe_amount"]
        self.assertEqual(formatter(123, "jpy"), "123")
        self.assertEqual(formatter(123, "usd"), "1.23")
        self.assertEqual(formatter(500, "ugx"), "500")
        self.assertEqual(formatter(500, "isk"), "5.00")
        self.assertEqual(formatter(500, "huf"), "5.00")
        self.assertEqual(formatter(500, "twd"), "5.00")
        self.assertEqual(formatter(-5, "usd"), "-0.05")

    def test_unsupported_three_decimal_presentment_currencies_are_rejected(self):
        import runpy
        namespace = runpy.run_path(str(SCRIPT))
        formatter = namespace["format_stripe_amount"]
        stripe_error = namespace["StripeError"]
        for currency in ("bhd", "jod", "kwd", "omr", "tnd"):
            with self.subTest(currency=currency), self.assertRaisesRegex(stripe_error, currency.upper()):
                formatter(1234, currency)

    def test_cancel_requires_confirmation(self):
        with StubStripeServer() as stub:
            proc = run_script(base_env(stub), "subscriptions", "cancel", "--id", "sub_1")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("refusing to cancel", proc.stderr)
        self.assertEqual(stub.requests, [], "no API call may be made without confirmation")

    def test_cancel_dry_run_does_not_post(self):
        with StubStripeServer() as stub:
            proc = run_script(base_env(stub), "--json", "subscriptions", "cancel",
                              "--id", "sub_1", "--dry-run")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = load_json(proc)
        self.assertTrue(data["dry_run"])
        self.assertEqual(stub.requests, [], "dry-run must not reach the API")

    def test_cancel_with_yes_posts_cancel_at_period_end(self):
        with StubStripeServer() as stub:
            proc = run_script(base_env(stub), "--json", "subscriptions", "cancel",
                              "--id", "sub_1", "--yes")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = load_json(proc)
        self.assertTrue(data["subscription"]["cancel_at_period_end"])
        posts = [form for method, path, form in stub.requests
                 if method == "POST" and "/subscriptions/sub_1" in path]
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0].get("cancel_at_period_end"), "true")

    def test_missing_api_key_errors_cleanly(self):
        env = dict(os.environ)
        env.pop("STRIPE_API_KEY", None)
        proc = run_script(env, "--json", "balance", "show")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("STRIPE_API_KEY", proc.stdout)

    def test_read_only_contract_no_write_opens(self):
        source = SCRIPT.read_text()
        writes = [line for line in source.splitlines()
                  if line.strip().startswith("open(") and ("'w'" in line or '"w"' in line)]
        self.assertEqual(writes, [], "script must never open files in write mode")


if __name__ == "__main__":
    unittest.main()
