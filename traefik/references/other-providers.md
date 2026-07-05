# Other Providers Reference

Beyond Docker and Kubernetes, Traefik supports several other infrastructure providers for automatic service discovery.

## AWS ECS Provider

Discovers services from Amazon ECS clusters using task definition labels.

### Configuration

```yaml
providers:
  ecs:
    clusters: ["default"]                  # Clusters to watch
    autoDiscoverClusters: false            # Auto-discover all clusters
    exposedByDefault: true                 # Auto-expose services (set false for security)
    defaultRule: "Host(`{{ normalize .Name }}`)"
    constraints: ""                        # Label filter expressions
    healthyTasksOnly: false                # Only discover healthy tasks
    ecsAnywhere: false                     # Enable ECS Anywhere support
    refreshSeconds: 15
    region: ""                             # AWS region
    accessKeyID: ""                        # AWS access key (or use IAM role)
    secretAccessKey: ""                    # AWS secret key
```

### Label Syntax

Uses Docker labels on ECS task definitions:

```json
{
  "containerDefinitions": [{
    "name": "my-app",
    "dockerLabels": {
      "traefik.enable": "true",
      "traefik.http.routers.app.rule": "Host(`app.example.com`)",
      "traefik.http.services.app.loadbalancer.server.port": "8080"
    }
  }]
}
```

- Labels use the same syntax as Docker provider labels
- ECS identifies services by task definition labels
- IAM roles preferred over static credentials for production

## HashiCorp Nomad Provider

Discovers services from Nomad using service tags.

### Configuration

```yaml
providers:
  nomad:
    endpoint:
      address: "http://127.0.0.1:4646"
      region: ""                            # Nomad region
      token: ""                             # ACL token
      endpointWaitTime: 0s
      tls:
        ca: ""
        cert: ""
        key: ""
        insecureSkipVerify: false
    namespaces: []                          # Discover services in these namespaces
    prefix: "traefik"                       # Tag prefix
    exposedByDefault: true
    defaultRule: "Host(`{{ normalize .Name }}`)"
    constraints: ""
    allowEmptyServices: false
    refreshInterval: 15s
    stale: false                            # Allow stale reads for performance
    watch: false                            # Watch for events (vs polling)
```

### Tag Syntax

Uses Consul-style tags on Nomad services:

```hcl
service {
  name = "my-app"
  tags = [
    "traefik.http.routers.app.rule=Host(`app.example.com`)",
    "traefik.http.services.app.loadbalancer.server.port=80",
  ]
}
```

## HashiCorp Consul Catalog Provider

Discovers services from Consul's service catalog.

### Configuration

```yaml
providers:
  consulCatalog:
    endpoint:
      address: "127.0.0.1:8500"
      scheme: "http"
      datacenter: ""
      token: ""
      endpointWaitTime: 0s
      tls:
        ca: ""
        cert: ""
        key: ""
        insecureSkipVerify: false
      httpAuth:
        username: ""
        password: ""
    prefix: "traefik"
    exposedByDefault: true
    defaultRule: "Host(`{{ normalize .Name }}`)"
    constraints: ""
    connectAware: false                     # Support Consul Connect
    connectByDefault: false
    serviceName: ""
    refreshInterval: 0s
    requireConsistent: false
    stale: false
    cache: true
    watch: true
    namespaces: []                          # Consul Enterprise namespaces
```

## KV Store Providers (Redis, Consul, etcd, ZooKeeper)

Traefik can read dynamic configuration from key-value stores. The configuration is stored as JSON under a root key.

### Redis

```yaml
providers:
  redis:
    rootKey: "traefik"
    endpoints: ["127.0.0.1:6379"]
    username: ""
    password: ""
    db: 0
    tls:
      ca: ""
      cert: ""
      key: ""
      insecureSkipVerify: false
    sentinel:
      masterName: ""
      username: ""
      password: ""
      latencyStrategy: false
      randomStrategy: false
      replicaStrategy: false
      useDisconnectedReplicas: false
```

### Consul

```yaml
providers:
  consul:
    rootKey: "traefik"
    endpoints: ["127.0.0.1:8500"]
    token: ""
    namespaces: []
    tls:
      ca: ""
      cert: ""
      key: ""
      insecureSkipVerify: false
```

### etcd

```yaml
providers:
  etcd:
    rootKey: "traefik"
    endpoints: ["127.0.0.1:2379"]
    username: ""
    password: ""
    tls:
      ca: ""
      cert: ""
      key: ""
      insecureSkipVerify: false
```

### ZooKeeper

```yaml
providers:
  zooKeeper:
    rootKey: "traefik"
    endpoints: ["127.0.0.1:2181"]
    username: ""
    password: ""
```

### KV Store Data Format

The value at the root key must be a JSON representation of Traefik's dynamic configuration:

```json
{
  "http": {
    "routers": {
      "my-router": {
        "rule": "Host(`example.com`)",
        "service": "my-service"
      }
    },
    "services": {
      "my-service": {
        "loadBalancer": {
          "servers": [{"url": "http://10.0.0.1:80"}]
        }
      }
    }
  }
}
```

## File Provider

For static/dynamic config managed as files (no service discovery). The most commonly used non-discovery provider.

```yaml
providers:
  file:
    directory: "/etc/traefik/dynamic/"    # Watch this directory
    watch: true                            # Auto-reload on changes
    filename: ""                           # Single file (alternative to directory)
    debugLogGeneratedTemplate: false
```

Files must have `.yml`, `.yaml`, or `.toml` extension. They are merged alphabetically.

## HTTP Provider

Fetches dynamic configuration from an HTTP(S) endpoint.

```yaml
providers:
  http:
    endpoint: "http://config-server:8080/traefik-config"
    pollInterval: 5s
    pollTimeout: 30s
    headers:                               # Custom request headers
      Authorization: "Bearer my-token"
    tls:
      ca: ""
      cert: ""
      key: ""
      insecureSkipVerify: false
```

## REST Provider

Accepts dynamic configuration updates via a REST API endpoint.

```yaml
providers:
  rest:
    insecure: false                        # Expose on Traefik's entryPoint
```

The REST provider exposes `PUT /api/providers/rest` to accept dynamic configuration updates.

## Provider Precedence

When multiple providers define the same router/service, the `providers.precedence` option determines which wins:

```yaml
providers:
  precedence:
    - "docker"
    - "kubernetesCRD"
    - "file"
    - "rest"
```

Providers listed first have higher priority. If not configured, the order is: plugin → http → docker/ecs/consulCatalog/nomad/rancher → marathon → kubernetes → rest → file → consul/etcd/zooKeeper/redis.

## Watching Multiple Providers

Traefik can run multiple providers simultaneously. This is common for hybrid setups (Docker + File provider for shared middlewares):

```yaml
providers:
  docker:
    endpoint: "unix:///var/run/docker.sock"
    exposedByDefault: false
  file:
    directory: "/etc/traefik/dynamic/"
    watch: true
```

Resources from different providers are isolated by their provider namespace. Reference cross-provider resources using the `@provider` suffix (e.g., `my-middleware@file`).
