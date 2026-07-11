# Networking, DNS, Services, and Gateway API

## Layered diagnosis

1. Pod IP and container listener.
2. Service selector and EndpointSlice membership.
3. Cluster DNS resolution from the calling namespace.
4. NetworkPolicy/CNI enforcement.
5. Ingress or Gateway API route and controller conditions.
6. Provider or distribution load balancer.
7. External DNS, TLS, firewall, and client path.

```sh
kubectl get svc,endpointslice -n NAMESPACE
kubectl describe svc NAME -n NAMESPACE
kubectl get networkpolicy -A
kubectl get ingress,gateway,gatewayclass,httproute -A
kubectl run dns-debug --rm -it --restart=Never --image=busybox:1.36 -- nslookup SERVICE.NAMESPACE.svc.cluster.local
```

NetworkPolicy has no effect unless the network plugin enforces it. Policies are additive; ingress and egress isolation are evaluated separately, and both source egress and destination ingress must allow a connection.

## Ingress and Gateway API

Ingress `networking.k8s.io/v1` remains important for compatibility. Gateway API is a separate SIG project with its own CRDs and controller implementations. Prefer Gateway API for new designs only after checking the installed Gateway API CRDs, controller support, and provider/distribution integration. Never assume `Gateway`, `GatewayClass`, or `HTTPRoute` exists because the Kubernetes API server is healthy.

## Sources

- https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/
- https://kubernetes.io/docs/concepts/services-networking/service/
- https://kubernetes.io/docs/concepts/services-networking/network-policies/
- https://kubernetes.io/docs/concepts/services-networking/ingress/
- https://gateway-api.sigs.k8s.io/docs/
