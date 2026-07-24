# Permit and Development Portal Reference

The City of Raleigh provides a guest-public self-service portal for permit,
plan, inspection, code case, request, license, and project searches. The adapter
discovers which of these record types are currently advertised by the runtime
criteria response and fails explicitly on incompatible criteria or result schemas.

## Base URL

```text
https://raleighnc-energovpub.tylerhost.net/apps/selfservice
```

The public entry point redirects from:

```text
https://permitportal.raleighnc.gov/
```

## Guest Endpoints

The adapter uses only the following guest-visible read-only endpoints:

- `/api/energov/search/criteria`
- `POST /api/energov/search/search`
- `GET /api/energov/permits/{permit-uuid}`
- `POST /api/energov/entity/inspections/search/search`

The two POST operations are guest-public searches. The shared HTTP policy
allowlists their exact paths and rejects other non-GET requests.

## Notes

- These endpoints are part of the public Tyler EnerGov Citizen Self Service application, not a documented open-data contract.
- The adapter is isolated from ArcGIS commands so upstream changes do not break dataset queries.
- No authenticated, write, payment, or private-contact endpoint is called.
- Output is limited to fields visible to an unauthenticated visitor.
- Set `RALEIGH_DISABLE_DEVELOPMENT=1` to disable this isolated adapter if the
  upstream guest contract changes, without disabling other Raleigh commands.
