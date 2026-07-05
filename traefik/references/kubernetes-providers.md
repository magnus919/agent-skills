# Kubernetes Provider Reference

Traefik acts as a fully-featured Kubernetes Ingress controller. It supports three Kubernetes provider modes: standard Ingress, CRD (Custom Resource Definitions), and Gateway API.

## Architecture Overview

When running inside Kubernetes, Traefik auto-detects the cluster:
- Reads `KUBERNETES_SERVICE_HOST` and `KUBERNETES_SERVICE_PORT` env vars
- Uses service account token from `/var/run/secrets/kubernetes.io/serviceaccount/token`
- Uses CA cert from `/var/run/secrets/kubernetes.io/serviceaccount/ca.crt`
- Each provider watches for Kubernetes resource events (create, update, delete) in real-time

For external-cluster access, set `endpoint` to the API server URL.

## Provider: Kubernetes Ingress

Standard Kubernetes Ingress controller. Uses the native `Ingress` resource with annotations for Traefik-specific behavior.

### Static Configuration

```yaml
providers:
  kubernetesIngress:
    endpoint: ""                          # In-cluster if empty
    namespaces: []                        # Watch specific namespaces (empty = all)
    ingressClass: "traefik"              # IngressClass to handle
    labelSelector: ""                     # Filter Ingress objects by labels
    throttleDuration: 0s
    allowEmptyServices: false
    allowExternalNameServices: false
    nativeLBByDefault: false
    disableClusterScopeResources: false   # Set true if RBAC limited
    strictPrefixMatching: false           # K8s-compliant prefix matching
    ingressEndpoint:
      ip: ""
      hostname: ""
      publishedService: ""                # namespace/service for status propagation
```

### Annotations Reference

Apply to `Ingress` resources with `traefik.ingress.kubernetes.io/` prefix:

| Annotation | Description |
|------------|-------------|
| `router.entrypoints` | EntryPoints (comma-separated, default: web) |
| `router.middlewares` | Middleware references (e.g., `namespace-middlewarename@kubernetescrd`) |
| `router.priority` | Router priority integer |
| `router.tls` | Enable TLS (`true`) |
| `router.tls.options` | TLS options reference |
| `router.tls.certresolver` | ACME cert resolver name |
| `service.serverstransport` | ServersTransport reference |
| `service.nativelb` | Use K8s-native load balancing |
| `service.passhostheader` | Pass Host header to backend (default: true) |
| `service.sticky.cookie.name` | Sticky session cookie name |

### Example Ingress Resource

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: whoami
  namespace: apps
  annotations:
    traefik.ingress.kubernetes.io/router.entrypoints: websecure
    traefik.ingress.kubernetes.io/router.tls: "true"
    traefik.ingress.kubernetes.io/router.tls.certresolver: letsencrypt
spec:
  ingressClassName: traefik
  rules:
    - host: whoami.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: whoami
                port:
                  number: 80
  tls:
    - secretName: whoami-tls
```

## Provider: Kubernetes CRD

Uses Traefik's custom resources (`IngressRoute`, `Middleware`, `TLSOption`, etc.) for richer configuration than standard Ingress.

### Static Configuration

```yaml
providers:
  kubernetesCRD:
    endpoint: ""
    namespaces: []
    ingressClass: "traefik"
    labelSelector: ""
    throttleDuration: 0s
    allowEmptyServices: false
    allowCrossNamespace: false             # Allow IngressRoutes to reference other namespaces
    allowExternalNameServices: false
    nativeLBByDefault: false
    disableClusterScopeResources: false
    crossProviderNamespaces: []            # Namespaces allowed for cross-provider refs
```

### Custom Resource Definitions (CRDs)

Install CRDs before using:

```bash
kubectl apply -f https://raw.githubusercontent.com/traefik/traefik/v3.7/docs/content/reference/dynamic-configuration/kubernetes-crd-definition-v1.yml
kubectl apply -f https://raw.githubusercontent.com/traefik/traefik/v3.7/docs/content/reference/dynamic-configuration/kubernetes-crd-rbac.yml
```

Available CRDs:

| CRD | API Version | Purpose |
|-----|-------------|---------|
| `IngressRoute` | `traefik.io/v1alpha1` | HTTP routing (routers, services, middlewares) |
| `IngressRouteTCP` | `traefik.io/v1alpha1` | TCP routing |
| `IngressRouteUDP` | `traefik.io/v1alpha1` | UDP routing |
| `Middleware` | `traefik.io/v1alpha1` | Middleware configuration |
| `MiddlewareTCP` | `traefik.io/v1alpha1` | TCP middleware configuration |
| `TLSOption` | `traefik.io/v1alpha1` | TLS options (minVersion, cipherSuites, etc.) |
| `TLSStore` | `traefik.io/v1alpha1` | Certificate stores |
| `TraefikService` | `traefik.io/v1alpha1` | Advanced service types (WRR, mirroring) |
| `ServersTransport` | `traefik.io/v1alpha1` | Backend transport config |
| `ServersTransportTCP` | `traefik.io/v1alpha1` | TCP backend transport config |

### IngressRoute Example

```yaml
apiVersion: traefik.io/v1alpha1
kind: IngressRoute
metadata:
  name: my-app
  namespace: apps
spec:
  entryPoints:
    - websecure
  routes:
    - match: Host(`app.example.com`) && PathPrefix(`/api`)
      kind: Rule
      services:
        - name: api-service
          port: 8080
      middlewares:
        - name: auth
        - name: ratelimit
  tls:
    certResolver: letsencrypt
```

### Middleware CRD Example

```yaml
apiVersion: traefik.io/v1alpha1
kind: Middleware
metadata:
  name: auth
  namespace: apps
spec:
  basicAuth:
    secret: auth-credentials    # Kubernetes Secret with users field
```

### Key CRD Features

- **Cross-namespace references**: IngressRoutes can reference Middlewares, Services, etc. in other namespaces when `allowCrossNamespace: true`
- **Provider namespace references**: Use `@kubernetescrd`, `@file`, `@docker` suffix to reference resources from other providers
- **TLS per route**: Each route in an IngressRoute can have its own TLS configuration

## Provider: Kubernetes Gateway API

Implements the Kubernetes Gateway API specification (Standard v1.5.1+). Supports `HTTPRoute`, `GRPCRoute`, `TLSRoute`, and experimental `TCPRoute`.

### Static Configuration

```yaml
providers:
  kubernetesGateway:
    endpoint: ""
    experimentalChannel: false             # Enable TCPRoute, experimental features
    namespaces: []
    labelSelector: ""
    throttleDuration: 0s
    nativeLBByDefault: false
    qps: 50                                # Max queries per sec to K8s API
    burst: 100                             # Max burst to K8s API
    statusAddress:
      ip: ""
      hostname: ""
      service:
        name: ""
        namespace: ""
    crossProviderNamespaces: []
```

### Prerequisites

```bash
# Install Gateway API CRDs (Standard channel)
kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.5.1/standard-install.yaml

# Install Traefik RBAC for Gateway API (if not using Helm)
kubectl apply -f https://raw.githubusercontent.com/traefik/traefik/v3.7/docs/content/reference/dynamic-configuration/kubernetes-gateway-rbac.yml
```

### Gateway API Example

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: GatewayClass
metadata:
  name: traefik
spec:
  controllerName: traefik.io/gateway-controller
---
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: traefik-gateway
  namespace: default
spec:
  gatewayClassName: traefik
  listeners:
    - name: https
      protocol: HTTPS
      port: 443
      tls:
        mode: Terminate
        certificateRefs:
          - kind: Secret
            name: wildcard-example-tls
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: app-route
  namespace: default
spec:
  parentRefs:
    - name: traefik-gateway
  hostnames:
    - app.example.com
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /api
      backendRefs:
        - name: api-service
          port: 8080
```

### Supported Resources

| Resource | Channel | Notes |
|----------|---------|-------|
| `GatewayClass` | Standard | Controller: `traefik.io/gateway-controller` |
| `Gateway` | Standard | HTTP, HTTPS, TCP, TLS listeners |
| `HTTPRoute` | Standard | Hostname matching, path routing, backend refs |
| `GRPCRoute` | Standard | gRPC service routing |
| `TLSRoute` | Standard | TLS passthrough routing |
| `TCPRoute` | Experimental | TCP port-based routing |
| `BackendTLSPolicy` | Standard | Backend TLS configuration |

## Helm Chart Deployment

The Traefik Helm Chart is the recommended installation method for Kubernetes:

```bash
helm repo add traefik https://traefik.github.io/charts
helm install traefik traefik/traefik \
  --namespace traefik \
  --create-namespace \
  --set providers.kubernetesIngress.enabled=true \
  --set providers.kubernetesCRD.enabled=true \
  --set ingressClass.enabled=true
```

Default entryPoints created by Helm: `web` (80), `websecure` (443), `traefik` (8080), `metrics` (9100).

## Resource Namespacing

In Kubernetes, resources must be referenced with their namespace. The format is:

```
<resource-name>.<namespace>@<provider>
```

Examples:
- `my-middleware.apps@kubernetescrd` — Middleware in the `apps` namespace
- `my-tlsoption.default@kubernetescrd` — TLSOption in `default` namespace
- `my-service@file` — Service from the File provider
