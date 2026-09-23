#!/usr/bin/env python3
"""Minimal private Laya HTTP adapter; run behind authenticated TLS ingress.

This is a reference service, not a complete production platform. It never
downloads weights: point --model-path at a pinned, pre-staged local snapshot.
"""

from __future__ import annotations

import argparse
import hmac
import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from systemone_probe import validate_request, validate_response

MAX_BODY = 64 * 1024
MAX_QUESTIONS = 16
MAX_OPTIONS = 64


class DecisionService:
    def __init__(self, agent: Any, model_path: str, expected_device: str):
        self.agent = agent
        self.model_path = model_path
        self.expected_device = expected_device
        self.lock = threading.BoundedSemaphore(1)
        self.requests = 0
        self.failures = 0

    @property
    def actual_device(self) -> str:
        return str(self.agent.device)

    def ready(self) -> bool:
        return self.actual_device == self.expected_device

    def decide(self, payload: Any) -> dict[str, Any]:
        validate_request(payload)
        questions = payload["questions"]
        if len(questions) > MAX_QUESTIONS:
            raise ValueError("too many questions")
        for qid, question in questions.items():
            if question["type"] in ("choice", "score") and len(question["criteria"]) > MAX_OPTIONS:
                raise ValueError(f"too many options for {qid}")
        if not self.ready():
            raise RuntimeError("model is not on the expected device")
        if not self.lock.acquire(blocking=False):
            raise BlockingIOError("inference worker busy")
        try:
            self.requests += 1
            result = self.agent.predict(payload["state"], questions)
            return validate_response(payload, result)
        except Exception:
            self.failures += 1
            raise
        finally:
            self.lock.release()


def make_handler(service: DecisionService, token: str):
    class Handler(BaseHTTPRequestHandler):
        server_version = "system-one-laya/1"

        def log_message(self, format: str, *args: Any) -> None:
            # The default logger includes the URL; log only the response status.
            status = args[1] if len(args) > 1 else "unknown"
            sys.stderr.write(f"laya-http status={status}\n")

        def send_json(self, status: int, data: dict[str, Any]) -> None:
            raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def authorized(self) -> bool:
            header = self.headers.get("Authorization", "")
            return hmac.compare_digest(header, "Bearer " + token)

        def do_GET(self) -> None:
            if self.path == "/healthz":
                self.send_json(200, {"alive": True})
            elif self.path == "/readyz":
                if not self.authorized():
                    self.send_json(401, {"error": "unauthorized"})
                else:
                    status = 200 if service.ready() else 503
                    self.send_json(status, {"ready": service.ready(), "device": service.actual_device, "model_path": service.model_path})
            else:
                self.send_json(404, {"error": "not found"})

        def do_POST(self) -> None:
            if self.path != "/v1/systemone":
                self.send_json(404, {"error": "not found"})
                return
            if not self.authorized():
                self.send_json(401, {"error": "unauthorized"})
                return
            try:
                length = int(self.headers.get("Content-Length", "-1"))
            except ValueError:
                length = -1
            if length < 0 or length > MAX_BODY:
                self.send_json(413, {"error": "invalid or excessive body size"})
                return
            if self.headers.get("Content-Type", "").split(";")[0] != "application/json":
                self.send_json(415, {"error": "expected application/json"})
                return
            try:
                payload = json.loads(self.rfile.read(length))
                self.send_json(200, service.decide(payload))
            except (ValueError, UnicodeDecodeError) as exc:
                self.send_json(400, {"error": str(exc)})
            except BlockingIOError:
                self.send_json(503, {"error": "worker busy"})
            except Exception:
                # No raw inference exception or state in the response.
                self.send_json(503, {"error": "inference unavailable"})

    return Handler


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-path", type=Path, required=True, help="pinned local snapshot directory")
    parser.add_argument("--device", default="cpu", help="required actual device: cpu, cuda, or mps")
    parser.add_argument("--host", default="127.0.0.1", help="bind address; use private ingress for non-loopback")
    parser.add_argument("--port", type=int, default=8788)
    args = parser.parse_args(argv)
    token = os.environ.get("SYSTEM_ONE_SERVICE_TOKEN")
    if not token or len(token) < 16:
        parser.error("SYSTEM_ONE_SERVICE_TOKEN must contain at least 16 characters")
    if not args.model_path.is_dir():
        parser.error("--model-path must be an existing local directory")
    if not (args.model_path / "rl_agent_config.json").is_file() or not (args.model_path / "model.safetensors").is_file():
        parser.error("model directory lacks Laya config or weights")
    import laya

    agent = laya.load(str(args.model_path), device=args.device)
    service = DecisionService(agent, str(args.model_path), args.device)
    if not service.ready():
        parser.error(f"requested {args.device}, but model loaded on {service.actual_device}")
    server = ThreadingHTTPServer((args.host, args.port), make_handler(service, token))
    print(json.dumps({"ready": True, "host": args.host, "port": args.port, "device": service.actual_device}), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
