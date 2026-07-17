import importlib.machinery
import io
import json
import os
import pathlib
import unittest
from contextlib import redirect_stderr, redirect_stdout


SCRIPT = pathlib.Path(__file__).parents[1] / "scripts" / "linear"
cli = importlib.machinery.SourceFileLoader("linear_cli", str(SCRIPT)).load_module()


class LinearCliTests(unittest.TestCase):
    def run_cli(self, arguments):
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            try:
                cli.main(arguments)
            except SystemExit as exc:
                return exc.code, stdout.getvalue(), stderr.getvalue()
        return 0, stdout.getvalue(), stderr.getvalue()

    def test_document_reference_parsing(self):
        uuid = "123e4567-e89b-12d3-a456-426614174000"
        self.assertEqual(cli.parse_document_ref(uuid), ("id", uuid))
        self.assertEqual(cli.parse_document_ref("roadmap-q3"), ("slugId", "roadmap-q3"))
        self.assertEqual(
            cli.parse_document_ref(
                "https://linear.app/acme/document/my-roadmap-38359beef67c"
            ),
            ("slugId", "38359beef67c"),
        )

    def test_issue_and_document_queries_use_verified_fields(self):
        class Client:
            def run(self, query, variables):
                self.query, self.variables = query, variables
                return {"issue": {"id": "issue-id"}}

        client = Client()
        self.assertEqual(cli.resolve_issue(client, "ENG-42"), {"id": "issue-id"})
        self.assertIn("query Issue($id: String!)", client.query)
        self.assertIn("issue(id: $id)", client.query)
        self.assertNotIn("issueByIdentifier", client.query)

        class StateClient:
            def run(self, query, variables):
                self.query, self.variables = query, variables
                return {
                    "team": {
                        "states": {
                            "nodes": [
                                {"id": "state-id", "name": "Done", "type": "completed"}
                            ]
                        }
                    }
                }

        state_client = StateClient()
        self.assertEqual(
            cli.resolve_state(
                state_client, {"team": {"id": "team-id", "key": "ENG"}}, "Done"
            ),
            {"id": "state-id", "name": "Done", "type": "completed"},
        )
        self.assertIn(
            "query TeamStates($id: String!, $first: Int!)", state_client.query
        )
        self.assertIn("states(first: $first)", state_client.query)
        self.assertEqual(state_client.variables, {"id": "team-id", "first": 100})

        uuid = "123e4567-e89b-12d3-a456-426614174000"
        query, variables = cli.document_query(uuid)
        self.assertIn("query Document($ref: String!)", query)
        self.assertIn("document(id: $ref)", query)
        self.assertEqual(variables, {"ref": uuid})

        query, variables = cli.document_query(
            "https://linear.app/acme/document/my-roadmap-38359beef67c"
        )
        self.assertIn("documents(filter: { slugId: { eq: $ref } }, first: 1)", query)
        self.assertNotIn("documentBySlugId", query)
        self.assertEqual(variables, {"ref": "38359beef67c"})

    def test_issue_list_builds_team_and_state_filters_independently(self):
        class Client:
            def run(self, query, variables):
                self.query, self.variables = query, variables
                return {"issues": {"nodes": []}}

        client = Client()
        parser = cli.build_parser()
        args = parser.parse_args(
            cli.extract_globals(
                ["issue", "list", "--team", "ENG", "--state", "Started", "--json"]
            )
        )
        with redirect_stdout(io.StringIO()):
            cli.issue_list(client, args)

        self.assertIn("team: { key: { eq: $team } }", client.query)
        self.assertIn("state: { name: { eq: $state } }", client.query)
        self.assertEqual(
            client.variables, {"first": 10, "team": "ENG", "state": "Started"}
        )

    def test_issue_update_and_move_use_verified_id_variable_type(self):
        original = cli.Client.run
        queries = []

        def run(_self, query, variables):
            queries.append(query)
            if query.startswith("query Issue"):
                return {
                    "issue": {"id": "issue-id", "team": {"id": "team-id", "key": "ENG"}}
                }
            if query.startswith("query TeamStates"):
                return {
                    "team": {
                        "states": {
                            "nodes": [
                                {"id": "state-id", "name": "Done", "type": "completed"}
                            ]
                        }
                    }
                }
            return {"issueUpdate": {"success": True, "issue": {"id": "issue-id"}}}

        try:
            cli.Client.run = run
            update = self.run_cli(
                [
                    "issue",
                    "update",
                    "ENG-42",
                    "--title",
                    "Updated",
                    "--confirm",
                    "--json",
                ]
            )
            move = self.run_cli(
                ["issue", "move", "ENG-42", "--state", "Done", "--confirm", "--json"]
            )
        finally:
            cli.Client.run = original

        self.assertEqual(update[0], 0, update[2])
        self.assertEqual(move[0], 0, move[2])
        issue_update_queries = [
            query for query in queries if query.startswith("mutation IssueUpdate")
        ]
        self.assertEqual(len(issue_update_queries), 2)
        for query in issue_update_queries:
            self.assertIn(
                "mutation IssueUpdate($id: String!, $input: IssueUpdateInput!)", query
            )

    def test_document_get_emits_first_slug_match(self):
        original = cli.Client.run
        try:
            cli.Client.run = lambda _self, _query, _variables: {
                "documents": {"nodes": [{"id": "document-id"}]}
            }
            code, output, error = self.run_cli(
                [
                    "document",
                    "get",
                    "https://linear.app/acme/document/my-roadmap-38359beef67c",
                    "--json",
                ]
            )
        finally:
            cli.Client.run = original
        self.assertEqual(code, 0, error)
        self.assertEqual(json.loads(output), {"id": "document-id"})

    def test_document_get_emits_bare_slug_match(self):
        original = cli.Client.run
        try:
            cli.Client.run = lambda _self, _query, _variables: {
                "documents": {"nodes": [{"id": "document-id"}]}
            }
            code, output, error = self.run_cli(
                ["document", "get", "roadmap-q3", "--json"]
            )
        finally:
            cli.Client.run = original
        self.assertEqual(code, 0, error)
        self.assertEqual(json.loads(output), {"id": "document-id"})

    def test_missing_single_object_reads_fail(self):
        original = cli.Client.run
        try:
            cli.Client.run = lambda _self, _query, _variables: {
                "issue": None,
                "document": None,
                "documents": {"nodes": []},
                "cycle": None,
            }
            cases = (
                (["issue", "get", "ENG-42", "--detail", "--json"], "issue 'ENG-42'"),
                (
                    [
                        "document",
                        "get",
                        "123e4567-e89b-12d3-a456-426614174000",
                        "--json",
                    ],
                    "document '123e4567-e89b-12d3-a456-426614174000'",
                ),
                (["document", "get", "roadmap-q3", "--json"], "document 'roadmap-q3'"),
                (["cycle", "get", "cycle-id", "--json"], "cycle 'cycle-id'"),
            )
            for arguments, message in cases:
                with self.subTest(arguments=arguments):
                    code, output, error = self.run_cli(arguments)
                    self.assertEqual(code, 2)
                    self.assertEqual(output, "")
                    self.assertIn(message + " was not found", error)
        finally:
            cli.Client.run = original

    def test_documented_issue_create_and_move_forms_parse(self):
        parser = cli.build_parser()
        create = parser.parse_args(
            ["issue", "create", "--team", "ENG", "--title", "Ship it"]
        )
        move = parser.parse_args(["issue", "move", "ENG-42", "--state", "Done"])
        self.assertEqual(
            (create.noun, create.action, create.team, create.title),
            ("issue", "create", "ENG", "Ship it"),
        )
        self.assertEqual(
            (move.noun, move.action, move.issue, move.state),
            ("issue", "move", "ENG-42", "Done"),
        )

    def test_dry_run_needs_no_credentials_or_network(self):
        old_key, old_token = (
            os.environ.pop("LINEAR_API_KEY", None),
            os.environ.pop("LINEAR_ACCESS_TOKEN", None),
        )
        original = cli.urlopen
        try:

            def network_call(*_args, **_kwargs):
                raise AssertionError("dry-run made a network call")

            cli.urlopen = network_call
            code, output, error = self.run_cli(
                [
                    "issue",
                    "create",
                    "--team",
                    "ENG",
                    "--title",
                    "Preview",
                    "--dry-run",
                    "--json",
                ]
            )
        finally:
            cli.urlopen = original
            if old_key is not None:
                os.environ["LINEAR_API_KEY"] = old_key
            if old_token is not None:
                os.environ["LINEAR_ACCESS_TOKEN"] = old_token
        self.assertEqual(code, 0, error)
        self.assertTrue(json.loads(output)["dry_run"])

    def test_update_requires_a_field_before_network_or_confirmation(self):
        original = cli.urlopen
        try:
            cli.urlopen = lambda *_args, **_kwargs: self.fail(
                "invalid update made a network call"
            )
            code, output, error = self.run_cli(["issue", "update", "ENG-42", "--json"])
        finally:
            cli.urlopen = original
        self.assertEqual(code, 2)
        self.assertEqual(output, "")
        self.assertIn("at least one field", error)

    def test_is_mutation_rejects_query(self):
        self.assertFalse(cli.is_mutation("query { viewer { id } }"))

    def test_is_mutation_accepts_mutation(self):
        self.assertTrue(
            cli.is_mutation('mutation { issueArchive(id: "x") { success } }')
        )

    def test_is_mutation_strips_comments(self):
        self.assertTrue(
            cli.is_mutation('# comment\nmutation { issueArchive(id: "x") { success } }')
        )

    def test_is_mutation_finds_mutation_after_fragment(self):
        self.assertTrue(
            cli.is_mutation(
                'fragment F on Issue { id }\nmutation { issueArchive(id: "x") { success } }'
            )
        )

    def test_raw_with_comment_mutation_exits_confirm(self):
        code, _output, error = self.run_cli(
            ["raw", '# comment\nmutation { issueArchive(id: "x") { success } }']
        )
        self.assertEqual(code, 6)
        self.assertIn("--confirm", error)

    def test_project_and_cycle_parsers(self):
        parser = cli.build_parser()
        project_list = parser.parse_args(["project", "list", "--team", "ENG"])
        project_get = parser.parse_args(["project", "get", "Roadmap"])
        cycle_list = parser.parse_args(["cycle", "list", "--team", "ENG"])
        cycle_get = parser.parse_args(["cycle", "get", "cycle-id"])
        self.assertEqual(
            (project_list.noun, project_list.action, project_list.team),
            ("project", "list", "ENG"),
        )
        self.assertEqual(
            (project_get.noun, project_get.action, project_get.project),
            ("project", "get", "Roadmap"),
        )
        self.assertEqual(
            (cycle_list.noun, cycle_list.action, cycle_list.team),
            ("cycle", "list", "ENG"),
        )
        self.assertEqual(
            (cycle_get.noun, cycle_get.action, cycle_get.cycle),
            ("cycle", "get", "cycle-id"),
        )

    def test_authorization_rejects_multiple_credentials(self):
        old_key, old_token = (
            os.environ.get("LINEAR_API_KEY"),
            os.environ.get("LINEAR_ACCESS_TOKEN"),
        )
        os.environ["LINEAR_API_KEY"] = "key-value"
        os.environ["LINEAR_ACCESS_TOKEN"] = "token-value"
        stderr = io.StringIO()
        try:
            with redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as exc:
                    cli.Client(None).authorization()
        finally:
            if old_key is None:
                os.environ.pop("LINEAR_API_KEY", None)
            else:
                os.environ["LINEAR_API_KEY"] = old_key
            if old_token is None:
                os.environ.pop("LINEAR_ACCESS_TOKEN", None)
            else:
                os.environ["LINEAR_ACCESS_TOKEN"] = old_token
        self.assertEqual(exc.exception.code, 3)
        self.assertIn("exactly one", stderr.getvalue())
        self.assertNotIn("key-value", stderr.getvalue())
        self.assertNotIn("token-value", stderr.getvalue())

    def test_project_and_cycle_queries_use_verified_contracts(self):
        self.assertEqual(
            cli.PROJECT_FIELDS,
            "id name description status { id name type } progress teams(first: 10) { nodes { id name key } } url",
        )
        self.assertEqual(
            cli.CYCLE_FIELDS,
            "id number name description startsAt endsAt progress team { id name key }",
        )

        class Client:
            def run(self, query, variables):
                self.query, self.variables = query, variables
                return {"projects": {"nodes": []}}

        client = Client()
        args = cli.build_parser().parse_args(
            ["--json", "project", "list", "--team", "ENG"]
        )
        with redirect_stdout(io.StringIO()):
            cli.project_list(client, args)
        self.assertIn("accessibleTeams: { some: { key: { eq: $team } } }", client.query)
        self.assertNotIn("filter: { team:", client.query)
        self.assertEqual(client.variables, {"first": 10, "team": "ENG"})

    def test_resolve_project_uses_direct_id_and_exact_name_queries(self):
        project_id = "123e4567-e89b-12d3-a456-426614174000"

        class IdClient:
            def run(self, query, variables):
                self.query, self.variables = query, variables
                return {"project": {"id": project_id}}

        id_client = IdClient()
        self.assertEqual(cli.resolve_project(id_client, project_id), {"id": project_id})
        self.assertIn("query Project($id: String!)", id_client.query)
        self.assertIn("project(id: $id)", id_client.query)
        self.assertEqual(id_client.variables, {"id": project_id})

        class NameClient:
            def run(self, query, variables):
                self.query, self.variables = query, variables
                return {
                    "projects": {"nodes": [{"id": "project-id", "name": "Roadmap"}]}
                }

        name_client = NameClient()
        self.assertEqual(
            cli.resolve_project(name_client, "Roadmap"),
            {"id": "project-id", "name": "Roadmap"},
        )
        self.assertIn(
            "projects(first: 2, filter: { name: { eq: $name } })", name_client.query
        )
        self.assertEqual(name_client.variables, {"name": "Roadmap"})

    def test_leaf_help_includes_examples(self):
        paths = [
            ["whoami"],
            ["raw"],
            ["team", "list"],
            *(
                ["issue", action]
                for action in (
                    "list",
                    "search",
                    "get",
                    "create",
                    "update",
                    "move",
                    "comment",
                )
            ),
            *(["document", action] for action in ("list", "search", "get")),
            *(
                [noun, action]
                for noun in ("project", "cycle")
                for action in ("list", "get")
            ),
        ]
        for path in paths:
            with self.subTest(path=path):
                code, output, error = self.run_cli(path + ["--help"])
                self.assertEqual(code, 0, error)
                self.assertIn("Example:", output)
                self.assertIn("--json", output)
                self.assertIn("--dry-run", output)
                self.assertIn("--limit LIMIT", output)
                self.assertIn("1-100", output)

    def test_update_and_comment_dry_runs_include_requested_intent(self):
        code, output, error = self.run_cli(
            [
                "issue",
                "update",
                "ENG-42",
                "--title",
                "Updated",
                "--priority",
                "high",
                "--dry-run",
                "--json",
            ]
        )
        self.assertEqual(code, 0, error)
        update = json.loads(output)["operations"][-1]
        self.assertEqual(
            update,
            {
                "operation": "issueUpdate",
                "issue": "ENG-42",
                "input": {"title": "Updated", "priority": "high"},
            },
        )

        code, output, error = self.run_cli(
            [
                "issue",
                "comment",
                "ENG-42",
                "--body",
                "Ready for review",
                "--dry-run",
                "--json",
            ]
        )
        self.assertEqual(code, 0, error)
        self.assertEqual(
            json.loads(output)["operations"][-1],
            {
                "operation": "commentCreate",
                "issue": "ENG-42",
                "body": "Ready for review",
            },
        )

    def test_issue_detail_dry_run_includes_detail_intent(self):
        code, output, error = self.run_cli(
            ["issue", "get", "ENG-42", "--detail", "--dry-run", "--json"]
        )
        self.assertEqual(code, 0, error)
        self.assertEqual(
            json.loads(output)["operations"],
            [{"operation": "resolve issue", "reference": "ENG-42", "detail": True}],
        )

    def test_extract_globals_moves_flags_and_requires_limit_value(self):
        self.assertEqual(
            cli.extract_globals(
                [
                    "issue",
                    "list",
                    "--json",
                    "--team",
                    "ENG",
                    "--dry-run",
                    "--limit",
                    "20",
                ]
            ),
            ["--json", "--dry-run", "--limit", "20", "issue", "list", "--team", "ENG"],
        )
        with redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as exc:
                cli.extract_globals(["issue", "list", "--limit"])
        self.assertEqual(exc.exception.code, 2)

    def test_validate_limit_boundaries(self):
        for limit in (1, 100):
            with self.subTest(limit=limit):
                cli.validate_limit(type("Args", (), {"limit": limit})())
        for limit in (0, 101):
            with self.subTest(limit=limit):
                with redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit) as exc:
                        cli.validate_limit(type("Args", (), {"limit": limit})())
                self.assertEqual(exc.exception.code, 2)

    def test_resolve_team_matches_key_or_name_and_rejects_ambiguity(self):
        class Client:
            def __init__(self, teams):
                self.teams = teams

            def run(self, _query, _variables):
                return {"teams": {"nodes": self.teams}}

        teams = [
            {"id": "eng", "key": "ENG", "name": "Engineering"},
            {"id": "ops", "key": "OPS", "name": "Operations"},
        ]
        self.assertEqual(cli.resolve_team(Client(teams), "eng")["id"], "eng")
        self.assertEqual(cli.resolve_team(Client(teams), "engineering")["id"], "eng")
        for team, candidates in (
            ("missing", teams),
            (
                "engineering",
                teams + [{"id": "platform", "key": "PLAT", "name": "Engineering"}],
            ),
        ):
            with self.subTest(team=team):
                with redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit) as exc:
                        cli.resolve_team(Client(candidates), team)
                self.assertEqual(exc.exception.code, 2)

    def test_issue_create_resolves_team_before_mutation(self):
        original = cli.Client.run
        calls = []

        def run(_self, query, variables):
            calls.append((query, variables))
            if query.startswith("query ResolveTeam"):
                return {
                    "teams": {
                        "nodes": [
                            {"id": "team-id", "key": "ENG", "name": "Engineering"}
                        ]
                    }
                }
            return {"issueCreate": {"success": True, "issue": {"id": "issue-id"}}}

        try:
            cli.Client.run = run
            code, _output, error = self.run_cli(
                [
                    "issue",
                    "create",
                    "--team",
                    "Engineering",
                    "--title",
                    "Ship it",
                    "--confirm",
                    "--json",
                ]
            )
        finally:
            cli.Client.run = original
        self.assertEqual(code, 0, error)
        self.assertEqual(calls[-1][1]["input"]["teamId"], "team-id")

    def test_resolve_state_reports_available_names(self):
        class Client:
            def run(self, _query, _variables):
                return {
                    "team": {
                        "states": {
                            "nodes": [
                                {"id": "todo", "name": "Todo", "type": "backlog"},
                                {"id": "done", "name": "Done", "type": "completed"},
                            ]
                        }
                    }
                }

        stderr = io.StringIO()
        with redirect_stderr(stderr):
            with self.assertRaises(SystemExit):
                cli.resolve_state(
                    Client(), {"team": {"id": "team-id", "key": "ENG"}}, "Missing"
                )
        self.assertIn("available states: Todo, Done", stderr.getvalue())

    def test_json_separates_stderr(self):
        code, output, error = self.run_cli(
            ["raw", "query { viewer { id } }", "--variables", "[]", "--json"]
        )
        self.assertEqual(code, 2)
        self.assertEqual(output, "")
        self.assertIn("--variables must be a JSON object", error)

    def test_graphql_errors_with_http_200(self):
        original = cli.Client.run
        try:
            cli.Client.run = lambda self, _query, _variables=None: self.handle_response(
                {"errors": [{"message": "test"}]}
            )
            code, output, error = self.run_cli(["whoami", "--json"])
        finally:
            cli.Client.run = original
        self.assertEqual(code, 5)
        self.assertEqual(output, "")
        self.assertIn("GraphQL error: test", error)


if __name__ == "__main__":
    unittest.main()
