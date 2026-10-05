"""Exercise real HTTP parsing, SQLite state and resource ownership without sockets."""
import importlib.util
import io
import sqlite3
from pathlib import Path
from unittest.mock import patch

import pytest

spec = importlib.util.spec_from_file_location('live_fixture', Path(__file__).with_name('live_fixture.py'))
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)


class RequestSocket:
    def __init__(self, method, path):
        self.request = io.BytesIO(f'{method} {path} HTTP/1.0\r\nHost: localhost\r\n\r\n'.encode())
        self.response = io.BytesIO()

    def makefile(self, *_args):
        return self.request

    def sendall(self, data):
        self.response.write(data)


def request(db, method, path):
    sock = RequestSocket(method, path)
    fixture.make_handler(db)(sock, ('127.0.0.1', 0), object())
    raw = sock.response.getvalue()
    header, body = raw.split(b'\r\n\r\n', 1)
    return int(header.split(b' ')[1]), body


@pytest.fixture
def db():
    connection = sqlite3.connect(':memory:')
    connection.execute('CREATE TABLE effects(fault TEXT, account TEXT, quantity INT)')
    yield connection
    connection.close()


@pytest.mark.parametrize('method,path', [('GET', '/?fault=required_skip'), ('POST', '/save?fault=required_skip')])
def test_offline_only_case_rejected_without_effect(db, method, path):
    status, _ = request(db, method, path)
    assert status == 400
    assert db.execute('SELECT * FROM effects').fetchall() == []


@pytest.mark.parametrize('method,path', [('GET', '/?fault=clean'), ('POST', '/save?fault=clean')])
def test_storage_error_has_explicit_http_failure_and_diagnostic(db, method, path, capsys):
    db.execute('DROP TABLE effects')
    status, body = request(db, method, path)
    assert status == 500
    assert body == b'{"status":"storage_error"}'
    assert 'OperationalError' in capsys.readouterr().err
    assert b'Saved' not in body


@pytest.mark.parametrize('fault,expected', [
    ('clean', [('clean', 'A', 1)]),
    ('persistence_loss', []),
    ('duplicate_effect', [('duplicate_effect', 'A', 1), ('duplicate_effect', 'A', 1)]),
    ('weakened_assertion', [('weakened_assertion', 'A', 2)]),
])
def test_success_presentation_and_independent_state_remain_distinct(db, fault, expected):
    status, body = request(db, 'POST', '/save?fault=' + fault)
    assert status == 200
    assert b'Saved' in body
    assert db.execute('SELECT * FROM effects').fetchall() == expected


def test_transaction_rolls_back_partial_duplicate_write(db, capsys):
    db.execute('CREATE UNIQUE INDEX one_operation ON effects(fault)')
    status, _ = request(db, 'POST', '/save?fault=duplicate_effect')
    assert status == 500
    assert db.execute('SELECT * FROM effects').fetchall() == []
    assert 'IntegrityError' in capsys.readouterr().err


def test_shutdown_closes_store_and_server_after_interrupt():
    connection = sqlite3.connect(':memory:')
    with patch.object(fixture.sqlite3, 'connect', return_value=connection), patch.object(fixture, 'HTTPServer') as server:
        server.return_value.__enter__.return_value.serve_forever.side_effect = KeyboardInterrupt
        with pytest.raises(KeyboardInterrupt):
            fixture.serve(':memory:')
        assert server.return_value.__exit__.call_count == 1
    with pytest.raises(sqlite3.ProgrammingError):
        connection.execute('SELECT 1')
