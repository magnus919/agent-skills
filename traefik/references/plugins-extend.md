# Plugins & Extending Traefik

Traefik supports two plugin systems for extending its capabilities with custom middlewares and providers.

## Plugin Systems Comparison

| Feature | Yaegi | WebAssembly (WASM) |
|---------|-------|-------------------|
| Language | Go | Any language compiling to WASM (Go, Rust, C++, TinyGo) |
| Compilation | Not required (interpreted) | Required (compiled to .wasm binary) |
| Performance | Interpreted | Near-native |
| Hot-reload | Yes | No (binary change requires reload) |
| Safety | Go sandbox | WASM sandbox |
| Extensibility | Middleware + Provider | Middleware only |
| Use case | Rapid development, prototyping | Production-grade, performance-critical |
| Plugin Catalog | Available | Available |

## Plugin Catalog

Browse available plugins: https://plugins.traefik.io/

The Plugin Catalog is accessible from the Traefik Dashboard under the **Plugins** menu entry. Each plugin provides:
- Installation instructions (static config snippet)
- Dynamic configuration syntax
- Usage examples

## Configuring Plugins (Static Config)

### Remote Plugins (from catalog)

```yaml
# Static config
experimental:
  plugins:
    plugin-name:
      moduleName: "github.com/org/plugin"
      version: "v0.1.0"
      # Optional settings (WASM only):
      settings:
        envs:
          - "CACHE_TTL=300"
        mounts:
          - "/data/cache:/cache"
```

### Local Plugins (development)

```yaml
experimental:
  localPlugins:
    plugin-name:
      moduleName: "github.com/org/plugin"
      settings:
        envs:
          - "DEBUG=true"
```

## Using Plugins in Dynamic Config

Plugins are referenced as middlewares with the `@plugin` provider namespace:

```yaml
# Dynamic config (File provider)
http:
  middlewares:
    my-auth:
      plugin:
        auth-plugin-name:
          headerName: "X-API-Key"
          secret: "my-secret"

http:
  routers:
    app:
      rule: "Host(`app.example.com`)"
      middlewares:
        - "my-auth@file"          # File-based middleware
        - "plugin-name@plugin"    # Plugin middleware

  services:
    app:
      loadBalancer:
        servers:
          - url: "http://backend:80"
```

With Docker labels:

```yaml
labels:
  - "traefik.http.middlewares.my-plugin.plugin.plugin-name.key=value"
  - "traefik.http.routers.app.middlewares=my-plugin@plugin"
```

## Plugin Development

### Yaegi Plugin (Go, no compilation)

Create a Go package with a module path and implement the middleware/provider interface. Import pattern:

```go
package myplugin

import (
    "context"
    "net/http"
)

func New(ctx context.Context, conf map[string]interface{}) (func(next http.Handler) http.Handler, error) {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(rw http.ResponseWriter, req *http.Request) {
            // Custom logic
            next.ServeHTTP(rw, req)
        })
    }, nil
}
```

### WASM Plugin (any language)

Compile to a `.wasm` binary following the http-wasm specification (https://http-wasm.io/). HTTP middleware handler with request/response manipulation capability.

### Development Resources

- **Developer docs**: https://plugins.traefik.io/install
- **Plugin creation guide**: https://plugins.traefik.io/create
- **Plugin catalog submission**: Publish to https://plugins.traefik.io/ for community use

## Provider Plugins

Yaegi plugins can extend Traefik with custom providers, enabling dynamic configuration from any source:

```yaml
experimental:
  plugins:
    my-provider-plugin:
      moduleName: "github.com/org/provider-plugin"
      version: "v0.1.0"

providers:
  plugin:
    my-provider-plugin:
      endpoint: "http://custom-source:8080"
      pollInterval: "30s"
```

## Security Considerations

- Plugins run with the same privileges as Traefik itself
- WASM provides stronger isolation (sandboxed by design)
- Only install plugins from trusted sources (verified hashes)
- Test plugins in staging before production deployment
- Plugin hash verification is optional but recommended for remote plugins:

```yaml
experimental:
  plugins:
    plugin-name:
      moduleName: "github.com/org/plugin"
      version: "v0.1.0"
      hash: "sha256:abc123..."
```

## FastProxy (Experimental)

FastProxy is an experimental HTTP/2 multiplexing optimization that reduces connection overhead to backends:

```yaml
# Static config
experimental:
  fastProxy: true
```

FastProxy connects to backend servers using a shared HTTP/2 connection pool, reducing connection churn for services with many concurrent requests. Available in Traefik v3.x experimental channel.
