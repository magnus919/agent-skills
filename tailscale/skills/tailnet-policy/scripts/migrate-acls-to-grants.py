#!/usr/bin/env python3
"""
migrate-acls-to-grants.py — Convert legacy ACL syntax to modern Grants syntax.

Parses a huJSON policy file containing legacy ACLs and converts each ACL rule
to its Grant equivalent. Preserves tagOwners, autoApprovers, SSH sections, and
tests that are already in valid format.

ACL -> Grant Mapping:
  Legacy: {"action": "accept", "users": [...], "ports": ["*:*"]}
  Grant:  {"src": <users>, "dst": <ports-destinations>, "ip": ["*:*"]}

The conversion extracts destination hosts from port expressions like "tag:svr:80"
or "100.64.0.1:443" by splitting on the last colon (port separator).

Usage:
  migrate-acls-to-grants.py --input policy.hujson --output policy-grants.hujson
  migrate-acls-to-grants.py --input policy.hujson --dry-run
  migrate-acls-to-grants.py --input policy.hujson --json
  migrate-acls-to-grants.py --help
"""

import argparse
import json
import os
import re
import sys
from typing import Any, Dict, List, Optional, Tuple


def parse_hujson(text: str) -> Tuple[Optional[Dict[str, Any]], List[str]]:
    """
    Parse huJSON text, handling trailing commas and // comments.
    Returns (parsed_dict, errors_list).
    """
    errors: List[str] = []
    cleaned = text

    # Protect strings
    strings: List[str] = []
    string_holders: List[str] = []

    def _protect_strings(s: str) -> str:
        result = []
        i = 0
        while i < len(s):
            if s[i] == '"':
                j = i + 1
                while j < len(s):
                    if s[j] == '\\':
                        j += 2
                        continue
                    if s[j] == '"':
                        j += 1
                        break
                    j += 1
                holder = '__STR_{}__'.format(len(strings))
                strings.append(s[i:j])
                string_holders.append(holder)
                result.append(holder)
                i = j
            else:
                result.append(s[i])
                i += 1
        return ''.join(result)

    def _restore_strings(s: str) -> str:
        for holder, orig in zip(string_holders, strings):
            s = s.replace(holder, orig)
        return s

    protected = _protect_strings(cleaned)

    # Remove // comments
    lines = protected.split('\n')
    cleaned_lines = []
    for line in lines:
        comment_pos = line.find('//')
        if comment_pos >= 0:
            line = line[:comment_pos]
        cleaned_lines.append(line)
    cleaned = '\n'.join(cleaned_lines)

    cleaned = _restore_strings(cleaned)

    # Remove trailing commas
    cleaned = re.sub(r',\s*([}\]])', r'\1', cleaned)
    cleaned = re.sub(r',\s*\n\s*([}\]])', r'\n\1', cleaned)

    try:
        parsed = json.loads(cleaned)
        return parsed, []
    except json.JSONDecodeError as e:
        errors.append("JSON parse error: {}".format(e))
        return None, errors


def _serialize_value(val: Any, level: int, indent: int) -> str:
    """Serialize a value to huJSON-style string."""
    prefix = ' ' * (level * indent)
    inner_prefix = ' ' * ((level + 1) * indent)

    if val is None:
        return 'null'
    elif isinstance(val, bool):
        return 'true' if val else 'false'
    elif isinstance(val, (int, float)):
        return str(val)
    elif isinstance(val, str):
        return json.dumps(val)
    elif isinstance(val, list):
        if not val:
            return '[]'
        items = []
        for item in val:
            items.append(inner_prefix + _serialize_value(item, level + 1, indent))
        return '[\n' + ',\n'.join(items) + '\n' + prefix + ']'
    elif isinstance(val, dict):
        if not val:
            return '{}'
        items = []
        for key, value in val.items():
            k = json.dumps(key)
            v = _serialize_value(value, level + 1, indent)
            items.append(inner_prefix + k + ': ' + v)
        return '{\n' + ',\n'.join(items) + '\n' + prefix + '}'
    else:
        return str(val)


def serialize_hujson(obj: Any, indent: int = 2) -> str:
    """Serialize to huJSON-style output (with trailing commas for readability)."""
    result = _serialize_value(obj, 0, indent)

    # Add trailing commas before ] and } for huJSON style
    lines = result.split('\n')
    output_lines = []
    for i, line in enumerate(lines):
        stripped = line.rstrip()
        if i < len(lines) - 1:
            next_line = lines[i + 1].strip() if i + 1 < len(lines) else ''
            if stripped.endswith('}') and next_line in (']', '},'):
                stripped += ','
            elif stripped.endswith(']') and next_line == ']':
                stripped += ','
        output_lines.append(stripped)

    return '\n'.join(output_lines)


def parse_port_expression(port_expr: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Parse a port expression like "tag:webserver:80" or "100.64.0.1:443" or "*:*".
    Returns (destination, port_or_none).
    
    Handles:
      "tag:webserver:80"   -> ("tag:webserver", "80")
      "100.64.0.1:443"     -> ("100.64.0.1", "443")
      "*:*"                -> ("*", "*")
      "tag:ci-runner:*"    -> ("tag:ci-runner", "*")
    """
    if port_expr == '*:*':
        return '*', '*'

    if port_expr.startswith('tag:'):
        # Split on last colon to isolate port
        # tag:name:port — need to be careful
        # Remove the leading 'tag:' then find the last colon
        after_tag = port_expr[4:]  # e.g., "webserver:80"
        last_colon = after_tag.rfind(':')
        if last_colon >= 0:
            tag_name = after_tag[:last_colon]
            port = after_tag[last_colon + 1:]
            return 'tag:' + tag_name, port
        return port_expr, None

    if ':' in port_expr:
        parts = port_expr.rsplit(':', 1)
        return parts[0], parts[1]

    return port_expr, None


def convert_acl_to_grants(acls: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Convert legacy ACL entries to modern Grant entries.
    Returns (grants, warnings).
    """
    grants: List[Dict[str, Any]] = []
    warnings: List[str] = []

    for i, acl in enumerate(acls):
        if not isinstance(acl, dict):
            warnings.append("acls[{}]: skipped non-object entry".format(i))
            continue

        action = acl.get('action', 'accept')
        users = acl.get('users', [])
        ports = acl.get('ports', [])

        if not isinstance(users, list):
            warnings.append("acls[{}]: 'users' must be an array, skipping".format(i))
            continue

        if action == 'drop':
            warnings.append("acls[{}]: drop rules cannot be directly converted to Grants "
                           "(Grants are accept-only; deny-by-default must be relied upon)".format(i))
            continue

        # For each port entry, create a grant
        if not isinstance(ports, list):
            warnings.append("acls[{}]: 'ports' must be an array, skipping".format(i))
            continue

        for port_expr in ports:
            if not isinstance(port_expr, str):
                warnings.append("acls[{}].ports: skipped non-string entry: {}".format(i, port_expr))
                continue

            dst, port = parse_port_expression(port_expr)

            if dst is None:
                warnings.append("acls[{}].ports: could not parse '{}'".format(i, port_expr))
                continue

            # Build ip filter
            ip_filter = port or '*'
            # If port is a number or has proto:port format, use as-is
            # If it's just a number, prefix with *: or tcp:
            if ip_filter.isdigit():
                ip_filter = '*:' + ip_filter
            elif ip_filter == '*':
                ip_filter = '*:*'

            # Determine if we need to merge with existing grants
            grant = {
                'src': list(users) if isinstance(users, list) else [users],
                'dst': [dst],
                'ip': [ip_filter],
            }
            grants.append(grant)

    return grants, warnings


def convert_legacy_tests(tests: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Convert legacy test entries if they use users/ports format."""
    warnings: List[str] = []
    converted: List[Dict[str, Any]] = []

    for i, test in enumerate(tests):
        if not isinstance(test, dict):
            warnings.append("tests[{}]: skipped non-object entry".format(i))
            continue

        # Check if it uses legacy format
        if 'users' in test or 'ports' in test:
            users = test.get('users', [])
            ports = test.get('ports', [])
            action = test.get('action', 'accept')

            for port_expr in (ports if isinstance(ports, list) else [ports]):
                dst, port_str = parse_port_expression(str(port_expr) if port_expr else '*:*')
                ip_filter = '*:' + port_str if port_str and port_str.isdigit() else (port_str or '*:*')

                new_test: Dict[str, Any] = {
                    'src': users if isinstance(users, list) else [users],
                    'dst': dst or '*',
                    'action': action,
                }
                # src might be a string (legacy tests accept strings)
                if isinstance(users, str):
                    new_test['src'] = users
                if dst and port_str:
                    new_test['ip'] = [ip_filter]

                converted.append(new_test)
                warnings.append("tests[{}]: converted from legacy format to grant-style test".format(i))
        else:
            # Already in modern format
            converted.append(test)

    return converted, warnings


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert legacy ACL syntax to modern Grants syntax",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input policy.hujson --output policy-grants.hujson
  %(prog)s --input policy.hujson --dry-run
  %(prog)s --input policy.hujson --json
        """
    )
    parser.add_argument('--input', '-i', required=True, help='Path to input huJSON policy file')
    parser.add_argument('--output', '-o', default=None, help='Path to output file (default: stdout)')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without writing')
    parser.add_argument('--json', '-j', action='store_true', help='Output as JSON')

    args = parser.parse_args()
    input_path = os.path.expanduser(args.input)

    if not os.path.exists(input_path):
        error_msg = "Input file not found: " + input_path
        if args.json:
            print(json.dumps({"converted": False, "errors": [error_msg]}, indent=2))
        else:
            print("ERROR: " + error_msg, file=sys.stderr)
        sys.exit(1)

    with open(input_path, 'r') as f:
        content = f.read()

    parsed, parse_errors = parse_hujson(content)

    if parsed is None:
        if args.json:
            print(json.dumps({"converted": False, "errors": parse_errors}, indent=2))
        else:
            for err in parse_errors:
                print("ERROR: " + err, file=sys.stderr)
        sys.exit(1)

    if not isinstance(parsed, dict):
        msg = "Policy root must be a JSON object"
        if args.json:
            print(json.dumps({"converted": False, "errors": [msg]}, indent=2))
        else:
            print("ERROR: " + msg, file=sys.stderr)
        sys.exit(1)

    # Extract sections
    existing_grants = parsed.get('grants', [])
    existing_acls = parsed.get('acls', [])
    tag_owners = parsed.get('tagOwners', {})
    auto_approvers = parsed.get('autoApprovers', {})
    ssh = parsed.get('ssh', [])
    existing_tests = parsed.get('tests', [])

    all_warnings: List[str] = []

    # Convert ACLs to grants
    if existing_acls:
        converted_grants, acl_warnings = convert_acl_to_grants(existing_acls)
        all_warnings.extend(acl_warnings)
    else:
        converted_grants = []

    # Combine existing grants with converted ones
    combined_grants = list(existing_grants) + converted_grants

    # Convert legacy tests
    converted_tests, test_warnings = convert_legacy_tests(existing_tests)
    all_warnings.extend(test_warnings)

    # Build output policy
    output_policy: Dict[str, Any] = {}

    if tag_owners:
        output_policy['tagOwners'] = tag_owners

    if combined_grants:
        output_policy['grants'] = combined_grants

    if auto_approvers:
        output_policy['autoApprovers'] = auto_approvers

    if ssh:
        output_policy['ssh'] = ssh

    if converted_tests:
        output_policy['tests'] = converted_tests

    # Stats
    stats = {
        'acls_converted': len(existing_acls),
        'grants_from_acls': len(converted_grants),
        'existing_grants_preserved': len(existing_grants),
        'total_grants': len(combined_grants),
        'warnings': len(all_warnings),
    }

    # Output
    if args.json:
        output = {
            "converted": True,
            "stats": stats,
            "warnings": all_warnings,
            "policy": output_policy,
        }
        print(json.dumps(output, indent=2))
    else:
        if all_warnings:
            print("Warnings:", file=sys.stderr)
            for w in all_warnings:
                print("  * " + w, file=sys.stderr)

        print("Converted {} ACL rule(s) -> {} grant(s)".format(stats['acls_converted'], stats['grants_from_acls']))
        print("Preserved {} existing grant(s)".format(stats['existing_grants_preserved']))
        print("Total: {} grant(s) in output".format(stats['total_grants']))

        if args.dry_run:
            print("\n[DRY RUN] Output would be written to: " + (args.output or 'stdout'))
            print("\n" + "-" * 40)
            print(serialize_hujson(output_policy))
        elif args.output:
            output_path = os.path.expanduser(args.output)
            serialized = serialize_hujson(output_policy)
            with open(output_path, 'w') as f:
                f.write(serialized)
            print("\nWritten to: " + output_path)
        else:
            print("\n" + "-" * 40)
            print(serialize_hujson(output_policy))

    if all_warnings:
        sys.exit(0)  # Non-fatal warnings


if __name__ == '__main__':
    main()
