"""Bounded browser integration test for the shipped pwrun scaffold.

Run after installing the project Playwright package and Chromium. The test
starts an ephemeral local HTTP server and confirms the server received the
browser request as well as that the JSON report recorded the reached URL.
"""

import json
import os
import signal
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from typing import Tuple

ROOT = Path(__file__).resolve().parents[1]
PWRUN = ROOT / "scripts" / "pwrun"
CONFIG_TEMPLATE = ROOT / "templates" / "playwright.config.ts"


def playwright_ready() -> bool:
    if not shutil.which("node") or not shutil.which("npx"):
        return False
    try:
        result = subprocess.run(
            [shutil.which("npx"), "--no-install", "playwright", "--version"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except subprocess.TimeoutExpired:
        return False
    cache = Path(os.environ.get("PLAYWRIGHT_BROWSERS_PATH", Path.home() / ".cache" / "ms-playwright"))
    chromium_installed = cache.is_dir() and any(entry.name.startswith("chromium-") for entry in cache.iterdir())
    return result.returncode == 0 and chromium_installed


def stop_process_group(process: subprocess.Popen) -> Tuple[str, str]:
    """Stop the smoke command and any webServer/browser children it started."""
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        return process.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        return process.communicate(timeout=5)


def wait_for_port_release(host: str, port: int, timeout: float = 5.0) -> bool:
    """Wait for the temporary webServer port to stop accepting connections."""
    deadline = time.monotonic() + timeout
    family = socket.AF_INET6 if ":" in host else socket.AF_INET
    while time.monotonic() < deadline:
        with socket.socket(family) as sock:
            sock.settimeout(0.2)
            if sock.connect_ex((host, port)) != 0:
                return True
        time.sleep(0.1)
    return False


@unittest.skipUnless(playwright_ready(), "requires local @playwright/test and an installed Chromium browser")
class ScaffoldNavigationIntegrationTests(unittest.TestCase):
    def test_pwrun_visits_requested_scaffold_target_and_reports_runtime_url(self):
        host = "::1"
        family = socket.AF_INET6
        try:
            sock = socket.socket(family)
            sock.bind((host, 0))
        except OSError:
            host = "127.0.0.1"
            family = socket.AF_INET
            sock = socket.socket(family)
            sock.bind((host, 0))
        with sock:
            port = sock.getsockname()[1]
        url_host = f"[{host}]" if ":" in host else host
        requested_url = f"http://{url_host}:{port}"

        with tempfile.TemporaryDirectory(prefix="pwrun-scaffold-", dir=ROOT) as tmp:
            project = Path(tmp)
            (project / "e2e").mkdir()
            (project / "playwright.config.ts").write_text(
                CONFIG_TEMPLATE.read_text(encoding="utf-8").replace(
                    "command: 'npm run dev'", "command: 'node server.mjs'"
                ),
                encoding="utf-8",
            )
            (project / "server.mjs").write_text(
                """import http from 'node:http';
import fs from 'node:fs';
http.createServer((request, response) => {
  fs.appendFileSync('server-requests.log', `${request.method} ${request.url}\\n`);
  response.writeHead(200, {'content-type': 'text/html'});
  response.end('<main><h1>Scaffold integration</h1></main>');
}).listen(Number(process.env.PORT), process.env.HOST);
""",
                encoding="utf-8",
            )
            (project / "e2e" / "navigation.spec.ts").write_text(
                """import { test, expect } from '@playwright/test';
test('visits configured target and records the reached URL', async ({ page }) => {
  await page.goto('/');
  test.info().annotations.push({ type: 'pwrun-navigation', description: page.url() });
  await expect(page.getByRole('heading', { name: 'Scaffold integration' })).toBeVisible();
});
""",
                encoding="utf-8",
            )
            env = os.environ.copy()
            env["PORT"] = str(port)
            env["HOST"] = host
            process = subprocess.Popen(
                [
                    sys.executable,
                    str(PWRUN),
                    "smoke",
                    "--json",
                    "--config",
                    str(project / "playwright.config.ts"),
                    "--spec",
                    "e2e/navigation.spec.ts",
                    "--url",
                    requested_url,
                    "--timeout",
                    "35",
                ],
                cwd=project,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                start_new_session=True,
            )
            timed_out = False
            stdout = ""
            stderr = ""
            try:
                try:
                    stdout, stderr = process.communicate(timeout=45)
                except subprocess.TimeoutExpired:
                    timed_out = True
            finally:
                cleanup_stdout, cleanup_stderr = stop_process_group(process)
                stdout = stdout or cleanup_stdout
                stderr = stderr or cleanup_stderr
                self.assertTrue(
                    wait_for_port_release(host, port),
                    f"temporary webServer still owns port {port}; stdout:\n{stdout}\nstderr:\n{stderr}",
                )
            if timed_out:
                self.fail(f"pwrun exceeded its 45 second bound; stdout:\n{stdout}\nstderr:\n{stderr}")
            result = subprocess.CompletedProcess(process.args, process.returncode, stdout, stderr)
            payload = json.loads(result.stdout)
            requests = (project / "server-requests.log").read_text(encoding="utf-8")

        self.assertEqual(result.returncode, 0, f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")
        self.assertEqual(payload["requested_url"], requested_url)
        self.assertTrue(payload["navigation_evidence"]["verified"])
        self.assertTrue(payload["navigation_evidence"]["requested_target_origin_observed"])
        self.assertTrue(any(item["url"] == f"{requested_url}/" for item in payload["navigation_evidence"]["observed"]))
        self.assertIn("GET /", requests)


if __name__ == "__main__":
    unittest.main()
