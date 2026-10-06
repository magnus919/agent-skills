"""Disposable loopback UI fixture; synthetic accounts only, no model calls.

Run: python3 docs/experiments/agent-ui/live_fixture.py --store /tmp/ui-live.sqlite
Browser: http://127.0.0.1:8765/?fault=clean (or a named FAULTS value).
Each GET resets that fault's trial. Inspect SQLite effects independently after
Save; stop server with Ctrl-C. Python 3.8+, standard library only.
Required-skip injection belongs to synthetic_matrix.py, not this live fixture.
"""
import argparse
import json
import sqlite3
import sys
from contextlib import closing
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

FAULTS = {'clean', 'persistence_loss', 'wrong_account', 'stale_replay',
          'duplicate_effect', 'weakened_assertion'}


def make_handler(db):
    class Handler(BaseHTTPRequestHandler):
        def storage_failure(self, error):
            # Preserve diagnostic category without disclosing a store path.
            print(json.dumps({'event': 'storage_error', 'kind': type(error).__name__}), file=sys.stderr)
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status":"storage_error"}')

        def do_GET(self):
            if urlparse(self.path).path != '/':
                self.send_error(404)
                return
            fault = parse_qs(urlparse(self.path).query).get('fault', ['clean'])[0]
            if fault not in FAULTS:
                self.send_error(400)
                return
            try:
                with db:
                    db.execute('DELETE FROM effects WHERE fault=?', (fault,))
            except sqlite3.Error as error:
                self.storage_failure(error)
                return
            account = 'B' if fault == 'wrong_account' else 'A'
            button = 'Apply order' if fault == 'stale_replay' else 'Save order'
            html = f'''<!doctype html><title>Synthetic QA fixture</title>
<h1>Synthetic order</h1><p>Account: {account}</p><p>Requested quantity: 1</p>
<button onclick="saveOrder()">{button}</button>
<p id="status" role="status">Ready</p>
<script>
async function saveOrder() {{
  const status = document.getElementById('status');
  try {{
    const response = await fetch('/save?fault={fault}', {{method:'POST'}});
    status.textContent = response.ok ? 'Saved' : 'Storage error';
  }} catch (error) {{ status.textContent = 'Request failed'; }}
}}
</script>'''
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode())

        def do_POST(self):
            fault = parse_qs(urlparse(self.path).query).get('fault', ['clean'])[0]
            if fault not in FAULTS or urlparse(self.path).path != '/save':
                self.send_error(400)
                return
            account = 'B' if fault == 'wrong_account' else 'A'
            quantity = 2 if fault == 'weakened_assertion' else 1
            try:
                if fault != 'persistence_loss':
                    with db:
                        for _ in range(2 if fault == 'duplicate_effect' else 1):
                            db.execute('INSERT INTO effects VALUES(?,?,?)', (fault, account, quantity))
            except sqlite3.Error as error:
                self.storage_failure(error)
                return
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'Saved'}).encode())

        def log_message(self, *_args):
            pass

    return Handler


def serve(store):
    with closing(sqlite3.connect(store)) as db:
        db.execute('CREATE TABLE IF NOT EXISTS effects(fault TEXT, account TEXT, quantity INT)')
        db.commit()
        with HTTPServer(('127.0.0.1', 8765), make_handler(db)) as server:
            server.serve_forever()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--store', required=True)
    try:
        serve(parser.parse_args().store)
    except KeyboardInterrupt:
        pass
