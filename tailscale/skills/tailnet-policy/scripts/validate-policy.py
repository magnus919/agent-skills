#!/usr/bin/env python3
"""
validate-policy.py — Validate huJSON policy files for Headscale/Tailscale.

Parses huJSON (handles trailing commas, comments), validates structure:
  - tagOwners references are consistent
  - grants have valid src/dst/ip fields
  - acls (legacy) have valid users/ports fields
  - autoApprovers have valid routes/exitNode
  - ssh rules have valid action/src/dst/users
  - tests have valid src/dst/ip/action

Usage:
  validate-policy.py --policy policy.hujson
  validate-policy.py --policy policy.hujson --json
  validate-policy.py --policy policy.hujson --fix
  validate-policy.py --help
"""

import argparse
import json
import os
import re
import sys
from typing import Any, Dict, List, Optional, Tuple


def parse_hujson(text: str) -> Tuple[Optional[Dict[str, Any]], List[str]]:
    """
    Parse huJSON text, handling trailing commas and single-line // comments.
    Returns (parsed_dict, errors_list).
    """
    errors: List[str] = []
    cleaned = text

    # Remove single-line // comments (but not http:// style)
    # Handle strings: temporarily replace strings so we don't mangle URLs in them
    strings: List[str] = []
    string_holders: List[str] = []

    def _protect_strings(s: str) -> str:
        """Replace JSON strings with placeholders to avoid comment removal inside them."""
        result = []
        i = 0
        while i < len(s):
            if s[i] == '"':
                # Find matching closing quote (skip escaped quotes)
                j = i + 1
                while j < len(s):
                    if s[j] == '\\':
                        j += 2
                        continue
                    if s[j] == '"':
                        j += 1
                        break
                    j += 1
                holder = f'__STR_{len(strings)}__'
                strings.append(s[i:j])
                string_holders.append(holder)
                result.append(holder)
                i = j
            else:
                result.append(s[i])
                i += 1
        return ''.join(result)

    def _restore_strings(s: str) -> str:
        """Restore string placeholders back to original strings."""
        for holder, orig in zip(string_holders, strings):
            s = s.replace(holder, orig)
        return s

    # Protect strings
    protected = _protect_strings(cleaned)

    # Remove // comments (outside strings)
    lines = protected.split('\n')
    cleaned_lines = []
    for line in lines:
        # Find // that's not inside a string (strings are already placeholders)
        comment_pos = line.find('//')
        if comment_pos >= 0:
            line = line[:comment_pos]
        cleaned_lines.append(line)
    cleaned = '\n'.join(cleaned_lines)

    # Restore strings
    cleaned = _restore_strings(cleaned)

    # Remove trailing commas before ] or }
    cleaned = re.sub(r',\s*([}\]])', r'\1', cleaned)

    # Also handle trailing commas in arrays/objects with whitespace/newlines
    cleaned = re.sub(r',\s*\n\s*([}\]])', r'\n\1', cleaned)

    try:
        parsed = json.loads(cleaned)
        return parsed, []
    except json.JSONDecodeError as e:
        errors.append(f"JSON parse error: {e}")
        return None, errors


def validate_tag_name(tag: str) -> Optional[str]:
    """Validate a tag name, return error message or None."""
    if not tag.startswith('tag:'):
        return f"Invalid tag format: '{tag}' — must start with 'tag:'"
    name = tag[4:]
    if not re.match(r'^[a-z0-9][a-z0-9-]*$', name):
        return f"Invalid tag name: '{tag}' — must be lowercase alphanumeric with hyphens"
    return None


def validate_autogroup(group: str) -> Optional[str]:
    """Validate an autogroup reference."""
    valid = {'autogroup:member', 'autogroup:admin', 'autogroup:tagged', 'autogroup:internet'}
    if group not in valid:
        return f"Unknown autogroup: '{group}' — valid options: {', '.join(sorted(valid))}"
    return None


def validate_grants(grants: List[Dict[str, Any]]) -> List[str]:
    """Validate grants array entries."""
    errors: List[str] = []
    for i, grant in enumerate(grants):
        prefix = f"grants[{i}]"

        if not isinstance(grant, dict):
            errors.append(f"{prefix}: expected object, got {type(grant).__name__}")
            continue

        # Check required fields
        if 'src' not in grant:
            errors.append(f"{prefix}: missing required field 'src'")
        if 'dst' not in grant:
            errors.append(f"{prefix}: missing required field 'dst'")

        # Validate src is an array
        src = grant.get('src', [])
        if not isinstance(src, list):
            errors.append(f"{prefix}.src: must be an array, got {type(src).__name__}")
        else:
            for j, s in enumerate(src):
                if not isinstance(s, str):
                    errors.append(f"{prefix}.src[{j}]: must be a string")
                elif s.startswith('tag:'):
                    err = validate_tag_name(s)
                    if err:
                        errors.append(f"{prefix}.src[{j}]: {err}")
                elif s.startswith('autogroup:'):
                    err = validate_autogroup(s)
                    if err:
                        errors.append(f"{prefix}.src[{j}]: {err}")

        # Validate dst is an array
        dst = grant.get('dst', [])
        if not isinstance(dst, list):
            errors.append(f"{prefix}.dst: must be an array, got {type(dst).__name__}")
        else:
            for j, d in enumerate(dst):
                if not isinstance(d, str):
                    errors.append(f"{prefix}.dst[{j}]: must be a string")
                elif d.startswith('tag:'):
                    err = validate_tag_name(d)
                    if err:
                        errors.append(f"{prefix}.dst[{j}]: {err}")

        # Validate ip if present
        ip = grant.get('ip', [])
        if ip is not None and not isinstance(ip, list):
            errors.append(f"{prefix}.ip: must be an array or omitted")
        elif ip:
            for j, p in enumerate(ip):
                if not isinstance(p, str):
                    errors.append(f"{prefix}.ip[{j}]: must be a string")

        # Validate proto if present
        proto = grant.get('proto')
        if proto is not None and proto not in ('tcp', 'udp', 'icmp'):
            errors.append(f"{prefix}.proto: must be 'tcp', 'udp', or 'icmp', got '{proto}'")

        # Validate via if present
        via = grant.get('via')
        if via is not None:
            if isinstance(via, list):
                for j, v in enumerate(via):
                    if not isinstance(v, str):
                        errors.append(f"{prefix}.via[{j}]: must be a string")
            elif not isinstance(via, str):
                errors.append(f"{prefix}.via: must be a string or array")

    return errors


def validate_acls(acls: List[Dict[str, Any]]) -> List[str]:
    """Validate legacy ACL syntax entries."""
    errors: List[str] = []
    for i, acl in enumerate(acls):
        prefix = f"acls[{i}]"

        if not isinstance(acl, dict):
            errors.append(f"{prefix}: expected object, got {type(acl).__name__}")
            continue

        if 'action' not in acl:
            errors.append(f"{prefix}: missing required field 'action'")
        elif acl['action'] not in ('accept', 'drop'):
            errors.append(f"{prefix}.action: must be 'accept' or 'drop', got '{acl['action']}'")

        if 'users' not in acl:
            errors.append(f"{prefix}: missing required field 'users'")
        elif not isinstance(acl['users'], list):
            errors.append(f"{prefix}.users: must be an array")

        if 'ports' not in acl:
            errors.append(f"{prefix}: missing required field 'ports'")
        elif not isinstance(acl['ports'], list):
            errors.append(f"{prefix}.ports: must be an array")

    return errors


def validate_tag_owners(tag_owners: Dict[str, Any], grants: List[Dict], acls: List[Dict]) -> List[str]:
    """Validate that all tags referenced in grants/acls have corresponding tagOwners."""
    errors: List[str] = []
    referenced_tags: set = set()

    if grants:
        for grant in grants:
            for field in ('src', 'dst'):
                items = grant.get(field, [])
                if isinstance(items, list):
                    for item in items:
                        if isinstance(item, str) and item.startswith('tag:'):
                            referenced_tags.add(item)

    if acls:
        for acl in acls:
            for field in ('users', 'ports'):
                items = acl.get(field, [])
                if isinstance(items, list):
                    for item in items:
                        if isinstance(item, str) and item.startswith('tag:'):
                            referenced_tags.add(item)

    if tag_owners and isinstance(tag_owners, dict):
        defined_tags = set(tag_owners.keys())
    else:
        defined_tags = set()

    if not tag_owners and referenced_tags:
        errors.append("Tags used in grants/acls but 'tagOwners' section is missing or empty")

    for tag in sorted(referenced_tags):
        if tag not in defined_tags:
            errors.append(f"Tag '{tag}' used in grants/acls but not defined in 'tagOwners'")

    # Check for unused tag owners
    if tag_owners and isinstance(tag_owners, dict):
        for tag in sorted(defined_tags):
            if tag not in referenced_tags:
                errors.append(f"Tag '{tag}' defined in 'tagOwners' but never referenced in grants/acls")

            # Validate tag name
            err = validate_tag_name(tag)
            if err:
                errors.append(err)

            # Validate owners
            owners = tag_owners[tag]
            if not isinstance(owners, list):
                errors.append(f"tagOwners.{tag}: must be an array")
            else:
                for j, owner in enumerate(owners):
                    if not isinstance(owner, str):
                        errors.append(f"tagOwners.{tag}[{j}]: must be a string")

    return errors


def validate_auto_approvers(auto_approvers: Dict[str, Any]) -> List[str]:
    """Validate autoApprovers section."""
    errors: List[str] = []

    if not isinstance(auto_approvers, dict):
        return [f"autoApprovers: expected object, got {type(auto_approvers).__name__}"]

    routes = auto_approvers.get('routes')
    if routes is not None:
        if not isinstance(routes, dict):
            errors.append("autoApprovers.routes: must be an object (cidr -> [users])")
        else:
            for cidr, users in routes.items():
                if not isinstance(cidr, str):
                    errors.append(f"autoApprovers.routes: key must be a string (CIDR)")
                if not isinstance(users, list):
                    errors.append(f"autoApprovers.routes['{cidr}']: must be an array of users")

    exit_node = auto_approvers.get('exitNode')
    if exit_node is not None:
        if not isinstance(exit_node, list):
            errors.append("autoApprovers.exitNode: must be an array of users")

    return errors


def validate_ssh(ssh_rules: List[Dict[str, Any]]) -> List[str]:
    """Validate Tailscale SSH rules."""
    errors: List[str] = []
    if not isinstance(ssh_rules, list):
        return [f"ssh: expected array, got {type(ssh_rules).__name__}"]

    for i, rule in enumerate(ssh_rules):
        prefix = f"ssh[{i}]"
        if not isinstance(rule, dict):
            errors.append(f"{prefix}: expected object")
            continue

        if 'action' not in rule:
            errors.append(f"{prefix}: missing 'action'")
        elif rule['action'] not in ('accept', 'check'):
            errors.append(f"{prefix}.action: must be 'accept' or 'check'")

        if 'src' not in rule:
            errors.append(f"{prefix}: missing 'src'")
        elif not isinstance(rule['src'], list):
            errors.append(f"{prefix}.src: must be an array")

        if 'dst' not in rule:
            errors.append(f"{prefix}: missing 'dst'")
        elif not isinstance(rule['dst'], list):
            errors.append(f"{prefix}.dst: must be an array")

        if 'users' not in rule:
            errors.append(f"{prefix}: missing 'users'")
        elif not isinstance(rule['users'], list):
            errors.append(f"{prefix}.users: must be an array")

    return errors


def validate_tests(tests: List[Dict[str, Any]]) -> List[str]:
    """Validate test definitions."""
    errors: List[str] = []
    if not isinstance(tests, list):
        return [f"tests: expected array, got {type(tests).__name__}"]

    for i, test in enumerate(tests):
        prefix = f"tests[{i}]"
        if not isinstance(test, dict):
            errors.append(f"{prefix}: expected object")
            continue

        if 'action' in test and test['action'] not in ('accept', 'drop'):
            errors.append(f"{prefix}.action: must be 'accept' or 'drop'")

    return errors


def auto_fix(content: str, errors: List[str]) -> Tuple[str, List[str]]:
    """
    Attempt auto-fixes for common issues.
    Returns (fixed_content, remaining_errors).
    """
    fixed = content
    remaining: List[str] = []

    # Fix 1: Missing closing brace
    open_braces = fixed.count('{')
    close_braces = fixed.count('}')
    if open_braces > close_braces:
        fixed += '\n}' * (open_braces - close_braces)
        remaining.append("Added missing closing braces")

    # Fix 2: Missing closing bracket
    open_brackets = fixed.count('[')
    close_brackets = fixed.count(']')
    if open_brackets > close_brackets:
        fixed += '\n]' * (open_brackets - close_brackets)
        remaining.append("Added missing closing brackets")

    # Fix 3: Trailing commas (already handled by parser, but fix in source)
    fixed = re.sub(r',\s*([}\]])', r'\1', fixed)

    # Fix 4: Remove BOM
    if fixed.startswith('\ufeff'):
        fixed = fixed[1:]
        remaining.append("Removed UTF-8 BOM")

    # Fix 5: Fix common tag naming errors (uppercase -> lowercase)
    fixed = re.sub(r'tag:([A-Z])', lambda m: f'tag:{m.group(1).lower()}', fixed)

    for err in errors:
        # Check if error was auto-fixable
        if "JSON parse error" in err:
            continue  # Might be fixed now, will re-validate
        remaining.append(err)

    return fixed, remaining


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate huJSON policy files for Headscale/Tailscale",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --policy policy.hujson
  %(prog)s --policy policy.hujson --json
  %(prog)s --policy policy.hujson --fix
        """
    )
    parser.add_argument('--policy', '-p', required=True, help='Path to huJSON policy file')
    parser.add_argument('--json', '-j', action='store_true', help='Output as JSON')
    parser.add_argument('--fix', '-f', action='store_true', help='Attempt auto-fix of common issues')
    parser.add_argument('--dry-run', action='store_true', help='Show what fixes would be applied without writing')

    args = parser.parse_args()
    policy_path = os.path.expanduser(args.policy)

    if not os.path.exists(policy_path):
        error_msg = f"Policy file not found: {policy_path}"
        if args.json:
            print(json.dumps({"valid": False, "errors": [error_msg]}, indent=2))
        else:
            print(f"ERROR: {error_msg}", file=sys.stderr)
        sys.exit(1)

    with open(policy_path, 'r') as f:
        content = f.read()

    parsed, parse_errors = parse_hujson(content)

    all_errors: List[str] = list(parse_errors)

    if parsed is not None and isinstance(parsed, dict):
        # Validate sections
        grants = parsed.get('grants')
        if grants is not None:
            all_errors.extend(validate_grants(grants))

        acls = parsed.get('acls')
        if acls is not None:
            all_errors.extend(validate_acls(acls))

        tag_owners = parsed.get('tagOwners', {})
        all_errors.extend(validate_tag_owners(tag_owners, grants or [], acls or []))

        auto_approvers = parsed.get('autoApprovers', {})
        if auto_approvers:
            all_errors.extend(validate_auto_approvers(auto_approvers))

        ssh = parsed.get('ssh')
        if ssh is not None:
            all_errors.extend(validate_ssh(ssh))

        tests = parsed.get('tests')
        if tests is not None:
            all_errors.extend(validate_tests(tests))

    elif parsed is not None and not isinstance(parsed, dict):
        all_errors.append(f"Policy root must be a JSON object, got {type(parsed).__name__}")

    # Auto-fix handling
    fix_notes: List[str] = []
    if args.fix and all_errors:
        fixed_content, remaining_errors = auto_fix(content, all_errors)
        fix_applied = fixed_content != content
        if fix_applied and not args.dry_run:
            with open(policy_path, 'w') as f:
                f.write(fixed_content)
            fix_notes.append(f"Applied fixes to {policy_path}")
            # Re-validate
            content = fixed_content
            all_errors = remaining_errors
            parsed, parse_errors = parse_hujson(content)
            if parsed and isinstance(parsed, dict):
                all_errors = list(parse_errors)
                grants = parsed.get('grants')
                if grants:
                    all_errors.extend(validate_grants(grants))
                acls = parsed.get('acls')
                if acls:
                    all_errors.extend(validate_acls(acls))
                tag_owners = parsed.get('tagOwners', {})
                all_errors.extend(validate_tag_owners(tag_owners, grants or [], acls or []))
                auto_approvers = parsed.get('autoApprovers', {})
                if auto_approvers:
                    all_errors.extend(validate_auto_approvers(auto_approvers))
                ssh = parsed.get('ssh')
                if ssh:
                    all_errors.extend(validate_ssh(ssh))
        elif fix_applied and args.dry_run:
            fix_notes.append("Would apply fixes (use --fix without --dry-run to apply)")

    is_valid = len(all_errors) == 0

    if args.json:
        output = {
            "valid": is_valid,
            "policy": os.path.basename(policy_path),
            "errors": all_errors,
        }
        if fix_notes:
            output["fixNotes"] = fix_notes
        print(json.dumps(output, indent=2))
    else:
        if fix_notes:
            for note in fix_notes:
                print(note)
        if is_valid:
            print(f"✓ Policy '{policy_path}' is valid")
        else:
            print(f"✗ Policy '{policy_path}' has {len(all_errors)} issue(s):", file=sys.stderr)
            for err in all_errors:
                print(f"  • {err}", file=sys.stderr)
            sys.exit(1)


if __name__ == '__main__':
    main()
