"""Bounded browser integration test for the shipped pwrun scaffold.

Run after installing the project Playwright package and Chromium. The test
starts an ephemeral local HTTP server and confirms the server received the
browser request as well as that the JSON report recorded the reached URL.
"""

import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

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


@unittest.skipUnless(playwright_ready(), "requires local @playwright/test and an installed Chromium browser")
class ScaffoldNavigationIntegrationTests(unittest.TestCase):
    def test_pwrun_visits_requested_scaffold_target_and_reports_runtime_url(self):
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        requested_url = f"http://127.0.0.1:{port}"

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
}).listen(Number(process.env.PORT), '127.0.0.1');
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
            result = subprocess.run(
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
                capture_output=True,
                text=True,
                timeout=45,
            )
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
