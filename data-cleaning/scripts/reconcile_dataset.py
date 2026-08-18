#!/usr/bin/env python3
"""Compare two CSV/TSV datasets by shape, key uniqueness, and aggregate columns."""
import argparse, csv, hashlib, json, pathlib, sys
from collections import Counter

def read(path, delimiter=None):
    raw=pathlib.Path(path).read_bytes(); text=raw.decode("utf-8-sig")
    if delimiter is None: delimiter=csv.Sniffer().sniff(text[:8192],delimiters=",\t;|").delimiter
    rows=list(csv.DictReader(text.splitlines(),delimiter=delimiter)); return rows, hashlib.sha256(raw).hexdigest()

def main():
    ap=argparse.ArgumentParser(description="Reconcile two delimited datasets without modifying them.")
    ap.add_argument("before"); ap.add_argument("after"); ap.add_argument("--key",action="append",required=True); ap.add_argument("--sum",dest="sums",action="append",default=[]); ap.add_argument("--output",default="-"); args=ap.parse_args()
    try: before,bh=read(args.before); after,ah=read(args.after)
    except (OSError,UnicodeError,ValueError) as e: print(f"Error: cannot read dataset: {e}",file=sys.stderr); return 2
    def keys(rows): return [tuple(r.get(k) for k in args.key) for r in rows]
    bk,ak=keys(before),keys(after); result={"before":{"rows":len(before),"sha256":bh,"duplicate_keys":sum(n-1 for n in Counter(bk).values() if n>1)},"after":{"rows":len(after),"sha256":ah,"duplicate_keys":sum(n-1 for n in Counter(ak).values() if n>1)},"key":args.key,"missing_keys":len(set(bk)-set(ak)),"new_keys":len(set(ak)-set(bk)),"sums":{}}
    for col in args.sums:
        def total(rows):
            return sum(float(r[col]) for r in rows if r.get(col) not in (None,""))
        try: result["sums"][col]={"before":total(before),"after":total(after),"delta":total(after)-total(before)}
        except (KeyError,ValueError) as e: print(f"Error: cannot sum {col}: {e}",file=sys.stderr); return 2
    text=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if args.output=="-": print(text,end="")
    else: pathlib.Path(args.output).write_text(text,encoding="utf-8")
    return 0
if __name__=="__main__": raise SystemExit(main())
