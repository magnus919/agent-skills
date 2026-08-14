#!/usr/bin/env python3
"""
ts-connectivity-report.py — Interpret Tailscale diagnostics into a structured report.

Reads the JSON output from ts-diagnostics.sh and produces a structured report
analyzing peer connectivity, path types (direct vs DERP relay), latency tiers,
exit node status, and MagicDNS health.

Usage:
    ./ts-connectivity-report.py --diagnostics <diagnostics.json>
    ./ts-connectivity-report.py --diagnostics diagnostics.json --json

Options:
    --diagnostics <path>   Path to JSON diagnostics file from ts-diagnostics.sh
    --json                 Output results in JSON format
    --help                 Show this help message and exit
"""

import json
import sys
import os
import re
from datetime import datetime


def usage():
    print(__doc__.strip())
    sys.exit(0)


def parse_args():
    args = {
        "diagnostics": None,
        "json_output": False,
    }
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--diagnostics" and i + 1 < len(sys.argv):
            args["diagnostics"] = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--json":
            args["json_output"] = True
            i += 1
        elif sys.argv[i] == "--help":
            usage()
        else:
            print(f"Unknown option: {sys.argv[i]}", file=sys.stderr)
            usage()
    return args


def load_diagnostics(path):
    """Load and validate the diagnostics JSON file."""
    if not os.path.exists(path):
        print(f"Error: diagnostics file not found: {path}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(path, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON in diagnostics file: {e}", file=sys.stderr)
        sys.exit(1)

    return data


def analyze_peers(diagnostics):
    """Analyze each peer for connectivity type and health."""
    peer_analysis = diagnostics.get("peer_analysis", [])
    status = diagnostics.get("status", {})
    peers_raw = status.get("Peer", {})

    results = []

    for peer in peer_analysis:
        hostname = peer.get("hostname", "unknown")
        dns_name = peer.get("dns_name", "")
        ips = peer.get("tailscale_ips", [])
        online = peer.get("online", False)
        primary_path = peer.get("primary_path", "unknown")
        relay_server = peer.get("relay_server", "")
        tx = peer.get("tx_bytes", 0)
        rx = peer.get("rx_bytes", 0)

        entry = {
            "hostname": hostname,
            "dns_name": dns_name,
            "tailscale_ips": ips,
            "online": online,
            "path_type": primary_path,
            "relay_server": relay_server,
            "traffic_bytes": {"tx": tx, "rx": rx},
            "latency_ms": None,
            "health": "unknown",
        }

        # Determine health
        if not online:
            entry["health"] = "offline"
        elif primary_path == "direct":
            entry["health"] = "healthy"
        elif primary_path == "relay":
            entry["health"] = "derp_relay"
        else:
            entry["health"] = "unknown"

        # Check for ping results matching this peer
        ping_results = diagnostics.get("ping_results", [])
        for ping in ping_results:
            target = ping.get("target", "")
            if (
                target in ips
                or target == hostname
                or target == hostname + "." + dns_name
            ):
                entry["latency_ms"] = ping.get("latency_ms")
                if ping.get("path_type") == "direct":
                    entry["path_type"] = "direct"
                    if entry["health"] == "derp_relay":
                        entry["health"] = "healthy"  # real-time ping confirms direct

        # Latency tier
        lat = entry["latency_ms"]
        if lat is not None:
            if lat < 10:
                entry["latency_tier"] = "green"
            elif lat < 50:
                entry["latency_tier"] = "yellow"
            else:
                entry["latency_tier"] = "red"
        else:
            entry["latency_tier"] = "unknown"

        results.append(entry)

    return results


def analyze_netcheck(diagnostics):
    """Analyze netcheck results."""
    netcheck = diagnostics.get("netcheck", {})
    if isinstance(netcheck, str):
        return {"raw_output": netcheck}

    report = {
        "udp_enabled": netcheck.get("UDP", True),
        "ipv4": netcheck.get("IPv4", False),
        "ipv6": netcheck.get("IPv6", False),
        "mapping_varies_by_dest": netcheck.get("MappingVariesByDest", None),
        "hair_pinning": netcheck.get("HairPinning", None),
        "captive_portal": netcheck.get("CaptivePortal", False),
        "global_derp_latency": {},
        "preferred_derp": netcheck.get("PreferredDERP", None),
    }

    # Parse DERP region latencies
    derp_map = netcheck.get("DERPMap", {})
    regions = derp_map.get("Regions", []) if isinstance(derp_map, dict) else []
    if isinstance(derp_map, dict):
        regions_obj = derp_map.get("Regions", {})
        if isinstance(regions_obj, dict):
            for region_id, region in regions_obj.items():
                if isinstance(region, dict):
                    report["global_derp_latency"][region.get("RegionName", f"Region{region_id}")] = {
                        "region_id": region_id,
                        "latency_ms": region.get("Latency", {}),
                    }

    # Also check top-level latency keys
    latency = netcheck.get("Latency", {})
    if isinstance(latency, dict):
        for region_name, lat_data in latency.items():
            if region_name not in report["global_derp_latency"]:
                report["global_derp_latency"][region_name] = lat_data

    return report


def analyze_exit_nodes(peer_analysis):
    """Check if any peers are exit nodes."""
    # This is a best-effort analysis from diagnostics data
    exit_nodes = [p for p in peer_analysis if "exit" in p.get("hostname", "").lower()]
    return {
        "exit_nodes_found": len(exit_nodes),
        "exit_nodes": exit_nodes,
    }


def analyze_magicdns(diagnostics):
    """Check MagicDNS health based on DNS names."""
    peer_analysis = diagnostics.get("peer_analysis", [])
    self_info = diagnostics.get("self", {})

    dns_names = []
    for peer in peer_analysis:
        dns = peer.get("dns_name", "")
        if dns:
            dns_names.append(dns)

    self_dns = self_info.get("dns_name", "")

    # MagicDNS is considered healthy if we have DNS names with a tailnet suffix
    has_dns_names = len(dns_names) > 0 or bool(self_dns)

    return {
        "magicdns_enabled": has_dns_names,
        "peers_with_dns": len(dns_names),
        "self_dns_name": self_dns,
        "sample_dns_names": dns_names[:5] if dns_names else [],
        "status": "healthy" if has_dns_names else "not_configured",
    }


def analyze_version(diagnostics):
    """Analyze version consistency."""
    version = diagnostics.get("version", {})
    client = version.get("client", "")
    daemon = version.get("daemon", "")

    version_match = client == daemon or not daemon
    return {
        "client_version": client,
        "daemon_version": daemon,
        "versions_match": version_match,
        "status": "consistent" if version_match else "mismatch",
    }


def generate_summary(peer_analysis, netcheck_report, magicdns, version_report):
    """Generate a summary with key findings."""
    total_peers = len(peer_analysis)
    online_peers = sum(1 for p in peer_analysis if p.get("online"))
    offline_peers = sum(1 for p in peer_analysis if not p.get("online"))
    direct_peers = sum(1 for p in peer_analysis if p.get("path_type") == "direct")
    relay_peers = sum(1 for p in peer_analysis if p.get("path_type") == "relay")
    green_peers = sum(1 for p in peer_analysis if p.get("latency_tier") == "green")
    yellow_peers = sum(1 for p in peer_analysis if p.get("latency_tier") == "yellow")
    red_peers = sum(1 for p in peer_analysis if p.get("latency_tier") == "red")

    issues = []

    if offline_peers > 0:
        offline_names = [
            p["hostname"] for p in peer_analysis if not p.get("online")
        ]
        issues.append(
            f"Offline peers ({offline_peers}): {', '.join(offline_names)}"
        )

    if relay_peers > 0:
        relay_names = [
            p["hostname"]
            for p in peer_analysis
            if p.get("path_type") == "relay"
        ]
        issues.append(
            f"Peers on DERP relay ({relay_peers}): {', '.join(relay_names)}. "
            "NAT traversal may need investigation."
        )

    if red_peers > 0:
        red_names = [
            p["hostname"]
            for p in peer_analysis
            if p.get("latency_tier") == "red"
        ]
        issues.append(
            f"High-latency peers ({red_peers}): {', '.join(red_names)}"
        )

    if not netcheck_report.get("udp_enabled", True):
        issues.append("UDP is blocked or disabled — DERP relay may be the only option")

    if not magicdns.get("magicdns_enabled"):
        issues.append(
            "MagicDNS not configured or no DNS names found. "
            "Run tailscale up with --accept-dns to enable."
        )

    if not version_report.get("versions_match"):
        issues.append(
            f"Version mismatch: client={version_report['client_version']}, "
            f"daemon={version_report['daemon_version']}"
        )

    summary = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "total_peers": total_peers,
        "online_peers": online_peers,
        "offline_peers": offline_peers,
        "direct_connections": direct_peers,
        "relay_connections": relay_peers,
        "latency_tiers": {
            "green": green_peers,
            "yellow": yellow_peers,
            "red": red_peers,
        },
        "issues": issues,
        "health": "healthy" if len(issues) == 0 else "degraded",
    }

    return summary


def format_human_report(
    summary, peer_analysis, netcheck_report, magicdns, version_report, exit_node_report
):
    """Format a human-readable report."""
    lines = []
    lines.append("=" * 60)
    lines.append("  Tailscale Connectivity Report")
    lines.append(f"  Generated: {summary['timestamp']}")
    lines.append("=" * 60)
    lines.append("")

    # Summary
    lines.append("--- Summary ---")
    health_color = (
        "\033[32mhealthy\033[0m"
        if summary["health"] == "healthy"
        else "\033[31mdegraded\033[0m"
    )
    lines.append(f"  Overall Health: {health_color}")
    lines.append(
        f"  Peers: {summary['online_peers']}/{summary['total_peers']} online "
        f"({summary['offline_peers']} offline)"
    )
    lines.append(
        f"  Connections: {summary['direct_connections']} direct, "
        f"{summary['relay_connections']} via DERP relay"
    )
    lines.append("  Latency Tiers:")
    lines.append(f"    \033[32m<10ms (green):\033[0m  {summary['latency_tiers']['green']}")
    lines.append(f"    \033[33m10-50ms (yellow):\033[0m {summary['latency_tiers']['yellow']}")
    lines.append(f"    \033[31m>50ms (red):\033[0m   {summary['latency_tiers']['red']}")
    lines.append("")

    # Issues
    if summary["issues"]:
        lines.append("\033[31m--- Issues Found ---\033[0m")
        for issue in summary["issues"]:
            lines.append(f"  ⚠  {issue}")
        lines.append("")
    else:
        lines.append("\033[32mNo issues found.\033[0m")
        lines.append("")

    # Peer Details
    lines.append("--- Peer Details ---")
    tier_color_map = {
        "green": "\033[32m",
        "yellow": "\033[33m",
        "red": "\033[31m",
        "unknown": "\033[90m",
    }
    for peer in peer_analysis:
        hostname = peer.get("hostname", "?")
        ips = ", ".join(peer.get("tailscale_ips", []))
        online = "\033[32mONLINE\033[0m" if peer.get("online") else "\033[31mOFFLINE\033[0m"
        path = peer.get("path_type", "?")
        if path == "direct":
            path_str = "\033[32mdirect\033[0m"
        elif path == "relay":
            relay = peer.get("relay_server", "")
            path_str = f"\033[33mrelay ({relay})\033[0m"
        else:
            path_str = f"\033[90m{path}\033[0m"

        lat = peer.get("latency_ms")
        tier = peer.get("latency_tier", "unknown")
        lat_color = tier_color_map.get(tier, "\033[90m")
        lat_str = f"{lat_color}{lat}ms\033[0m" if lat is not None else "\033[90m?\033[0m"

        lines.append(f"  {hostname:25} {ips:20} {online:8} Path: {path_str:20} Latency: {lat_str}")
    lines.append("")

    # Netcheck
    lines.append("--- Netcheck ---")
    lines.append(f"  UDP enabled:    {netcheck_report.get('udp_enabled', '?')}")
    lines.append(f"  IPv4:           {netcheck_report.get('ipv4', '?')}")
    lines.append(f"  IPv6:           {netcheck_report.get('ipv6', '?')}")
    lines.append(
        f"  Captive portal: {netcheck_report.get('captive_portal', '?')}"
    )
    pref_derp = netcheck_report.get("preferred_derp")
    lines.append(f"  Preferred DERP: {pref_derp if pref_derp else 'none'}")
    if netcheck_report.get("global_derp_latency"):
        lines.append("  DERP Latencies:")
        for region, lat_data in netcheck_report["global_derp_latency"].items():
            if isinstance(lat_data, dict):
                lat_val = lat_data.get("latency_ms", "?")
            elif isinstance(lat_data, (int, float)):
                lat_val = lat_data
            else:
                lat_val = "?"
            lines.append(f"    {region}: {lat_val}ms")
    lines.append("")

    # MagicDNS
    lines.append("--- MagicDNS ---")
    mdns_status = magicdns.get("status", "unknown")
    mdns_color = "\033[32m" if mdns_status == "healthy" else "\033[33m"
    lines.append(f"  Status:       {mdns_color}{mdns_status}\033[0m")
    lines.append(f"  Peers w/ DNS: {magicdns.get('peers_with_dns', 0)}")
    lines.append(f"  Self DNS:     {magicdns.get('self_dns_name', 'none')}")
    lines.append("")

    # Version
    lines.append("--- Version ---")
    ver_match = version_report.get("status", "unknown")
    ver_color = "\033[32m" if ver_match == "consistent" else "\033[31m"
    lines.append(f"  Client:  {version_report.get('client_version', '?')}")
    lines.append(f"  Daemon:  {version_report.get('daemon_version', '?')}")
    lines.append(f"  Match:   {ver_color}{ver_match}\033[0m")
    lines.append("")

    # Exit Nodes
    lines.append("--- Exit Nodes ---")
    if exit_node_report.get("exit_nodes_found", 0) > 0:
        for en in exit_node_report.get("exit_nodes", []):
            lines.append(f"  {en.get('hostname', '?')} — {', '.join(en.get('tailscale_ips', []))}")
    else:
        lines.append("  No exit nodes detected from available data.")
    lines.append("")

    lines.append("=" * 60)
    return "\n".join(lines)


def main():
    args = parse_args()

    if not args["diagnostics"]:
        print("Error: --diagnostics <path> is required", file=sys.stderr)
        usage()

    diagnostics = load_diagnostics(args["diagnostics"])

    peer_analysis = analyze_peers(diagnostics)
    netcheck_report = analyze_netcheck(diagnostics)
    exit_node_report = analyze_exit_nodes(peer_analysis)
    magicdns_report = analyze_magicdns(diagnostics)
    version_report = analyze_version(diagnostics)
    summary = generate_summary(
        peer_analysis, netcheck_report, magicdns_report, version_report
    )

    if args["json_output"]:
        output = {
            "summary": summary,
            "peers": peer_analysis,
            "netcheck": netcheck_report,
            "magicdns": magicdns_report,
            "version": version_report,
            "exit_nodes": exit_node_report,
        }
        print(json.dumps(output, indent=2))
    else:
        print(
            format_human_report(
                summary,
                peer_analysis,
                netcheck_report,
                magicdns_report,
                version_report,
                exit_node_report,
            )
        )


if __name__ == "__main__":
    main()
