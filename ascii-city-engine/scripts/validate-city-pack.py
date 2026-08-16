#!/usr/bin/env python3
"""Validate an ASCII city pack using only the Python standard library."""
from __future__ import annotations

import json
import math
import re
import sys
from datetime import date
from pathlib import Path

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")

# Resource caps: bound CPU/memory spent on any single pack so a crafted or
# corrupt pack cannot trigger unbounded work in the O(n^2) geometry checks.
MAX_POLYGON_VERTICES = 2000      # per building footprint or surface geometry
MAX_ELEVATION_CELLS = 4_000_000  # per terrain grid (e.g. 2000x2000)
MAX_FEATURES_PER_TILE = 100_000  # buildings + surfaces + props combined

# Documented per-kind prop glyph map (city-provider-contract.md). One glyph per kind.
PROP_GLYPHS = {"traffic_signal": "T", "street_lamp": "i", "tree": "t", "bus_stop": "B",
               "bench": "b", "bollard": "o", "fire_hydrant": "f", "crossing": "="}
FALLBACK_GLYPH = "?"

class Report:
    def __init__(self): self.passed = 0; self.failed = 0
    def rule(self, name, ok, detail=""):
        self.passed += bool(ok); self.failed += not ok
        suffix = f" — {detail}" if detail else ""
        print(f"{'PASS' if ok else 'FAIL'} {name}{suffix}")

def load_json(path, report, label):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        report.rule(label, True, str(path))
        return data
    except Exception as exc:
        report.rule(label, False, f"{path}: {exc}")
        return None

def valid_date(value):
    if not isinstance(value, str) or not DATE_RE.fullmatch(value): return False
    try: date.fromisoformat(value); return True
    except ValueError: return False

def finite_number(value): return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
def point(value): return isinstance(value, list) and len(value) == 2 and all(finite_number(v) for v in value)
def orient(a,b,c): return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def on_segment(a,b,p): return min(a[0],b[0]) <= p[0] <= max(a[0],b[0]) and min(a[1],b[1]) <= p[1] <= max(a[1],b[1])
def intersects(a,b,c,d):
    o1,o2,o3,o4 = orient(a,b,c),orient(a,b,d),orient(c,d,a),orient(c,d,b)
    if ((o1>0 and o2<0) or (o1<0 and o2>0)) and ((o3>0 and o4<0) or (o3<0 and o4>0)): return True
    return any(abs(o)<1e-9 and on_segment(x,y,p) for o,x,y,p in ((o1,a,b,c),(o2,a,b,d),(o3,c,d,a),(o4,c,d,b)))
def simple_polygon(poly):
    if not isinstance(poly,list) or len(poly)<3 or not all(point(p) for p in poly): return False
    if len(poly) > MAX_POLYGON_VERTICES: return False
    pts = poly[:-1] if poly[0] == poly[-1] else poly
    if len(pts)<3 or len({tuple(p) for p in pts})<3 or abs(sum(pts[i][0]*pts[(i+1)%len(pts)][1]-pts[(i+1)%len(pts)][0]*pts[i][1] for i in range(len(pts))))<1e-9: return False
    n=len(pts)
    for i in range(n):
        for j in range(i+1,n):
            if j in (i,(i+1)%n) or i in (j,(j+1)%n): continue
            if i==0 and j==n-1: continue
            if intersects(pts[i],pts[(i+1)%n],pts[j],pts[(j+1)%n]): return False
    return True

def valid_provenance(p, manifest=False):
    if not isinstance(p,dict): return False
    source_key = "name" if manifest else "source"
    required=(source_key,"url","license","retrieved")
    if not all(isinstance(p.get(k),str) and p[k] for k in required): return False
    if not p["url"].startswith("https://") or not valid_date(p["retrieved"]): return False
    if not manifest and not (finite_number(p.get("confidence")) and 0 <= p["confidence"] <= 1): return False
    if "confidence" in p and not (finite_number(p["confidence"]) and 0 <= p["confidence"] <= 1): return False
    return True

def inside(bounds,x,y): return bounds["min_x"] <= x <= bounds["max_x"] and bounds["min_y"] <= y <= bounds["max_y"]
def all_points(tile):
    for b in tile.get("buildings", []):
        if isinstance(b, dict):
            yield from b.get("footprint", [])
    for s in tile.get("surfaces", []):
        if isinstance(s, dict):
            yield from s.get("geometry", [])
    for p in (tile.get("props") or []):
        if isinstance(p, dict):
            yield [p.get("x"), p.get("y")]
    for g in (tile.get("signs") or []):
        if isinstance(g, dict):
            yield [g.get("x"), g.get("y")]

def main(argv):
    report=Report(); pack=Path(argv[1]).resolve() if len(argv)==2 else None
    report.rule("pack.directory", bool(pack and pack.is_dir()), str(pack) if pack else "usage: validate-city-pack.py <pack-dir>")
    if not pack or not pack.is_dir(): return 1
    root=Path(__file__).resolve().parents[1]
    ms=load_json(root/"templates/city-pack-manifest.schema.json",report,"schema.manifest.load")
    ws=load_json(root/"templates/world.schema.json",report,"schema.world.load")
    report.rule("schema.manifest.required-contract", bool(ms and set(("name","version","crs","bounds","tiles","provenance")) <= set(ms.get("required",[]))))
    report.rule("schema.world.required-contract", bool(ws and set(("terrain","buildings","surfaces","props")) <= set(ws.get("required",[]))))
    manifest=load_json(pack/"manifest.json",report,"manifest.parse")
    if not isinstance(manifest,dict): return 1
    required=("name","version","crs","bounds","tiles","provenance")
    report.rule("manifest.required", all(k in manifest for k in required), ", ".join(required))
    report.rule("manifest.identity", isinstance(manifest.get("name"),str) and bool(manifest["name"]) and isinstance(manifest.get("version"),str) and bool(re.fullmatch(r"\d+\.\d+\.\d+",manifest["version"])) and isinstance(manifest.get("crs"),str) and bool(manifest["crs"]))
    b=manifest.get("bounds")
    bounds_ok=isinstance(b,dict) and all(finite_number(b.get(k)) for k in ("min_x","min_y","max_x","max_y")) and b["min_x"]<b["max_x"] and b["min_y"]<b["max_y"]
    report.rule("manifest.bounds",bounds_ok)
    prov=manifest.get("provenance")
    report.rule("manifest.provenance",isinstance(prov,list) and bool(prov) and all(valid_provenance(p,True) for p in prov),"source URLs, licenses, ISO dates, confidence")
    tiles=manifest.get("tiles")
    report.rule("manifest.tiles.nonempty",isinstance(tiles,list) and bool(tiles) and all(isinstance(t,str) and t for t in tiles or []))
    if not isinstance(tiles,list): tiles=[]
    tile_data=[]
    for idx,rel in enumerate(tiles):
        safe=isinstance(rel,str) and not Path(rel).is_absolute()
        path=(pack/rel).resolve() if safe else pack
        safe=safe and (pack==path or pack in path.parents)
        report.rule(f"tile[{idx}].path",safe and path.is_file(),str(rel))
        data=load_json(path,report,f"tile[{idx}].parse") if safe and path.is_file() else None
        if isinstance(data,dict): tile_data.append((idx,rel,data))
    # pack-wide road-name set so a sign in one tile may reference a road whose
    # name-carrying surface lives in another tile (the contract supports multi-tile)
    pack_road_names=set()
    for _idx,_rel,_tile in tile_data:
        for _s in (_tile.get("surfaces",[]) if isinstance(_tile.get("surfaces"),list) else []):
            if isinstance(_s,dict) and isinstance(_s.get("name"),str) and _s.get("name"):
                pack_road_names.add(_s["name"])
    building_ids=[]; surface_ids=[]; building_count=0; surface_count=0; terrain_extents=[]
    for idx,rel,tile in tile_data:
        report.rule(f"tile[{idx}].required",all(k in tile for k in ("terrain","buildings","surfaces","props")),rel)
        n_b=len(tile.get("buildings",[])) if isinstance(tile.get("buildings"),list) else 0
        n_s=len(tile.get("surfaces",[])) if isinstance(tile.get("surfaces"),list) else 0
        n_p=len(tile.get("props",[])) if isinstance(tile.get("props"),list) else 0
        n_g=len(tile.get("signs",[])) if isinstance(tile.get("signs"),list) else 0
        total_features=n_b+n_s+n_p+n_g
        report.rule(f"tile[{idx}].feature-count",total_features<=MAX_FEATURES_PER_TILE,f"{total_features} features")
        if total_features>MAX_FEATURES_PER_TILE:
            # still collect IDs for pack-wide uniqueness even though we skip the
            # expensive per-feature geometry checks (so duplicates in an oversized
            # tile are not silently accepted)
            for _j,it in enumerate(tile.get("buildings",[]) if isinstance(tile.get("buildings"),list) else []):
                if isinstance(it,dict) and isinstance(it.get("id"),str): building_ids.append(it["id"])
            for _j,it in enumerate(tile.get("surfaces",[]) if isinstance(tile.get("surfaces"),list) else []):
                if isinstance(it,dict) and isinstance(it.get("id"),str): surface_ids.append(it["id"])
            continue  # short-circuit quadratic work below
        terrain=tile.get("terrain",{}); elev=terrain.get("elevations"); res=terrain.get("resolution_m"); origin=terrain.get("origin")
        rectangular=isinstance(elev,list) and len(elev)>=2 and all(isinstance(row,list) and len(row)>=2 for row in elev) and len({len(row) for row in elev})==1 and all(v is None or finite_number(v) for row in elev for v in row)
        cells=sum(len(row) for row in elev) if isinstance(elev,list) else 0
        report.rule(f"tile[{idx}].terrain.cells",cells<=MAX_ELEVATION_CELLS,f"{cells} cells")
        terrain_ok=finite_number(res) and res>0 and point(origin) and rectangular and cells<=MAX_ELEVATION_CELLS and valid_provenance(terrain.get("provenance"))
        report.rule(f"tile[{idx}].terrain",terrain_ok,"rectangular grid, meter resolution, provenance")
        if terrain_ok:
            ext=(origin[0],origin[1],origin[0]+(len(elev[0])-1)*res,origin[1]+(len(elev)-1)*res); terrain_extents.append(ext)
            report.rule(f"tile[{idx}].terrain.bounds",bool(bounds_ok and inside(b,ext[0],ext[1]) and inside(b,ext[2],ext[3])),str(ext))
        buildings=tile.get("buildings",[]); building_count += len(buildings) if isinstance(buildings,list) else 0
        b_ok=isinstance(buildings,list)
        for j,item in enumerate(buildings if isinstance(buildings,list) else []):
            ok=isinstance(item,dict) and isinstance(item.get("id"),str) and bool(item["id"]) and simple_polygon(item.get("footprint")) and finite_number(item.get("base_elev_m")) and finite_number(item.get("height_m")) and item["height_m"]>0 and isinstance(item.get("color"),str) and bool(COLOR_RE.fullmatch(item["color"])) and valid_provenance(item.get("provenance"))
            report.rule(f"tile[{idx}].building[{j}]",ok,item.get("id","missing id") if isinstance(item,dict) else "not object"); b_ok &= ok
            if isinstance(item,dict) and isinstance(item.get("id"),str): building_ids.append(item["id"])
        report.rule(f"tile[{idx}].buildings",b_ok,f"count={len(buildings) if isinstance(buildings,list) else 0}")
        surfaces=tile.get("surfaces",[]); surface_count += len(surfaces) if isinstance(surfaces,list) else 0
        s_ok=isinstance(surfaces,list)
        for j,item in enumerate(surfaces if isinstance(surfaces,list) else []):
            ok=isinstance(item,dict) and isinstance(item.get("id"),str) and bool(item["id"]) and isinstance(item.get("kind"),str) and bool(item["kind"]) and isinstance(item.get("walkable"),bool) and isinstance(item.get("geometry"),list) and 2<=len(item["geometry"])<=MAX_POLYGON_VERTICES and all(point(p) for p in item["geometry"]) and valid_provenance(item.get("provenance"))
            report.rule(f"tile[{idx}].surface[{j}]",ok,item.get("id","missing id") if isinstance(item,dict) else "not object"); s_ok &= ok
            if isinstance(item,dict) and isinstance(item.get("id"),str): surface_ids.append(item["id"])
        report.rule(f"tile[{idx}].surfaces",s_ok,f"count={len(surfaces) if isinstance(surfaces,list) else 0}")
        props=tile.get("props",[])
        p_ok=isinstance(props,list)
        for j,item in enumerate(props if isinstance(props,list) else []):
            ok=isinstance(item,dict) and isinstance(item.get("id"),str) and bool(item["id"]) and isinstance(item.get("kind"),str) and bool(item["kind"]) and finite_number(item.get("x")) and finite_number(item.get("y"))
            if ok and "provenance" in item: ok = ok and valid_provenance(item.get("provenance"))
            report.rule(f"tile[{idx}].prop[{j}]",ok,f"{item.get('kind','?')} ({item.get('id','?')})" if isinstance(item,dict) else "not object"); p_ok &= ok
        known=sorted({p["kind"] for p in (props if isinstance(props,list) else []) if isinstance(p,dict) and isinstance(p.get("kind"),str) and p["kind"] in PROP_GLYPHS})
        unknown=sorted({p["kind"] for p in (props if isinstance(props,list) else []) if isinstance(p,dict) and isinstance(p.get("kind"),str) and p["kind"] not in PROP_GLYPHS})
        report.rule(f"tile[{idx}].props",p_ok,f"count={len(props) if isinstance(props,list) else 0} kinds={len(known)}")
        # unknown kinds are permitted: the engine renders them with the documented
        # fallback glyph '?'. Report them (so a misspelled kind is visible) but do not
        # fail the pack on their presence.
        if unknown: report.rule(f"tile[{idx}].props.unknown-kinds",True,f"rendered with fallback '?': {', '.join(unknown)}")
        signs=tile.get("signs",[])
        g_ok=isinstance(signs,list)
        for j,item in enumerate(signs if isinstance(signs,list) else []):
            ok=isinstance(item,dict) and isinstance(item.get("id"),str) and bool(item["id"]) and isinstance(item.get("text"),str) and bool(item["text"]) and item["text"] in pack_road_names and finite_number(item.get("x")) and finite_number(item.get("y"))
            if ok and "provenance" in item: ok = ok and valid_provenance(item.get("provenance"))
            report.rule(f"tile[{idx}].sign[{j}]",ok,f"{item.get('text','?')} ({item.get('id','?')})" if isinstance(item,dict) else "not object"); g_ok &= ok
        # emit the signs rule unconditionally: a non-list/null signs value must FAIL,
        # matching how props is reported regardless of type
        signs_ok = isinstance(signs,list)
        if signs_ok: signs_ok = g_ok
        report.rule(f"tile[{idx}].signs",signs_ok,f"count={len(signs) if isinstance(signs,list) else 0}")
        extents_ok=bool(bounds_ok) and all(point(p) and inside(b,p[0],p[1]) for p in all_points(tile))
        report.rule(f"tile[{idx}].content.bounds",extents_ok,rel)
    from collections import Counter
    bc=Counter(building_ids); sc=Counter(surface_ids)
    duplicates=sorted(x for x,n in bc.items() if n>1)
    report.rule("buildings.unique-ids",not duplicates,", ".join(duplicates))
    surface_dupes=sorted(x for x,n in sc.items() if n>1)
    report.rule("surfaces.unique-ids",not surface_dupes,", ".join(surface_dupes))
    if isinstance(manifest.get("spawn"),dict) and bounds_ok:
        s=manifest["spawn"]; report.rule("manifest.spawn.bounds",finite_number(s.get("x")) and finite_number(s.get("y")) and finite_number(s.get("heading_deg")) and inside(b,s["x"],s["y"]))
    if terrain_extents:
        minx=min(e[0] for e in terrain_extents); miny=min(e[1] for e in terrain_extents); maxx=max(e[2] for e in terrain_extents); maxy=max(e[3] for e in terrain_extents)
        extent=f"[{minx:.1f}, {miny:.1f}]..[{maxx:.1f}, {maxy:.1f}]"
    else: extent="none"
    print(f"SUMMARY rules_passed={report.passed} rules_failed={report.failed} buildings={building_count} terrain_extent={extent} surfaces={surface_count}")
    return 0 if report.failed==0 else 1

if __name__ == "__main__": raise SystemExit(main(sys.argv))
