#!/usr/bin/env python3
"""Execute every canonical eval case with the deterministic fake adapter.

This checks runner plumbing and isolated output only. It deliberately does not
interpret fake responses as semantic grading evidence.
"""
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from eval_runner.fake_adapter import FakeAdapter
from eval_runner.models import AdapterInput, EvalCase, ExitStatus

def skills():
 out=subprocess.check_output(['git','ls-files','-z','**/SKILL.md'],cwd=ROOT).decode()
 return sorted(Path(x).parent for x in out.split('\0') if x and '/agent-council/profiles/skills/' not in x)
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--output-dir',required=True); args=ap.parse_args()
 out=Path(args.output_dir).resolve(); out.mkdir(parents=True,exist_ok=True)
 adapter=FakeAdapter(); records=[]; failures=[]
 for skill in skills():
  manifest=skill/'evals/evals.json'; data=json.loads(manifest.read_text())
  for raw in data['evals']:
   case=EvalCase(raw['id'],raw['prompt'],raw['expected_output'],raw['assertions'],raw.get('files',[]),raw.get('case_set','dev'))
   result=adapter.execute(AdapterInput(skill.resolve(),case,out,out,limits={'network_policy':'disabled'}))
   ok=result.exit_status is ExitStatus.COMPLETED
   records.append({'skill':str(skill),'case_id':case.id,'status':result.exit_status.value,'adapter':adapter.name,'adapter_version':adapter.version})
   if not ok: failures.append(f'{skill}:{case.id}')
 report={'runner':'all-canonical-fake-v1','adapter':adapter.name,'adapter_version':adapter.version,'semantic_grading':'not_performed','skill_count':len(skills()),'case_count':len(records),'failures':failures,'records':records}
 (out/'report.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
 print(json.dumps({k:report[k] for k in ('runner','adapter','skill_count','case_count','failures','semantic_grading')},indent=2))
 return 1 if failures else 0
if __name__=='__main__': raise SystemExit(main())
