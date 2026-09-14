# CryptPad — integrate private collaborative editing

## Why Install This Skill

CryptPad can provide encrypted collaborative editors inside another application, but its
API is easy to mistake for a cloud document REST service. This skill helps your agent pick
the supported interface and identify who must store documents, authorize users and manage keys.

Your agent gets practical guidance for embedding editors, working with existing CryptDrive
documents, and diagnosing an instance. A small CLI checks public resources without executing
server JavaScript, while a browser adapter handles save acknowledgements and concurrent key updates.

## What You Get

| Directory | Contents |
|---|---|
| `scripts/` | Read-only instance probe, offline link inspector, and contract tests |
| `references/` | Architecture, API contracts, operations, and dated primary sources |
| `templates/` | Integration plan, browser configuration, and callback adapter |
| `evals/` | Output-quality scenarios and separate trigger probes |

## Quick Start

From this directory:

```sh
python3 scripts/cryptpad.py probe --origin https://cryptpad.example.org
python3 scripts/cryptpad.py inspect-link < /secure/path/document-link.txt
```

Replace the example origin with your instance. A successful probe reports `"ok": true`
and recognized config/loader endpoints; browser editing still needs separate verification.
The offline inspector returns the application and whether a fragment exists, without exposing keys.

## Triggers

- “Can CryptPad edit documents stored by our application?”
- “Build an embedded editor with reliable saves and key rotation.”
- “Why does our CryptPad instance load but collaboration fail?”
- “Export a CryptDrive document through my authorized browser session.”

## Requirements

Python 3.10+; no Python packages or API key for discovery. Editing needs a browser, an
instance permitting the required embedding, and authorized document access. Node.js runs
the optional adapter contract test. This is not a headless CryptDrive CRUD client.
