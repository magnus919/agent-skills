# Headscale REST API Reference

Base URL: `https://<headscale.example.com>/api/v1`
Auth: `Authorization: Bearer <API_KEY>`
Content-Type: `application/json`

## Users

### List all users
```
GET /api/v1/user
```
Response: `{"users": [{"id": "...", "name": "alice", "created_at": "..."}]}`

### Get specific user
```
GET /api/v1/user?name=alice
```

### Create user
```
POST /api/v1/user
{"name": "alice"}
```

### Delete user
```
DELETE /api/v1/user/<id>
```

## Pre-auth Keys

### Create pre-auth key
```
POST /api/v1/preauthkey
{
  "user": "alice",
  "expiration": "2026-01-01T00:00:00Z",
  "reusable": false,
  "ephemeral": false,
  "tags": ["tag:server"]
}
```
Response: `{"preauthkey": {"key": "mkey-...", "id": "...", "expiration": "..."}}`

### List pre-auth keys for user
```
GET /api/v1/preauthkey?user=alice
```

### Expire pre-auth key
```
DELETE /api/v1/preauthkey/<id>
```

## Node Registration & Management

### Register a web-authenticated node
```
POST /api/v1/auth/register
{"user": "alice", "authId": "<auth-id-from-browser>"}
```

### List nodes
```
GET /api/v1/node
GET /api/v1/node?user=alice
```
Response: `{"nodes": [{"id": "...", "name": "...", "ip_addresses": ["100.x.y.z"], "tags": ["tag:server"], "online": true, "last_seen": "...", "expiry": "...", "created_at": "..."}]}`

### Get node by ID
```
GET /api/v1/node/<id>
```

### Delete node
```
DELETE /api/v1/node/<id>
```

### Tag a node
```
POST /api/v1/node/<id>/tags
{"tags": ["tag:server", "tag:prod"]}
```

### Move node to user
```
POST /api/v1/node/<id>/user
{"user": "bob"}
```

### Set node tags (replace all)
```
POST /api/v1/node/<id>/tags
{"tags": ["tag:server"]}
```

### Rename node
```
POST /api/v1/node/<id>/rename
{"name": "new-name"}
```

## Routes

### List routes
```
GET /api/v1/route
```
Response: `{"routes": [{"id": "...", "node_id": "...", "prefix": "192.168.1.0/24", "advertised": true, "enabled": false, "is_primary": false}]}`

### Enable route
```
POST /api/v1/route/<id>/enable
```

### Disable route
```
POST /api/v1/route/<id>/disable
```

### Delete route
```
DELETE /api/v1/route/<id>
```

## API Keys (self-management)

### List API keys
```
GET /api/v1/apikey
```

### Expire API key
```
DELETE /api/v1/apikey/<prefix>
```

## Health & Diagnostics

### Health check
```
GET /health
```
Response: Health status (varies by deployment)

### Version
```
GET /version
```
Response: Headscale version string

### Swagger documentation
```
GET /swagger
```
Response: Interactive API documentation

## Error Responses

All endpoints return standard HTTP codes:
- 200: Success
- 400: Bad request (validation error)
- 401: Unauthorized (bad or missing API key)
- 404: Resource not found
- 500: Internal server error

Error body: `{"message": "error description", "details": {...}}`
