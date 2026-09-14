#!/usr/bin/env python3
"""Read-only, offline diagnostics for Maven and Gradle Spring AI projects."""

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

VERSION = r"[0-9]+\.[0-9]+(?:\.[0-9]+)?(?:-[A-Za-z0-9.-]+)?"


def finding(code, severity, message, paths, evidence):
    return {
        "code": code,
        "severity": severity,
        "message": message,
        "paths": paths,
        "evidence": evidence,
    }


def read(path):
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise RuntimeError(f"cannot decode {path} as UTF-8") from exc
    except OSError as exc:
        raise RuntimeError(f"cannot read {path}: {exc}") from exc


def strip_comments(text):
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"(?m)^\s*//.*$", "", text)
    text = re.sub(r"(?m)^\s*#.*$", "", text)
    return text


def strip_java_comments(text):
    """Remove Java comments while preserving string and character literals."""
    result = []
    index = 0
    state = "normal"
    while index < len(text):
        char = text[index]
        next_char = text[index + 1] if index + 1 < len(text) else ""
        if state == "normal":
            if char == '"':
                state = "string"
                result.append(char)
            elif char == "'":
                state = "char"
                result.append(char)
            elif char == "/" and next_char == "/":
                state = "line"
                result.append(" ")
                index += 1
            elif char == "/" and next_char == "*":
                state = "block"
                result.append(" ")
                index += 1
            else:
                result.append(char)
        elif state == "line":
            if char == "\n":
                state = "normal"
                result.append(char)
        elif state == "block":
            if char == "*" and next_char == "/":
                state = "normal"
                result.append(" ")
                index += 1
            elif char == "\n":
                result.append("\n")
        else:
            result.append(char)
            if char == "\\" and next_char:
                result.append(next_char)
                index += 1
            elif (state == "string" and char == '"') or (state == "char" and char == "'"):
                state = "normal"
        index += 1
    return "".join(result)


def rel(root, paths):
    return [str(path.relative_to(root)) for path in paths]


def maven_versions(text):
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        raise ValueError("pom.xml is not well-formed XML") from exc
    # Namespace-independent element access, scoped to the dependency or parent.
    def child(node, name):
        return next((x for x in node if x.tag.split("}")[-1] == name), None)

    def value(node, name):
        item = child(node, name)
        return (item.text or "").strip() if item is not None else ""

    props_node = child(root, "properties")
    props = {
        x.tag.split("}")[-1]: (x.text or "").strip()
        for x in (props_node if props_node is not None else [])
    }
    ai, boot = set(), set()
    for node in root.iter():
        if node.tag.split("}")[-1] not in {"dependency", "parent"}:
            continue
        coordinate = (value(node, "groupId"), value(node, "artifactId"))
        target = None
        if coordinate == ("org.springframework.ai", "spring-ai-bom"):
            target = ai
        elif coordinate[0] == "org.springframework.boot" and coordinate[1] in {
            "spring-boot-starter-parent", "spring-boot-dependencies"
        }:
            target = boot
        if target is None:
            continue
        version = value(node, "version")
        seen = set()
        while version.startswith("${") and version.endswith("}") and version not in seen:
            seen.add(version)
            version = props.get(version[2:-1], version)
        if re.fullmatch(VERSION, version):
            target.add(version)
    # A conventional property is a declared clue, not proof of dependency resolution.
    for key in ("spring-ai.version", "spring-ai-version"):
        if re.fullmatch(VERSION, props.get(key, "")):
            ai.add(props[key])
    return ai, boot, props


def gradle_versions(text):
    clean = strip_comments(text)
    variables = dict(
        re.findall(r"(?:def\s+)?([A-Za-z][A-Za-z0-9_]*)\s*=\s*[\"']([^\"']+)[\"']", clean)
    )
    ai, boot = set(), set()
    for match in re.finditer(r"spring-ai-bom:([^\"')\s]+)", clean):
        value = match.group(1)
        if value.startswith("${"):
            value = variables.get(value[2:-1], value)
        elif value.startswith("$"):
            value = variables.get(value[1:], value)
        if re.fullmatch(VERSION, value):
            ai.add(value)
    for key, value in variables.items():
        if key.lower() in {"springaiversion", "spring_ai_version"} and re.fullmatch(VERSION, value):
            ai.add(value)
        if key.lower() in {"springbootversion", "spring_boot_version"} and re.fullmatch(
            VERSION, value
        ):
            boot.add(value)
    return ai, boot, variables


def check(root):
    build_files = [
        path
        for path in (
            root / "pom.xml",
            root / "build.gradle",
            root / "build.gradle.kts",
            root / "gradle.properties",
        )
        if path.exists()
    ]
    if not build_files:
        raise ValueError("no pom.xml, build.gradle, build.gradle.kts, or gradle.properties found")
    config = []
    for base in (root / "src/main/resources", root / "src/test/resources"):
        for name in ("application.properties", "application.yml", "application.yaml"):
            path = base / name
            if path.exists():
                config.append((path, read(path)))
    java_files = [
        path
        for base in (root / "src/main/java", root / "src/test/java")
        if base.exists()
        for path in base.rglob("*.java")
    ]
    build_text = "\n".join(read(path) for path in build_files)
    clean_build = strip_comments(build_text)
    if any(path.name == "pom.xml" for path in build_files):
        ai_versions, boot_versions, variables = maven_versions(read(root / "pom.xml"))
    else:
        ai_versions, boot_versions, variables = gradle_versions(build_text)
    source = [(path, strip_java_comments(read(path))) for path in java_files]
    findings = []
    if not ai_versions:
        unresolved = bool(
            re.search(r"spring-ai-bom|spring-ai\.version\s*[<>=:]", clean_build, re.I)
        )
        code = "SPRING_AI_VERSION_UNKNOWN" if unresolved else "SPRING_AI_VERSION_MISSING"
        message = (
            "Spring AI dependency management was found but its version is unresolved."
            if unresolved
            else "No Spring AI BOM or version property was detected."
        )
        findings.append(
            finding(
                code,
                "warning",
                message,
                rel(root, build_files),
                "static dependency scan; compatibility is not established",
            )
        )
    memory_files = [path for path, text in source if "ChatMemory" in text]
    if memory_files:
        if not any("CONVERSATION_ID" in text for _, text in source):
            findings.append(
                finding(
                    "MEMORY_CONVERSATION_ID_MISSING",
                    "error",
                    "Chat memory symbols are present but no explicit conversation ID symbol was found.",
                    rel(root, memory_files),
                    "source scan",
                )
            )
        findings.append(
            finding(
                "MEMORY_ISOLATION_UNPROVEN",
                "warning",
                "A conversation ID symbol does not prove user/tenant isolation; test the authenticated scope and persistence boundary.",
                rel(root, memory_files),
                "static scan cannot prove isolation",
            )
        )
    stream_files = [path for path, text in source if re.search(r"\.stream\s*\(", text)]
    if stream_files and "spring-boot-starter-webflux" not in clean_build:
        findings.append(
            finding(
                "STREAMING_STACK_UNCLEAR",
                "warning",
                "Streaming code was found without a detected WebFlux starter; verify the selected Spring AI runtime stack.",
                rel(root, build_files),
                "source and dependency scan",
            )
        )
    logging_files = [
        path
        for path, text in config
        if re.search(r"log-(?:prompt|completion)\s*[:=]\s*true", strip_comments(text), re.I)
    ]
    if logging_files:
        findings.append(
            finding(
                "PROMPT_LOGGING_ENABLED",
                "error",
                "Prompt or completion logging is enabled; review redaction, access, retention, and rollback.",
                rel(root, logging_files),
                "configuration value is true",
            )
        )
    literal_files = [
        path
        for path, text in config
        if re.search(
            r"spring\.ai\.[^\n]*(?:api-key|apiKey)\s*[:=]\s*(?!\$\{|\$)[^\s#]+",
            strip_comments(text),
            re.I,
        )
    ]
    if literal_files:
        findings.append(
            finding(
                "PROVIDER_SECRET_LITERAL",
                "error",
                "A provider credential appears literal; use an environment or secret reference. The value is omitted.",
                rel(root, literal_files),
                "credential key detected; value redacted",
            )
        )
    retrieval_files = [
        path
        for path, text in source
        if re.search(r"QuestionAnswerAdvisor|RetrievalAugmentationAdvisor|VectorStore", text)
    ]
    if retrieval_files:
        findings.append(
            finding(
                "RETRIEVAL_AUTH_UNVERIFIED",
                "warning",
                "Retrieval integration was found; static scanning cannot establish authorization or tenant filtering before prompt construction.",
                rel(root, retrieval_files),
                "retrieval symbols detected",
            )
        )
    tool_files = [
        path for path, text in source if re.search(r"\.tools\s*\(|@Tool\b|ToolCallback|Mcp", text)
    ]
    if tool_files:
        findings.append(
            finding(
                "TOOL_AUTH_UNVERIFIED",
                "warning",
                "Tool or MCP integration was found; static scanning cannot establish authorization, argument validation, timeout, or side-effect controls.",
                rel(root, tool_files),
                "tool symbols detected",
            )
        )
    facts = {
        "build_files": rel(root, build_files),
        "spring_ai_versions": sorted(ai_versions),
        "spring_boot_versions": sorted(boot_versions),
        "version_variables": sorted(variables),
        "config_files": rel(root, [path for path, _ in config]),
        "java_files": len(java_files),
        "compatibility_assessment": "static-facts-only; consult official release and upgrade notes",
    }
    status = (
        "error"
        if any(item["severity"] == "error" for item in findings)
        else ("warning" if findings else "ok")
    )
    return {
        "status": status,
        "project": str(root),
        "facts": facts,
        "findings": findings,
        "errors": [],
    }


def human(result):
    lines = [f"status: {result['status']}", f"project: {result['project']}"]
    lines.extend(
        f"{item['severity'].upper()} {item['code']}: {item['message']}"
        for item in result["findings"]
    )
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    try:
        args = parser.parse_args(argv)
        root = Path(args.root).expanduser().resolve()
        if not root.is_dir():
            raise ValueError(f"project root is not a directory: {root}")
        result = check(root)
        if args.strict and result["status"] == "warning":
            result["status"] = "error"
        print(json.dumps(result, indent=2, sort_keys=True) if args.json else human(result))
        return 1 if result["status"] == "error" else 0
    except (OSError, RuntimeError, ValueError) as exc:
        project = str(Path(args.root).expanduser()) if "args" in locals() else None
        result = {
            "status": "invalid",
            "project": project,
            "facts": {},
            "findings": [],
            "errors": [str(exc)],
        }
        if "args" in locals() and args.json:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
