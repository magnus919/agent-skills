"""Offline safety/contract tests; optional Node test exercises browser callbacks."""

import importlib.util
import json
import shutil
import subprocess
import unittest
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("cryptpad_probe", ROOT / "scripts/cryptpad.py")
cp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cp)


class CryptPadTests(unittest.TestCase):
    def test_upstream_wrappers(self):
        for wrapper in ("define(function(){;\nreturn %s;\n});", "define(function (){return %s;});"):
            self.assertEqual(
                cp.parse_config(wrapper % '{"enableEmbedding":true}'), {"enableEmbedding": True}
            )

    def test_no_executable_config(self):
        for body in (
            "<html>login</html>",
            "define(function(){return process.exit();});",
            'define(function(){return {"x":1};}); alert(1);',
        ):
            with self.assertRaises(ValueError):
                cp.parse_config(body)

    def test_probe_rejects_secret_and_remote_http_before_network(self):
        for url in (
            "https://host/pad/#secret",
            "https://user:pass@host",
            "https://host/?token=a",
            "http://example.com",
            "https://host/#x",
            "file:///tmp/x",
            "https://host:bad",
        ):
            with self.assertRaises(ValueError):
                cp.probe(url, 1, lambda *a: self.fail("Unexpected network"))

    def test_secret_redaction(self):
        result = cp.inspect_link(
            "https://example.com/pad/secret-path?token=secret-query#/2/pad/edit/secret-key/"
        )
        self.assertNotIn("secret", json.dumps(result))
        self.assertEqual(result["application"], "pad")
        self.assertEqual(result["network_requests"], 0)
        self.assertEqual(result["access_rights"], "not assessed")

    def test_probe_minimal_evidence(self):
        called = []

        def fake(url, timeout):
            called.append(url)
            if url.endswith("/api/config"):
                return 'define(function(){;return {"enableEmbedding":false,"adminKeys":["private-test"]};});'
            return "CryptPadAPI onSave onNewKey"

        result = cp.probe("https://example.com/", 1, fake)
        self.assertTrue(result["ok"])
        self.assertFalse(result["config"]["enableEmbedding"])
        self.assertNotIn("private-test", json.dumps(result))
        self.assertEqual(len(called), 2)

    def test_http_failure_and_html_are_incomplete(self):
        def fake(url, timeout):
            if url.endswith("config"):
                raise urllib.error.HTTPError(url, 403, "secret-message", {}, None)
            return "<html>CryptPad login</html>"

        result = cp.probe("https://example.com", 1, fake)
        self.assertFalse(result["ok"])
        self.assertNotIn("secret-message", json.dumps(result))
        self.assertEqual(result["endpoints"]["/api/config"]["code"], 403)

    def test_redirects_refused(self):
        self.assertIsNone(
            cp.NoRedirect().redirect_request(None, None, 302, "", {}, "https://other")
        )

    def test_cli_stdin_and_invalid_input(self):
        run = subprocess.run(
            [shutil.which("python3"), str(ROOT / "scripts/cryptpad.py"), "inspect-link"],
            input="https://host/code/#secret",
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(run.returncode, 0)
        self.assertNotIn("secret", run.stdout + run.stderr)
        bad = subprocess.run(
            [
                shutil.which("python3"),
                str(ROOT / "scripts/cryptpad.py"),
                "probe",
                "--origin",
                "https://user:secret@host",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(bad.returncode, 2)
        self.assertNotIn("secret", bad.stdout + bad.stderr)

    @unittest.skipUnless(shutil.which("node"), "Node.js required for callback contract test")
    def test_browser_adapter(self):
        script = r"""
import assert from 'node:assert/strict';
import {createEvents} from './templates/integration-adapter.mjs';
let saved = false, acknowledged = false, errors = [], unsaved;
let current = 'old', view;
const events = createEvents({
 persist: async () => {saved = true;},
 compareAndSwapKeys: async data => {
   if (current === data.old) {current = data.new; view = data.view;}
   return current;
 }, report: code => errors.push(code), setUnsaved: value => {unsaved = value;}
});
await events.onSave(new Blob(['data']), () => {assert.ok(saved); acknowledged = true;});
assert.ok(acknowledged);
let winners = [];
await Promise.all([
 events.onNewKey({old:'old',new:'alice',view:'alice-view'}, k => winners.push(k)),
 events.onNewKey({old:'old',new:'bob',view:'bob-view'}, k => winners.push(k))
]);
assert.deepEqual(winners, ['alice','alice']); assert.equal(view,'alice-view');
events.onHasUnsavedChanges(true); assert.equal(unsaved,true);
const broken = createEvents({persist: () => {throw Error('sensitive');},
 compareAndSwapKeys: async () => '', report: code => errors.push(code), setUnsaved: () => {}});
await broken.onSave(new Blob(), () => assert.fail('acknowledged failed save'));
await broken.onNewKey({}, () => assert.fail('accepted empty key'));
assert.deepEqual(errors, ['SAVE_FAILED','KEY_UPDATE_FAILED']);
"""
        subprocess.run(
            ["node", "--input-type=module", "-e", script], cwd=ROOT, check=True, capture_output=True
        )


if __name__ == "__main__":
    unittest.main()
