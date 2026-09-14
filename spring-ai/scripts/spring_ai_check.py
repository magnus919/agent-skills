#!/usr/bin/env python3
"""Offline, read-only diagnostics for Maven/Gradle Spring AI projects."""
import argparse, json, re, sys
from pathlib import Path

VERSION_RE = re.compile(r"(?:spring-ai\.version\s*[<>=:]\s*|spring-ai-bom[^\n]{0,180}?<version>)[\"']?([0-9]+\.[0-9]+(?:\.[0-9]+)?(?:-[A-Za-z0-9.-]+)?)", re.I)
BOOT_RE = re.compile(r"(?:spring-boot\.version\s*[<>=:]\s*|spring-boot-dependencies[^\n]{0,180}?<version>)[\"']?([0-9]+\.[0-9]+(?:\.[0-9]+)?)", re.I)
JAVA_RE = re.compile(r"(?:java\.version\s*[<>=:]\s*|sourceCompatibility\s*[=:]\s*|JavaLanguageVersion\.of\()\s*[\"']?(\d+)", re.I)

def finding(code, severity, message, paths, evidence):
    return {"code": code, "severity": severity, "message": message, "paths": paths, "evidence": evidence}

def read(path):
    try: return path.read_text(encoding="utf-8")
    except UnicodeDecodeError: return ""
    except OSError as exc: raise RuntimeError(f"cannot read {path}: {exc}")

def check(root):
    files = [p for p in (root / "pom.xml", root / "build.gradle", root / "build.gradle.kts", root / "gradle.properties") if p.exists()]
    if not files: raise ValueError("no pom.xml, build.gradle, build.gradle.kts, or gradle.properties found")
    cfg = []
    for base in (root / "src/main/resources", root / "src/test/resources"):
        for name in ("application.properties", "application.yml", "application.yaml"):
            p = base / name
            if p.exists(): cfg.append((p, read(p)))
    build_text = "\n".join(read(p) for p in files)
    versions = sorted(set(VERSION_RE.findall(build_text)))
    boots = sorted(set(BOOT_RE.findall(build_text)))
    java = sorted(set(JAVA_RE.findall(build_text)))
    source_files = [p for d in (root / "src/main/java", root / "src/test/java") if d.exists() for p in d.rglob("*.java")]
    source = [(p, read(p)) for p in source_files]
    findings = []
    def paths(ps): return [str(p.relative_to(root)) for p in ps]
    alltexts = [(p,t) for p,t in cfg + source]
    props = "\n".join(t for _,t in cfg)
    text = "\n".join(t for _,t in alltexts)
    if not versions: findings.append(finding("SPRING_AI_VERSION_MISSING", "warning", "No Spring AI BOM or version property detected; verify dependency management before upgrades.", [str(p.relative_to(root)) for p in files], "dependency files inspected"))
    if "ChatMemory" in text and "CONVERSATION_ID" not in text: findings.append(finding("MEMORY_CONVERSATION_ID_MISSING", "error", "Chat memory symbols are present but no explicit conversation ID parameter was found.", paths([p for p,t in source if "ChatMemory" in t]), "search for ChatMemory and CONVERSATION_ID"))
    if ("stream()" in text or ".stream(" in text) and not re.search(r"spring-boot-starter-webflux|spring-ai-starter-model", build_text): findings.append(finding("STREAMING_STACK_UNCLEAR", "warning", "Streaming code was found but no reactive web starter was detected; verify the runtime stack for the selected Spring AI line.", paths(files), "stream() symbol and dependency scan"))
    if re.search(r"log-prompt\s*[:=]\s*true|log-completion\s*[:=]\s*true", props, re.I): findings.append(finding("PROMPT_LOGGING_ENABLED", "error", "Prompt or completion logging is enabled; review redaction, access, retention, and rollback before use.", paths([p for p,t in cfg if re.search(r"log-prompt\s*[:=]\s*true|log-completion\s*[:=]\s*true", t, re.I)]), "configuration value is true"))
    if re.search(r"spring\.ai\.[^\n]*(?:api-key|apiKey)\s*[:=]\s*[^$\s][^\n]*", props, re.I): findings.append(finding("PROVIDER_SECRET_LITERAL", "error", "A provider credential appears to be literal configuration; move it to an environment or secret reference.", paths([p for p,t in cfg]), "key value is not an environment placeholder"))
    if "QuestionAnswerAdvisor" in text or "RetrievalAugmentationAdvisor" in text or "VectorStore" in text:
        if not re.search(r"(?:authorization|permission|tenant|owner|acl|access)", text, re.I): findings.append(finding("RETRIEVAL_AUTH_UNCLEAR", "warning", "Retrieval symbols are present but no authorization/ownership check was found in inspected source; verify filtering before prompt construction.", paths([p for p,t in source if re.search(r"QuestionAnswerAdvisor|RetrievalAugmentationAdvisor|VectorStore", t)]), "retrieval symbols and authorization terms"))
    if re.search(r"\.tools\(|@Tool|ToolCallback|Mcp", text):
        if not re.search(r"(?:authorize|authorization|permission|allow|deny|policy|timeout)", text, re.I): findings.append(finding("TOOL_AUTH_BOUNDARY_UNCLEAR", "warning", "Tool or MCP integration was found without an obvious authorization or timeout boundary; inspect execution before enabling side effects.", paths([p for p,t in source if re.search(r"\.tools\(|@Tool|ToolCallback|Mcp", t)]), "tool symbols and boundary terms"))
    if "stream()" in text and re.search(r"save|persist|commit|publish|send", text, re.I): findings.append(finding("STREAM_COMMIT_REVIEW", "warning", "Streaming and a persistence/side-effect symbol coexist; verify partial output cannot commit before terminal completion.", paths(source_files), "stream and side-effect symbols"))
    facts = {"build_files": paths(files), "spring_ai_versions": versions, "spring_boot_versions": boots, "java_versions": java, "config_files": paths([p for p,_ in cfg]), "java_files": len(source_files)}
    status = "error" if any(x["severity"] == "error" for x in findings) else ("warning" if findings else "ok")
    return {"status": status, "project": str(root), "facts": facts, "findings": findings, "errors": []}

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default="."); ap.add_argument("--json", action="store_true"); ap.add_argument("--strict", action="store_true")
    try:
        args = ap.parse_args(argv); root = Path(args.root).expanduser().resolve()
        if not root.is_dir(): raise ValueError(f"project root is not a directory: {root}")
        result = check(root)
        if args.strict and result["status"] == "warning": result["status"] = "error"
        print(json.dumps(result, indent=2, sort_keys=True) if args.json else human(result))
        return 1 if result["status"] == "error" else 0
    except (ValueError, RuntimeError, OSError) as exc:
        result = {"status":"invalid", "project":str(Path(args.root).expanduser()) if 'args' in locals() else None, "facts":{}, "findings":[], "errors":[str(exc)]}
        print(json.dumps(result, indent=2, sort_keys=True) if 'args' in locals() and args.json else f"ERROR: {exc}", file=sys.stderr if not ('args' in locals() and args.json) else sys.stdout)
        return 2

def human(result):
    lines = [f"status: {result['status']}", f"project: {result['project']}"]
    for f in result["findings"]: lines.append(f"{f['severity'].upper()} {f['code']}: {f['message']}")
    return "\n".join(lines)

if __name__ == "__main__": sys.exit(main())
