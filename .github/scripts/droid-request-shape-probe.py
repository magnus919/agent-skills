"""Temporary local-only diagnostic for Droid's first Responses request.

Never log request content, headers, or credentials. The probe does not forward
requests to a provider; it intentionally returns a 400 after logging metadata.
"""

import json
from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)
        try:
            request = json.loads(body)
        except (ValueError, UnicodeDecodeError):
            request = {}
        metadata = {
            "path": self.path,
            "keys": sorted(request),
            "model": request.get("model"),
            "reasoning": request.get("reasoning"),
            "stream": request.get("stream"),
            "tool_count": len(request.get("tools") or []),
            "tool_types": sorted({t.get("type") for t in request.get("tools") or []}),
            "input_type": type(request.get("input")).__name__,
        }
        print("DROID_REQUEST_SHAPE " + json.dumps(metadata, sort_keys=True), flush=True)
        self.send_response(400)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"error":{"message":"local diagnostic complete"}}')

    def log_message(self, format, *args):
        pass


HTTPServer(("127.0.0.1", 8765), Handler).serve_forever()
