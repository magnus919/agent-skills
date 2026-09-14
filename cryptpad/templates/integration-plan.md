# CryptPad integration plan

- Instance / deployed release / evidence:
- Main origin / sandbox origin / embedding policy:
- External storage integration or existing CryptDrive workflow:
- Document app / import format / export format / conversion test:
- Authorized target and changes / rollback:
- Browser source-file access / CORS or Blob URL lifecycle:
- Plaintext boundary / client encryption and key distribution requirements:
- Durable save owner / revision checks / retry policy / visible failure state:
- Generated or application-managed session keys:
- Atomic old-key comparison / edit-view pair storage / concurrent winner response:
- Viewer authorization / view-key distribution / inactive-session behavior:
- Revocation / session migration / rejection of stale-session saves:
- Restore/export destination / retention and backup evidence:

## Acceptance evidence

| Check | Result and evidence |
|---|---|
| Two editors join the same session and converge | |
| Simultaneous first joins return one winning key | |
| Failed save remains visibly unsaved and is not acknowledged | |
| Retry cannot overwrite a newer revision | |
| Fresh session reopens the durably saved export | |
| Viewer receives no edit key and cannot mutate | |
| Revoked participant cannot obtain new-session keys or save old-session content | |
| Required document formatting/content survives import/export | |

Record tests not run and their prerequisites. Do not turn planned checks into claimed results.
