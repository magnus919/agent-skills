# TLS & ACME Reference

Traefik can automatically obtain and renew TLS certificates from Let's Encrypt (and other ACME CAs), handle custom certificates, and configure TLS options.

## ACME Certificate Resolvers (Let's Encrypt)

Define certificate resolvers in the static configuration:

```yaml
# Static config (traefik.yml)
certificatesResolvers:
  letsencrypt:
    acme:
      email: "admin@example.com"           # REQUIRED — registration email
      storage: "/letsencrypt/acme.json"    # Certificate storage (JSON)
      caServer: "https://acme-v02.api.letsencrypt.org/directory"
      # Use staging for testing to avoid rate limits:
      # caServer: "https://acme-staging-v02.api.letsencrypt.org/directory"
      keyType: "RSA4096"                   # EC256, EC384, RSA2048, RSA4096, RSA8192
      preferredChain: ""                   # Preferred certificate chain issuer
      certificatesDuration: 2160           # Hours before renewal (default 2160 = 90 days)

      # HTTP-01 Challenge (port 80)
      httpChallenge:
        entryPoint: "web"                  # EntryPoint listening on port 80

      # TLS-ALPN-01 Challenge (port 443)
      tlsChallenge: {}

      # DNS-01 Challenge (required for wildcard certs)
      dnsChallenge:
        provider: "cloudflare"             # DNS provider name
        resolvers:                         # Optional custom DNS resolvers
          - "1.1.1.1:53"
          - "8.8.8.8:53"
        delayBeforeCheck: 0s               # Wait before checking propagation
        disablePropagationCheck: false

      # External Account Binding (for ACME providers that require it)
      eab:
        kid: ""                            # Key identifier
        hmacEncoded: ""                    # Base64 URL-encoded HMAC key
```

### Challenge Types

| Challenge | Port Required | Wildcard Certs | Notes |
|-----------|--------------|----------------|-------|
| HTTP-01 | Port 80 | No | Simplest — just needs port 80 reachable |
| TLS-ALPN-01 | Port 443 | No | No port 80 needed, but port 443 must be reachable |
| DNS-01 | No ports needed | Yes | Requires DNS provider API credentials |

### Configuring DNS Providers

Traefik uses [Lego](https://go-acme.github.io/lego/dns/) for DNS challenges. Each provider requires specific environment variables.

```yaml
# Cloudflare example — requires env vars at Traefik's runtime
# CF_DNS_API_TOKEN=your_token
# or
# CF_API_EMAIL=email@example.com
# CF_API_KEY=your_global_api_key
certificatesResolvers:
  letsencrypt:
    acme:
      dnsChallenge:
        provider: "cloudflare"
```

Common providers and their env vars:

| Provider | `provider` value | Required env vars |
|----------|-----------------|-------------------|
| Cloudflare | `cloudflare` | `CF_DNS_API_TOKEN` or `CF_API_EMAIL` + `CF_API_KEY` |
| AWS Route53 | `route53` | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` (or IAM role) |
| Google Cloud DNS | `gcloud` | `GCE_PROJECT`, `GCE_SERVICE_ACCOUNT_FILE` |
| DigitalOcean | `digitalocean` | `DO_AUTH_TOKEN` |
| Azure | `azure` | `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, `AZURE_SUBSCRIPTION_ID`, `AZURE_TENANT_ID` |
| Namecheap | `namecheap` | `NAMECHEAP_API_USER`, `NAMECHEAP_API_KEY` |
| Linode | `linode` | `LINODE_TOKEN` |
| Vultr | `vultr` | `VULTR_API_KEY` |
| OVH | `ovh` | `OVH_ENDPOINT`, `OVH_APPLICATION_KEY`, `OVH_APPLICATION_SECRET`, `OVH_CONSUMER_KEY` |

Full provider list: https://go-acme.github.io/lego/dns/

### Wildcard Certificate with DNS-01

```yaml
# DNS challenge is REQUIRED for wildcard certs
certificatesResolvers:
  letsencrypt:
    acme:
      email: "admin@example.com"
      storage: "/letsencrypt/acme.json"
      dnsChallenge:
        provider: "cloudflare"
        delayBeforeCheck: 0
      # HTTP and TLS challenges are NOT needed for wildcard-only
```

## Using Certificates in Routers

Reference a certificate resolver on the router:

```yaml
# Dynamic config (File provider)
http:
  routers:
    app:
      rule: "Host(`app.example.com`)"
      tls:
        certResolver: "letsencrypt"
        options: "default@file"       # Optional TLS options
        domains:
          - main: "example.com"
            sans:
              - "www.example.com"
              - "api.example.com"
      service: "app-backend"
```

Or via Docker labels:

```yaml
labels:
  - "traefik.http.routers.app.rule=Host(`app.example.com`)"
  - "traefik.http.routers.app.tls=true"
  - "traefik.http.routers.app.tls.certresolver=letsencrypt"
```

## TLS Options

Define TLS connection parameters:

```yaml
# Dynamic config (File provider)
tls:
  options:
    default:                           # Applies to all routers unless overridden
      minVersion: VersionTLS12         # Minimum TLS version
      maxVersion: VersionTLS13         # Maximum TLS version
      cipherSuites:                    # Specific cipher suites
        - TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
        - TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
        - TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256
        - TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384
      sniStrict: false                 # Reject if SNI doesn't match a server cert
      preferServerCipherSuites: false
      curvePreferences:                # ECC curves for key exchange
        - CurveP256
        - CurveP384
        - CurveP521

    modern:                            # Modern security profile
      minVersion: VersionTLS13
      sniStrict: true

    mtls:                              # Mutual TLS (client certificates)
      minVersion: VersionTLS12
      clientAuth:
        caFiles:
          - "/etc/traefik/certs/ca.pem"
        clientAuthType: RequireAndVerifyClientCert  # or VerifyClientCertIfGiven
```

TLS reference in a router:

```yaml
http:
  routers:
    secured-app:
      rule: "Host(`app.example.com`)"
      tls:
        options: "modern@file"         # Namespace:name@provider
```

## Custom Certificates

Manually load certificates instead of using ACME:

```yaml
# Dynamic config
tls:
  certificates:
    - certFile: "/etc/traefik/certs/example.com.pem"
      keyFile: "/etc/traefik/certs/example.com-key.pem"
      stores:
        - "default"                    # Certificate store to use
    - certFile: "/etc/traefik/certs/wildcard.example.com.pem"
      keyFile: "/etc/traefik/certs/wildcard.example.com-key.pem"
```

## Default Certificate

Traefik generates a self-signed certificate by default. To set a custom default:

```yaml
# Dynamic config
tls:
  stores:
    default:
      defaultCertificate:
        certFile: "/etc/traefik/certs/default.pem"
        keyFile: "/etc/traefik/certs/default-key.pem"
```

## TLS on EntryPoints

Enable TLS for all routers on an entryPoint:

```yaml
entryPoints:
  websecure:
    address: ":443"
    http:
      tls: true                        # All routers on websecure get TLS
      tls:
        certResolver: "letsencrypt"    # Default cert resolver
        options: "default@file"        # Default TLS options
```

Or per-router override:

```yaml
http:
  routers:
    no-tls-route:
      rule: "Host(`public.example.com`)"
      entryPoints: ["websecure"]
      # No tls block = no TLS for this specific route
```

## Automatic Certificate Renewal

Traefik automatically tracks certificate expiry and renews:
- Default cert validity: 90 days
- Renewal starts: 30 days before expiry
- Configured by `certificatesDuration` (in hours, default 2160 = 90 days)
- Unused certificates may still be renewed

## Certificate Storage

ACME certificates are stored as JSON in the `storage` file (default `acme.json`):

```yaml
certificatesResolvers:
  letsencrypt:
    acme:
      storage: "/letsencrypt/acme.json"
```

**Important:** `acme.json` must have permissions `600` (owner read/write only) or Traefik will refuse to start.

## v3 TLS Changes

- The `tls` option on routers now defaults based on the entryPoint's `http.tls` setting
- `tls.minVersion` now defaults to `VersionTLS12` instead of `VersionTLS10`
- The deprecated `tls` section in static config for default cert has been replaced by the dynamic `tls.stores` approach
