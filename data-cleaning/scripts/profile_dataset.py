#!/usr/bin/env python3
"""Dependency-free, read-only first-pass profiler for CSV/TSV/JSONL."""
import argparse, csv, hashlib, json, math, pathlib, sys
from collections import Counter

def load(path, delimiter=None, max_rows=None):
    p=pathlib.Path(path); raw=p.read_bytes(); digest=hashlib.sha256(raw).hexdigest()
    rows=[]
    if p.suffix.lower() in (".jsonl", ".ndjson"):
        for line in raw.decode("utf-8-sig").splitlines():
            if line.strip(): rows.append(json.loads(line))
            if max_rows and len(rows)>=max_rows: break
        headers=sorted({k for r in rows if isinstance(r,dict) for k in r})
        rows=[{h:r.get(h) for h in headers} for r in rows]
    else:
        text=raw.decode("utf-8-sig")
        sample=text[:8192]; dialect=csv.Sniffer().sniff(sample, delimiters=delimiter or ",\t;|")
        reader=csv.DictReader(text.splitlines(), dialect=dialect); headers=reader.fieldnames or []
        for r in reader:
            rows.append(r)
            if max_rows and len(rows)>=max_rows: break
    return p, digest, headers, rows

def profile(path, delimiter=None, max_rows=None):
    p,digest,headers,rows=load(path,delimiter,max_rows); cols={}
    for h in headers:
        vals=[r.get(h) for r in rows]; nonempty=[v for v in vals if v not in (None, "")]
        missing=sum(v in (None, "") for v in vals); distinct=Counter(str(v) for v in nonempty)
        nums=[]
        for v in nonempty:
            try: nums.append(float(str(v).strip()))
            except (ValueError,TypeError): pass
        cols[h]={"rows":len(vals),"missing":missing,"missing_fraction":(missing/len(vals) if vals else 0),"distinct":len(distinct),"top_values":distinct.most_common(5),"numeric_parse_fraction":(len(nums)/len(nonempty) if nonempty else 0),"min":min(nums) if nums else None,"max":max(nums) if nums else None}
    tuples=[tuple(r.get(h) for h in headers) for r in rows]; dup=sum(n-1 for n in Counter(tuples).values() if n>1)
    return {"file":str(p),"sha256":digest,"rows_profiled":len(rows),"sampled":bool(max_rows),"columns":headers,"duplicate_rows_in_profile":dup,"fields":cols}

def main():
    ap=argparse.ArgumentParser(description="Profile CSV, TSV, or JSONL without modifying input.")
    ap.add_argument("input"); ap.add_argument("--output",default="-"); ap.add_argument("--delimiter"); ap.add_argument("--max-rows",type=int)
    args=ap.parse_args()
    try: result=profile(args.input,args.delimiter,args.max_rows)
    except (OSError,UnicodeError,ValueError,json.JSONDecodeError) as e:
        print(f"Error: cannot profile input: {e}",file=sys.stderr); return 2
    text=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if args.output=="-": print(text,end="")
    else: pathlib.Path(args.output).write_text(text,encoding="utf-8")
    return 0
if __name__=="__main__": raise SystemExit(main())
