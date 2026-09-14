#!/usr/bin/env python3
"""Run the vendor-neutral ready/valid FPGA fixture without touching hardware."""
import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSET = ROOT / "assets"

def clean(value):
    if isinstance(value, bytes):
        return value.decode(errors="replace")
    return value or ""

def run(cmd, cwd, timeout=30):
    try:
        p = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, timeout=timeout)
        return {"command": cmd, "returncode": p.returncode, "stdout": clean(p.stdout), "stderr": clean(p.stderr), "status": "ok" if p.returncode == 0 else "failed"}
    except FileNotFoundError as e:
        return {"command": cmd, "returncode": None, "error": str(e), "stdout": "", "stderr": "", "status": "missing_tool"}
    except subprocess.TimeoutExpired as e:
        return {"command": cmd, "returncode": None, "error": "timeout", "stdout": clean(e.stdout), "stderr": clean(e.stderr), "status": "timeout"}

def version(tool, flag="--version"):
    if not tool:
        return {"status": "missing_tool"}
    return run([tool, flag], Path.cwd())

def source_hashes():
    result = {}
    for path in (ASSET / "rv_buffer.sv", ASSET / "tb_rv_buffer.sv"):
        result[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result

def yq(path):
    return '"' + str(path).replace('\\', '/') .replace('"', '\\"') + '"'

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--width", type=int, choices=(1, 8), nargs="+", default=[1, 8])
    ap.add_argument("--seed", type=int, default=20260914)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    out = (args.output.resolve() if args.output else Path(tempfile.mkdtemp(prefix="fpga-fixture-")))
    if args.output and out.exists() and (not out.is_dir() or any(out.iterdir())):
        ap.error(f"output directory must be new or empty: {out}")
    out.mkdir(parents=True, exist_ok=True)
    results = {"fixture": "rv_buffer", "hardware": False, "simulation": [], "synthesis": [], "output": str(out), "source_sha256": source_hashes()}
    iverilog = shutil.which("iverilog")
    vvp = shutil.which("vvp")
    yosys = shutil.which("yosys")
    for width in args.width:
        sim = out / f"sim_w{width}.vvp"
        if not iverilog or not vvp:
            results["simulation"].append({"width": width, "status": "skipped", "reason": "iverilog or vvp unavailable"})
        else:
            sim_versions = {"iverilog": version(iverilog, "-V"), "vvp": version(vvp, "-V")}
            compile_r = run([iverilog, "-g2012", "-s", "tb_rv_buffer", f"-Ptb_rv_buffer.DATA_WIDTH={width}", "-o", str(sim), str(ASSET / "rv_buffer.sv"), str(ASSET / "tb_rv_buffer.sv")], out)
            if compile_r["returncode"] == 0:
                exec_r = run([vvp, str(sim), f"+SEED={args.seed}"], out)
                ok = exec_r["returncode"] == 0 and "PASS" in exec_r.get("stdout", "") and "ERROR" not in exec_r.get("stdout", "") and "FAIL" not in exec_r.get("stdout", "")
                results["simulation"].append({"width": width, "status": "passed" if ok else "failed", "versions": sim_versions, "compile": compile_r, "run": exec_r})
            else:
                results["simulation"].append({"width": width, "status": "failed", "compile": compile_r})
        if not yosys:
            results["synthesis"].append({"width": width, "status": "skipped", "reason": "yosys unavailable"})
        else:
            ys = out / f"synth_w{width}.ys"
            netlist = out / f"synth_w{width}.json"
            ys.write_text(f"read_verilog -sv {yq(ASSET / 'rv_buffer.sv')}\nhierarchy -top rv_buffer -chparam DATA_WIDTH {width}\nproc; opt; check -assert; synth -top rv_buffer; check -assert; write_json {yq(netlist)}; stat\n")
            syn = run([yosys, str(ys)], out)
            results["synthesis"].append({"width": width, "status": "passed" if syn["returncode"] == 0 and netlist.exists() else "failed", "version": version(yosys), "run": syn, "netlist": str(netlist)})
    statuses = [x["status"] for x in results["simulation"] + results["synthesis"]]
    results["status"] = "passed" if statuses and all(x == "passed" for x in statuses) else ("incomplete" if statuses and all(x in ("passed", "skipped") for x in statuses) else "failed")
    payload = json.dumps(results, indent=2)
    if args.output:
        (out / "result.json").write_text(payload + "\n")
    print(payload if args.json else f"{results['status']}: simulation={[(x['width'], x['status']) for x in results['simulation']]} synthesis={[(x['width'], x['status']) for x in results['synthesis']]} output={out}")
    return 0 if results["status"] == "passed" else 1

if __name__ == "__main__":
    raise SystemExit(main())
