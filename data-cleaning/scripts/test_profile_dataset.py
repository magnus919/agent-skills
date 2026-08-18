#!/usr/bin/env python3
import csv, json, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).parent
SCRIPT=ROOT/"profile_dataset.py"
def run():
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/"sample.csv"; p.write_text("id,name,amount\n1,Alice,2.5\n1,Alice,2.5\n2,,bad\n",encoding="utf-8")
        out=subprocess.check_output([sys.executable,str(SCRIPT),str(p)],text=True); data=json.loads(out)
        assert data["rows_profiled"]==3 and data["duplicate_rows_in_profile"]==1
        assert data["fields"]["name"]["missing"]==1
        assert data["fields"]["amount"]["numeric_parse_fraction"]==2/3
if __name__=="__main__": run(); print("profile_dataset tests: PASS")
