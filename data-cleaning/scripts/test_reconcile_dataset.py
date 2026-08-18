#!/usr/bin/env python3
import json,subprocess,sys,tempfile
from pathlib import Path
SCRIPT=Path(__file__).with_name("reconcile_dataset.py")
def run():
 with tempfile.TemporaryDirectory() as d:
  a=Path(d)/"a.csv"; b=Path(d)/"b.csv"; a.write_text("id,amount\n001,2\n002,3\n"); b.write_text("id,amount\n001,2\n003,4\n")
  out=subprocess.check_output([sys.executable,str(SCRIPT),str(a),str(b),"--key","id","--sum","amount"],text=True); r=json.loads(out)
  assert r["missing_keys"]==1 and r["new_keys"]==1 and r["sums"]["amount"]["delta"]==1.0
if __name__=="__main__": run(); print("reconcile_dataset tests: PASS")
