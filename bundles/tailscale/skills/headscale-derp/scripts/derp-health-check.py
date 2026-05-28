#!/usr/bin/env python3
"""
headscale-derp: derp-health-check.py — Check DERP relay health.

Tests:
  - TCP connectivity to relay:3478 (STUN)
  - TLS handshake on relay:443 (DERP relay)
  - WebSocket connectivity test

Usage:
  derp-health-check.py --host <derp.example.com>
                       [--stun-port <3478>]
                       [--relay-port <443>]
                       [--json]
                       [--timeout <5>]
                       [--help]

Examples:
  derp-health-check.py --host derp.example.com
  derp-health-check.py --host derp.example.com --stun-port 3478 --relay-port 443
  derp-health-check.py --host derp.example.com --json
  derp-health-check.py --host derp.example.com --json --timeout 10
"""

import argparse
import json
import socket
import ssl
import sys
import time
import urllib.request
import urllib.error

try:
    import websocket  # optional: pip install websocket-client
except ImportError:
    websocket = None


def check_tcp_connectivity(host: str, port: int, timeout: float) -> dict:
    """Check basic TCP connectivity to a host:port."""
    result = {
        "check": "tcp_connectivity",
        "host": host,
        "port": port,
        "protocol": "tcp",
    }
    start = time.time()
    try:
        sock = socket.create_connection((host, port), timeout=timeout)
        elapsed = round((time.time() - start) * 1000, 1)
        sock.close()
        result["status"] = "ok"
        result["latency_ms"] = elapsed
        result["message"] = f"TCP connection to {host}:{port} succeeded ({elapsed}ms)"
    except (socket.timeout, ConnectionRefusedError, OSError) as e:
        elapsed = round((time.time() - start) * 1000, 1)
        result["status"] = "fail"
        result["latency_ms"] = elapsed
        result["message"] = f"TCP connection to {host}:{port} failed: {e}"
    return result


def check_tls_handshake(host: str, port: int, timeout: float) -> dict:
    """Perform a TLS handshake and return cert info."""
    result = {
        "check": "tls_handshake",
        "host": host,
        "port": port,
        "protocol": "tls",
    }
    start = time.time()
    try:
        context = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=host) as tls_sock:
                elapsed = round((time.time() - start) * 1000, 1)
                cert = tls_sock.getpeercert()
                subject = dict(x[0] for x in cert.get("subject", []))
                issuer = dict(x[0] for x in cert.get("issuer", []))
                san = cert.get("subjectAltName", [])
                result["status"] = "ok"
                result["latency_ms"] = elapsed
                result["tls_version"] = tls_sock.version()
                result["cipher"] = tls_sock.cipher()[0] if tls_sock.cipher() else None
                result["subject"] = subject.get("commonName", "?")
                result["issuer"] = issuer.get("organizationName", "?")
                result["san"] = [entry[1] for entry in san] if san else []
                result["message"] = f"TLS handshake with {host}:{port} succeeded ({elapsed}ms)"
    except (socket.timeout, ConnectionRefusedError, ssl.SSLError, OSError) as e:
        elapsed = round((time.time() - start) * 1000, 1)
        result["status"] = "fail"
        result["latency_ms"] = elapsed
        result["message"] = f"TLS handshake with {host}:{port} failed: {e}"
    return result


def check_stun(host: str, port: int, timeout: float) -> dict:
    """
    STUN connectivity check via TCP (DERP STUN).
    Sends a simple STUN binding request and checks for a response.
    """
    result = {
        "check": "stun_connectivity",
        "host": host,
        "port": port,
        "protocol": "stun",
    }
    start = time.time()
    try:
        # STUN binding request (RFC 5389) — minimal message
        # Magic cookie: 0x2112A442
        # Transaction ID: 16 random bytes
        import random

        stun_msg = bytearray(20)
        # Type: Binding Request (0x0001)
        stun_msg[0] = 0x00
        stun_msg[1] = 0x01
        # Length: 0 (empty message)
        stun_msg[2] = 0x00
        stun_msg[3] = 0x00
        # Magic cookie
        stun_msg[4] = 0x21
        stun_msg[5] = 0x12
        stun_msg[6] = 0xA4
        stun_msg[7] = 0x42
        # Transaction ID (12 random bytes)
        for i in range(12):
            stun_msg[8 + i] = random.randint(0, 255)

        sock = socket.create_connection((host, port), timeout=timeout)
        sock.sendall(bytes(stun_msg))
        response = sock.recv(1024)
        elapsed = round((time.time() - start) * 1000, 1)
        sock.close()

        if len(response) >= 20:
            # Check response type (Binding Success = 0x0101)
            resp_type = (response[0] << 8) | response[1]
            result["status"] = "ok"
            result["latency_ms"] = elapsed
            result["response_type"] = resp_type
            result["message"] = (
                f"STUN request to {host}:{port} got response "
                f"(type=0x{resp_type:04x}, {elapsed}ms)"
            )
        else:
            result["status"] = "degraded"
            result["latency_ms"] = elapsed
            result["message"] = (
                f"STUN response too short ({len(response)} bytes) "
                f"from {host}:{port}"
            )
    except (socket.timeout, ConnectionRefusedError, OSError) as e:
        elapsed = round((time.time() - start) * 1000, 1)
        result["status"] = "fail"
        result["latency_ms"] = elapsed
        result["message"] = f"STUN request to {host}:{port} failed: {e}"

    return result


def check_websocket(host: str, port: int, timeout: float) -> dict:
    """
    WebSocket connectivity test to the DERP relay endpoint.

    DERP uses a custom WebSocket-based protocol over TLS. This test
    attempts to establish a WebSocket connection to the DERP endpoint
    at /derp (the standard DERP path).
    """
    result = {
        "check": "websocket_connectivity",
        "host": host,
        "port": port,
        "protocol": "wss",
    }

    if websocket is None:
        result["status"] = "skipped"
        result["message"] = (
            "websocket-client not installed. Install with: pip install websocket-client"
        )
        return result

    start = time.time()
    ws_url = f"wss://{host}:{port}/derp"
    try:
        ws = websocket.create_connection(
            ws_url,
            timeout=timeout,
            sslopt={"check_hostname": True, "cert_reqs": ssl.CERT_REQUIRED},
        )
        elapsed = round((time.time() - start) * 1000, 1)
        ws.close()
        result["status"] = "ok"
        result["latency_ms"] = elapsed
        result["url"] = ws_url
        result["message"] = f"WebSocket connection to {ws_url} succeeded ({elapsed}ms)"
    except Exception as e:
        elapsed = round((time.time() - start) * 1000, 1)
        result["status"] = "fail"
        result["latency_ms"] = elapsed
        result["url"] = ws_url
        result["message"] = f"WebSocket connection to {ws_url} failed: {e}"

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Check DERP relay health — STUN, TLS, and WebSocket connectivity.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--host",
        required=True,
        help="DERP relay hostname (e.g., derp.example.com)",
    )
    parser.add_argument(
        "--stun-port",
        type=int,
        default=3478,
        help="STUN UDP port (default: 3478)",
    )
    parser.add_argument(
        "--relay-port",
        type=int,
        default=443,
        help="DERP relay TLS port (default: 443)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output structured JSON",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=5,
        help="Timeout in seconds for each check (default: 5)",
    )
    parser.add_argument(
        "--skip-stun",
        action="store_true",
        help="Skip STUN connectivity check",
    )

    args = parser.parse_args()

    # Run all checks
    check_results = {}

    # 1. TCP to STUN port
    tcp_stun = check_tcp_connectivity(args.host, args.stun_port, args.timeout)
    check_results["tcp_stun"] = tcp_stun

    # 2. STUN protocol check (TCP-based)
    if not args.skip_stun:
        stun = check_stun(args.host, args.stun_port, args.timeout)
        check_results["stun"] = stun
    else:
        check_results["stun"] = {
            "check": "stun_connectivity",
            "status": "skipped",
            "message": "Skipped via --skip-stun",
        }

    # 3. TCP to relay port
    tcp_relay = check_tcp_connectivity(args.host, args.relay_port, args.timeout)
    check_results["tcp_relay"] = tcp_relay

    # 4. TLS handshake on relay port
    tls = check_tls_handshake(args.host, args.relay_port, args.timeout)
    check_results["tls"] = tls

    # 5. WebSocket connectivity
    ws = check_websocket(args.host, args.relay_port, args.timeout)
    check_results["websocket"] = ws

    # Determine overall status
    critical_checks = ["tcp_stun", "tls", "tcp_relay"]
    failures = [
        k for k in critical_checks
        if check_results.get(k, {}).get("status") == "fail"
    ]
    warnings = [
        k for k in check_results
        if check_results.get(k, {}).get("status") == "degraded"
    ]
    skipped = [
        k for k in check_results
        if check_results.get(k, {}).get("status") == "skipped"
    ]

    if not failures:
        overall_status = "healthy"
    elif len(failures) < len(critical_checks):
        overall_status = "degraded"
    else:
        overall_status = "unhealthy"

    summary_lines = []
    summary_lines.append(f"Host: {args.host}")
    summary_lines.append(f"Overall: {overall_status}")
    if failures:
        summary_lines.append(f"Failed: {', '.join(failures)}")
    if warnings:
        summary_lines.append(f"Degraded: {', '.join(warnings)}")
    if skipped:
        summary_lines.append(f"Skipped: {', '.join(skipped)}")

    if args.json:
        output = {
            "status": overall_status,
            "host": args.host,
            "summary": {
                "total": len(check_results),
                "ok": sum(
                    1 for c in check_results.values() if c.get("status") == "ok"
                ),
                "degraded": len(warnings),
                "fail": len(failures),
                "skipped": len(skipped),
            },
            "checks": check_results,
        }
        print(json.dumps(output, indent=2))
    else:
        print("=" * 60)
        print(f"  DERP Health Check — {args.host}")
        print("=" * 60)
        for check_name, result in check_results.items():
            status = result.get("status", "unknown")
            if status == "ok":
                status_str = f"   {GREEN}OK{NC}" if _use_color() else "   OK"
            elif status == "degraded":
                status_str = f" {YELLOW}DEGRADED{NC}" if _use_color() else " DEGRADED"
            elif status == "skipped":
                status_str = f" {CYAN}SKIPPED{NC}" if _use_color() else " SKIPPED"
            else:
                status_str = f"  {RED}FAIL{NC}" if _use_color() else "  FAIL"

            print(f"  {check_name:20s} {status_str}")
            print(f"    {result.get('message', '')}")
            if result.get("latency_ms") is not None:
                print(f"    Latency: {result['latency_ms']}ms")
            if result.get("tls_version"):
                print(f"    TLS: {result['tls_version']} / Cipher: {result.get('cipher', '?')}")
            if result.get("subject"):
                print(f"    Cert CN: {result['subject']} / Issuer: {result.get('issuer', '?')}")
            print()

        print("-" * 60)
        print(f"  Overall: {overall_status}")
        print("=" * 60)


def _use_color():
    return sys.stderr.isatty()


# ANSI color helpers (for text output)
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
CYAN = "\033[0;36m"
NC = "\033[0m"


if __name__ == "__main__":
    main()
