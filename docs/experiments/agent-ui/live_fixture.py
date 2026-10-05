"""Disposable loopback UI fixture; synthetic accounts only, no model calls.

Run: python3 docs/experiments/agent-ui/live_fixture.py --store /tmp/ui-live.sqlite
Browser: http://127.0.0.1:8765/?fault=clean (or a named FAULTS value).
Each GET resets that fault's trial. Inspect SQLite effects independently after
Save; stop server with Ctrl-C. Python 3.8+, standard library only.
"""
import argparse
import json
import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

FAULTS = {'clean', 'persistence_loss', 'wrong_account', 'stale_replay',
          'duplicate_effect', 'weakened_assertion', 'required_skip'}


def serve(store):
    db = sqlite3.connect(store)
    db.execute('CREATE TABLE IF NOT EXISTS effects(fault TEXT, account TEXT, quantity INT)')

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if urlparse(self.path).path != '/':
                self.send_error(404)
                return
            fault = parse_qs(urlparse(self.path).query).get('fault', ['clean'])[0]
            if fault not in FAULTS:
                self.send_error(400)
                return
            db.execute('DELETE FROM effects WHERE fault=?', (fault,))
            db.commit()
            account = 'B' if fault == 'wrong_account' else 'A'
            button = 'Apply order' if fault == 'stale_replay' else 'Save order'
            html = f'''<!doctype html><title>Synthetic QA fixture</title>
<h1>Synthetic order</h1><p>Account: {account}</p><p>Requested quantity: 1</p>
<button onclick="fetch('/save?fault={fault}',{{method:'POST'}}).then(()=>document.getElementById('status').textContent='Saved')">{button}</button>
<p id="status" role="status">Ready</p>'''
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
            if fault != 'persistence_loss':
                for _ in range(2 if fault == 'duplicate_effect' else 1):
                    db.execute('INSERT INTO effects VALUES(?,?,?)', (fault, account, quantity))
                db.commit()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'Saved'}).encode())

        def log_message(self, *_args):
            pass

    HTTPServer(('127.0.0.1', 8765), Handler).serve_forever()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--store', required=True)
    serve(parser.parse_args().store)
