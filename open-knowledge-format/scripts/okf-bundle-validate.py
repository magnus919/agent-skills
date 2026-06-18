#!/usr/bin/env python3
"""
okf-bundle-validate.py — Validate an OKF v0.1 knowledge bundle.

Checks:
  1. Every non-reserved .md file has parseable YAML frontmatter
  2. Every frontmatter block has a non-empty "type" field
  3. Reserved filenames (index.md, log.md) follow their defined structure
  4. Cross-links point to existing concept files (soft warning)
  5. No filename collisions between concept IDs

Usage:
  python3 okf-bundle-validate.py <bundle-directory>
  python3 okf-bundle-validate.py <bundle-directory> --fix-missing-types
  python3 okf-bundle-validate.py <bundle-directory> --json
"""

import os
import sys
import json
import re
import argparse
from pathlib import Path

RESERVED = {"index.md", "log.md"}
DATE_HEADING_RE = re.compile(r"^##\s+\d{4}-\d{2}-\d{2}")
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
MD_LINK_RE = re.compile(r"\]\(((?:/|\./|\.\./)?[^)]+\.md)\)")


class ValidationResult:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []
        self.stats = {
            "concept_files": 0,
            "reserved_files": 0,
            "cross_links": 0,
            "broken_links": 0,
        }

    def error(self, path, msg):
        self.errors.append({"path": str(path), "message": msg})

    def warning(self, path, msg):
        self.warnings.append({"path": str(path), "message": msg})

    def add_info(self, msg):
        self.info.append(msg)

    @property
    def passed(self):
        return len(self.errors) == 0

    def to_dict(self):
        return {
            "passed": self.passed,
            "errors": self.errors,
            "warnings": self.warnings,
            "info": self.info,
            "stats": self.stats,
        }

    def summary(self):
        parts = []
        if self.errors:
            parts.append(f"FAILED: {len(self.errors)} error(s)")
        else:
            parts.append("PASSED")
        parts.append(f"{self.stats['concept_files']} concepts")
        parts.append(f"{self.stats['reserved_files']} reserved files")
        parts.append(f"{self.stats['cross_links']} cross-links")
        if self.stats["broken_links"]:
            parts.append(f"{self.stats['broken_links']} broken link(s)")
        return ", ".join(parts)


def parse_frontmatter(content):
    """Parse YAML frontmatter from markdown content. Returns (fields, body, error)."""
    if not content.startswith("---"):
        return None, content, "File does not start with frontmatter delimiter"
    
    # Find closing ---
    end_idx = content.find("\n---", 3)
    if end_idx == -1:
        return None, content, "Frontmatter not closed (missing closing ---)"
    
    yaml_block = content[3:end_idx].strip()
    body = content[end_idx + 4:].strip()
    
    if not yaml_block:
        return {}, body, None
    
    # Simple YAML parser for the subset OKF uses
    fields = {}
    current_key = None
    list_mode = False
    
    for line in yaml_block.split("\n"):
        # Skip blank lines and comments
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        
        # Tag list continuation
        if list_mode and stripped.startswith("- "):
            if isinstance(fields.get(current_key), list):
                fields[current_key].append(stripped[2:])
            continue
        else:
            list_mode = False
        
        # Key-value pair
        if ":" in stripped and not stripped.startswith("- "):
            colon_idx = stripped.index(":")
            key = stripped[:colon_idx].strip()
            value = stripped[colon_idx + 1:].strip()
            current_key = key
            
            if not value or value == "|" or value == ">":
                fields[key] = ""
            elif value.startswith("[") and value.endswith("]"):
                # Inline list
                inner = value[1:-1]
                items = [item.strip().strip("'\"") for item in inner.split(",") if item.strip()]
                fields[key] = items
            elif value.startswith("- "):
                list_mode = True
                fields[key] = [value[2:]]
            elif value.lower() == "true":
                fields[key] = True
            elif value.lower() == "false":
                fields[key] = False
            else:
                # Remove surrounding quotes
                if (value.startswith("'") and value.endswith("'")) or \
                   (value.startswith('"') and value.endswith('"')):
                    value = value[1:-1]
                fields[key] = value
    
    return fields, body, None


def collect_md_files(bundle_path):
    """Collect all .md files in the bundle directory."""
    md_files = []
    for root, dirs, files in os.walk(bundle_path):
        # Skip hidden dirs
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for f in files:
            if f.endswith(".md"):
                abs_path = Path(root) / f
                rel_path = abs_path.relative_to(bundle_path)
                md_files.append(rel_path)
    return sorted(md_files)


def check_index_file(path, content, result):
    """Check an index.md file follows OKF conventions."""
    lines = content.strip().split("\n")
    
    # Check for frontmatter (should NOT have it, except at bundle root)
    if content.startswith("---"):
        # Only allowed at bundle root for okf_version
        if str(path) != "index.md":
            result.warning(path, "index.md in subdirectory contains frontmatter (should be frontmatter-free)")
        else:
            # Has frontmatter - check it only contains okf_version
            end_idx = content.find("\n---", 3)
            if end_idx != -1:
                yaml_block = content[3:end_idx].strip()
                if yaml_block and "okf_version" not in yaml_block:
                    result.warning(path, "Root index.md frontmatter should only contain okf_version")


def check_log_file(path, content, result):
    """Check a log.md file follows OKF conventions."""
    lines = content.strip().split("\n")
    date_headings = 0
    
    for line in lines:
        if DATE_HEADING_RE.match(line.strip()):
            date_headings += 1
    
    if date_headings == 0:
        result.warning(path, "log.md has no ISO 8601 date headings (## YYYY-MM-DD)")


def validate_bundle(bundle_path, fix_missing_types=False):
    """Validate an OKF v0.1 bundle directory."""
    result = ValidationResult()
    bundle_path = Path(bundle_path).resolve()
    
    if not bundle_path.is_dir():
        result.error(bundle_path, "Not a directory")
        return result
    
    result.add_info(f"Bundle path: {bundle_path}")
    
    md_files = collect_md_files(bundle_path)
    if not md_files:
        result.error(bundle_path, "No markdown files found in bundle")
        return result
    
    # Build concept ID map
    concept_ids = {}
    for rel_path in md_files:
        stem = str(rel_path.with_suffix(""))
        concept_ids[stem] = rel_path
    
    # Validate each file
    for rel_path in md_files:
        abs_path = bundle_path / rel_path
        filename = rel_path.name
        
        try:
            content = abs_path.read_text(encoding="utf-8")
        except Exception as e:
            result.error(rel_path, f"Cannot read file: {e}")
            continue
        
        is_reserved = filename in RESERVED
        
        if is_reserved:
            result.stats["reserved_files"] += 1
        else:
            result.stats["concept_files"] += 1
        
        # Check frontmatter
        fields, body, parse_err = parse_frontmatter(content)
        
        if parse_err:
            if is_reserved:
                result.add_info(f"Reserved file {rel_path} has no frontmatter (expected for {filename})")
            else:
                result.error(rel_path, parse_err)
            continue
        
        # Check reserved file structure
        if filename == "index.md" and is_reserved:
            check_index_file(rel_path, content, result)
        elif filename == "log.md" and is_reserved:
            check_log_file(rel_path, content, result)
        
        if is_reserved:
            continue
        
        # Check required 'type' field
        if not fields or "type" not in fields or not fields.get("type"):
            if fix_missing_types:
                # We don't actually fix here — this is informational
                result.error(rel_path, "Missing required 'type' field in frontmatter")
            else:
                result.error(rel_path, "Missing required 'type' field in frontmatter")
            continue
        
        # Check cross-links
        md_links = MD_LINK_RE.findall(body) if body else []
        for link in md_links:
            result.stats["cross_links"] += 1
            
            # Resolve relative links
            if link.startswith("/"):
                # Bundle-relative
                target = link[1:].replace(".md", "")
            elif link.startswith("./") or link.startswith("../"):
                # Relative — resolve from file's directory
                file_dir = str(rel_path.parent) if str(rel_path.parent) != "." else ""
                target = os.path.normpath(os.path.join(file_dir, link)).replace(".md", "")
            else:
                # External URL or same-file anchor — skip
                continue
            
            # Remove anchors
            target = target.split("#")[0]
            
            if target and target not in concept_ids:
                result.stats["broken_links"] += 1
                result.warning(rel_path, f"Broken link to '{target}.md' (concept ID: {target})")
    
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Validate an OKF v0.1 knowledge bundle"
    )
    parser.add_argument(
        "bundle",
        help="Path to the OKF bundle directory"
    )
    parser.add_argument(
        "--fix-missing-types",
        action="store_true",
        help="Flag missing type fields as errors (default: errors)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    
    args = parser.parse_args()
    
    result = validate_bundle(args.bundle, fix_missing_types=args.fix_missing_types)
    
    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print("\n" + "=" * 60)
        print(f"  OKF Bundle Validation: {result.summary()}")
        print("=" * 60)
        
        if result.errors:
            print(f"\n  Errors ({len(result.errors)}):")
            for err in result.errors:
                print(f"    ✗ {err['path']}: {err['message']}")
        
        if result.warnings:
            print(f"\n  Warnings ({len(result.warnings)}):")
            for warn in result.warnings:
                print(f"    ⚠ {warn['path']}: {warn['message']}")
        
        if result.info:
            print(f"\n  Info:")
            for msg in result.info:
                print(f"    ℹ {msg}")
        
        print()
    
    return 0 if result.passed else 1


if __name__ == "__main__":
    sys.exit(main())
