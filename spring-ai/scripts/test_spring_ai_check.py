import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "spring_ai_check", Path(__file__).with_name("spring_ai_check.py")
)
spring_ai_check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(spring_ai_check)


class SpringAICheckTests(unittest.TestCase):
    def make(self, pom="", java="", props="", gradle=None, kotlin=None):
        directory = Path(tempfile.mkdtemp())
        if gradle is not None:
            (directory / "build.gradle").write_text(gradle)
        elif kotlin is not None:
            (directory / "build.gradle.kts").write_text(kotlin)
        else:
            (directory / "pom.xml").write_text(
                pom if pom.startswith("<project") else "<project>" + pom + "</project>"
            )
        if java:
            path = directory / "src/main/java/example/App.java"
            path.parent.mkdir(parents=True)
            path.write_text(java)
        if props:
            path = directory / "src/main/resources/application.properties"
            path.parent.mkdir(parents=True)
            path.write_text(props)
        return directory

    def test_shipped_fixture_is_parseable(self):
        project = Path(__file__).resolve().parents[1] / "examples/minimal-project"
        result = spring_ai_check.check(project)
        self.assertEqual(result["facts"]["spring_ai_versions"], ["2.0.1"])
        self.assertEqual(result["status"], "ok")

    def test_json_clean_fixture(self):
        project = self.make(
            '<properties><spring-ai.version>2.0.1</spring-ai.version>'
            '<java.version>21</java.version></properties>',
            "class App { ChatClient c; }",
            "spring.ai.chat.client.observations.log-prompt=false",
        )
        result = spring_ai_check.check(project)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["facts"]["spring_ai_versions"], ["2.0.1"])

    def test_realistic_gradle_notation(self):
        project = self.make(
            gradle='ext { springAiVersion = "2.0.1" }\n'
            'dependencies { implementation platform('
            '"org.springframework.ai:spring-ai-bom:${springAiVersion}") }'
        )
        self.assertEqual(
            spring_ai_check.check(project)["facts"]["spring_ai_versions"], ["2.0.1"]
        )

    def test_kotlin_and_maven_parent_versions(self):
        kotlin = self.make(
            kotlin='val springAiVersion = "2.0.1"\n'
            'dependencies { implementation(platform('
            '"org.springframework.ai:spring-ai-bom:$springAiVersion")) }'
        )
        self.assertEqual(
            spring_ai_check.check(kotlin)["facts"]["spring_ai_versions"], ["2.0.1"]
        )
        maven = self.make(
            "<parent><groupId>org.springframework.boot</groupId>"
            "<artifactId>spring-boot-starter-parent</artifactId>"
            "<version>3.5.0</version></parent>"
            "<dependencyManagement><dependency>"
            "<groupId>org.springframework.ai</groupId><artifactId>spring-ai-bom</artifactId>"
            "<version>2.0.1</version></dependency></dependencyManagement>"
        )
        facts = spring_ai_check.check(maven)["facts"]
        self.assertEqual(facts["spring_ai_versions"], ["2.0.1"])
        self.assertEqual(facts["spring_boot_versions"], ["3.5.0"])

    def test_maven_version_cannot_leak_from_adjacent_dependency(self):
        project = self.make(
            '<dependencyManagement><dependencies>'
            '<dependency><groupId>org.springframework.ai</groupId>'
            '<artifactId>spring-ai-bom</artifactId></dependency>'
            '<dependency><groupId>example</groupId><artifactId>other</artifactId>'
            '<version>9.8.7</version></dependency>'
            '</dependencies></dependencyManagement>'
        )
        result = spring_ai_check.check(project)
        self.assertEqual(result["facts"]["spring_ai_versions"], [])
        self.assertIn("SPRING_AI_VERSION_UNKNOWN", [x["code"] for x in result["findings"]])

    def test_namespaced_maven_version_precedes_artifact(self):
        project = self.make(
            '<project xmlns="http://maven.apache.org/POM/4.0.0">'
            '<dependencyManagement><dependencies><dependency>'
            '<version>2.0.1</version><artifactId>spring-ai-bom</artifactId>'
            '<groupId>org.springframework.ai</groupId>'
            '</dependency></dependencies></dependencyManagement></project>'
        )
        self.assertEqual(spring_ai_check.check(project)["facts"]["spring_ai_versions"], ["2.0.1"])

    def test_memory_id_reports_isolation_unproven(self):
        project = self.make("<project/>", "class App { ChatMemory memory; }")
        codes = [item["code"] for item in spring_ai_check.check(project)["findings"]]
        self.assertIn("MEMORY_CONVERSATION_ID_MISSING", codes)
        project = self.make(
            "<project/>",
            'class App { ChatMemory memory; String x = "CONVERSATION_ID"; }',
        )
        codes = [item["code"] for item in spring_ai_check.check(project)["findings"]]
        self.assertIn("MEMORY_ISOLATION_UNPROVEN", codes)

    def test_secret_and_logging_findings(self):
        project = self.make(
            "<project/>",
            props="spring.ai.openai.api-key=abc\n"
            "spring.ai.chat.client.observations.log-prompt=true",
        )
        codes = [item["code"] for item in spring_ai_check.check(project)["findings"]]
        self.assertIn("PROVIDER_SECRET_LITERAL", codes)
        self.assertIn("PROMPT_LOGGING_ENABLED", codes)

    def test_retrieval_and_tools_are_always_unverified(self):
        project = self.make(
            "<project/>",
            "class App { VectorStore v; ToolCallback t; boolean allow = true; }",
        )
        codes = [item["code"] for item in spring_ai_check.check(project)["findings"]]
        self.assertIn("RETRIEVAL_AUTH_UNVERIFIED", codes)
        self.assertIn("TOOL_AUTH_UNVERIFIED", codes)

    def test_comments_do_not_trigger_config_or_symbols(self):
        project = self.make(
            "<project/>",
            java="// ChatMemory and @Tool\nclass App {}",
            props="# spring.ai.chat.client.observations.log-prompt=true\n"
            "# spring.ai.openai.api-key=secret",
        )
        codes = [item["code"] for item in spring_ai_check.check(project)["findings"]]
        self.assertNotIn("PROMPT_LOGGING_ENABLED", codes)
        self.assertNotIn("PROVIDER_SECRET_LITERAL", codes)

    def test_java_block_comments_do_not_trigger_symbols_and_literals_survive(self):
        comments = (
            "/** ChatMemory, VectorStore, and @Tool are documented here. */\n"
            "/* .stream() and a fake key are also comments. */\n"
            "class App {}"
        )
        project = self.make("<project/>", comments)
        codes = [item["code"] for item in spring_ai_check.check(project)["findings"]]
        self.assertNotIn("MEMORY_CONVERSATION_ID_MISSING", codes)
        self.assertNotIn("RETRIEVAL_AUTH_UNVERIFIED", codes)
        self.assertNotIn("TOOL_AUTH_UNVERIFIED", codes)
        self.assertNotIn("STREAMING_STACK_UNCLEAR", codes)
        literal = 'class App { String literal = "/* ChatMemory */"; }'
        self.assertIn("ChatMemory", spring_ai_check.strip_java_comments(literal))

    def test_java_text_blocks_preserve_comment_looking_content(self):
        java = 'class App { String text = """hello " // ChatMemory\n/* VectorStore */\n"""; }'
        project = self.make("<project/>", java)
        result = spring_ai_check.check(project)
        codes = [item["code"] for item in result["findings"]]
        self.assertIn("MEMORY_CONVERSATION_ID_MISSING", codes)
        self.assertIn("RETRIEVAL_AUTH_UNVERIFIED", codes)

    def test_java_text_block_escaped_delimiter_stays_open(self):
        text = 'String text = """a \\\""" b // ChatMemory\nend""";'
        cleaned = spring_ai_check.strip_java_comments(text)
        self.assertIn("// ChatMemory", cleaned)
        self.assertEqual(cleaned, text)

    def test_unknown_and_secret_safe_errors(self):
        project = self.make(
            "<properties><spring-ai.version>${managed.version}</spring-ai.version></properties>",
            props="spring.ai.openai.api-key=super-secret",
        )
        result = spring_ai_check.check(project)
        codes = [item["code"] for item in result["findings"]]
        self.assertIn("SPRING_AI_VERSION_UNKNOWN", codes)
        self.assertNotIn("super-secret", json.dumps(result))

    def test_unsupported_project_is_invalid(self):
        with self.assertRaises(ValueError):
            spring_ai_check.check(Path(tempfile.mkdtemp()))

    def test_invalid_root_json_exit(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = spring_ai_check.main(["--root", "/does/not/exist", "--json"])
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(output.getvalue())["status"], "invalid")


if __name__ == "__main__":
    unittest.main()
