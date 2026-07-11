import importlib.machinery
import io
import json
import pathlib
import unittest
from contextlib import redirect_stderr, redirect_stdout

SCRIPT = pathlib.Path(__file__).parents[1] / "scripts" / "forgejo-cli"
cli = importlib.machinery.SourceFileLoader("forgejo_cli", str(SCRIPT)).load_module()


class CliTests(unittest.TestCase):
    def run_cli(self, args):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            try:
                cli.main(args)
            except SystemExit as exc:
                return exc.code, out.getvalue(), err.getvalue()
        return 0, out.getvalue(), err.getvalue()

    def plan(self, args):
        code, out, err = self.run_cli(["--dry-run", "--json"] + args)
        self.assertEqual(code, 0, err)
        return json.loads(out)

    def test_help_needs_no_credentials(self):
        self.assertEqual(self.run_cli(["--help"])[0], 0)
        self.assertEqual(self.run_cli(["issue", "--help"])[0], 0)

    def test_issue_create_plan(self):
        plan = self.plan(["issue", "create", "--owner", "me", "--repo", "x", "--title", "hello"])
        self.assertEqual((plan["method"], plan["path"]), ("POST", "/api/v1/repos/me/x/issues"))
        self.assertEqual(plan["body"]["title"], "hello")

    def test_mutation_requires_force(self):
        code, _, err = self.run_cli(["repo", "create", "--name", "x"])
        self.assertNotEqual(code, 0)
        self.assertIn("mutation", err)

    def test_api_path_guard_and_plan(self):
        self.assertNotEqual(self.run_cli(["api", "--method", "GET", "--path", "/bad"])[0], 0)
        plan = self.plan(["api", "--method", "PATCH", "--path", "/api/v1/user/settings", "--query", "theme=dark", "--data", '{"language":"en"}'])
        self.assertEqual(plan["query"], {"theme": "dark"})
        self.assertEqual(plan["body"], {"language": "en"})

    def test_representative_groups(self):
        cases = [
            (["pr", "create", "--owner", "me", "--repo", "x", "--title", "t", "--head", "h", "--base", "main"], "POST", "/api/v1/repos/me/x/pulls"),
            (["release", "create", "--owner", "me", "--repo", "x", "--tag-name", "v2"], "POST", "/api/v1/repos/me/x/releases"),
            (["content", "update", "--owner", "me", "--repo", "x", "--path", "a b.txt", "--content", "eA==", "--sha", "abc"], "PUT", "/api/v1/repos/me/x/contents/a%20b.txt"),
            (["hook", "create", "--owner", "me", "--repo", "x", "--url", "https://hook"], "POST", "/api/v1/repos/me/x/hooks"),
        ]
        for args, method, path in cases:
            plan = self.plan(args)
            self.assertEqual((plan["method"], plan["path"]), (method, path))

    def test_repo_creation_needs_no_owner(self):
        self.assertEqual(self.plan(["repo", "create", "--name", "demo", "--private"])["path"], "/api/v1/user/repos")


if __name__ == "__main__":
    unittest.main()
