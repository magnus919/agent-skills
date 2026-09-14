import json, tempfile, unittest
from pathlib import Path
import spring_ai_check

class SpringAICheckTests(unittest.TestCase):
    def make(self, pom, java="", props=""):
        d = Path(tempfile.mkdtemp()); (d / "pom.xml").write_text(pom)
        if java: p=d/"src/main/java/example/App.java"; p.parent.mkdir(parents=True); p.write_text(java)
        if props: p=d/"src/main/resources/application.properties"; p.parent.mkdir(parents=True); p.write_text(props)
        return d
    def test_json_clean_fixture(self):
        d=self.make('<properties><spring-ai.version>2.0.1</spring-ai.version><java.version>21</java.version></properties>', 'class App { ChatClient c; }', 'spring.ai.chat.client.observations.log-prompt=false')
        r=spring_ai_check.check(d); self.assertEqual(r['status'],'ok'); self.assertEqual(r['facts']['spring_ai_versions'],['2.0.1'])
    def test_memory_id_finding(self):
        d=self.make('<project/>','class App { ChatMemory memory; }'); r=spring_ai_check.check(d); self.assertIn('MEMORY_CONVERSATION_ID_MISSING',[f['code'] for f in r['findings']])
    def test_secret_and_logging_findings(self):
        d=self.make('<project/>',props='spring.ai.openai.api-key=abc\nspring.ai.chat.client.observations.log-prompt=true'); r=spring_ai_check.check(d); codes=[f['code'] for f in r['findings']]; self.assertIn('PROVIDER_SECRET_LITERAL',codes); self.assertIn('PROMPT_LOGGING_ENABLED',codes)
    def test_retrieval_and_tools_boundaries(self):
        d=self.make('<project/>','class App { VectorStore v; ToolCallback t; }'); r=spring_ai_check.check(d); codes=[f['code'] for f in r['findings']]; self.assertIn('RETRIEVAL_AUTH_UNCLEAR',codes); self.assertIn('TOOL_AUTH_BOUNDARY_UNCLEAR',codes)
    def test_invalid_root_json_exit(self):
        import contextlib, io
        out=io.StringIO()
        with contextlib.redirect_stdout(out): code=spring_ai_check.main(['--root','/does/not/exist','--json'])
        self.assertEqual(code,2); self.assertEqual(json.loads(out.getvalue())['status'],'invalid')

if __name__ == '__main__': unittest.main()
