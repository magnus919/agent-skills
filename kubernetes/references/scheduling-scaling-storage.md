# Scheduling, resources, scaling, and storage

## Pending Pods

Inspect, in order: Pod events, node readiness/pressure, resource requests, taints/tolerations, selectors and affinity, topology spread, quotas, priorities, and admission policy. `Pending` is a symptom, not a root cause.

```sh
kubectl describe pod NAME -n NAMESPACE
kubectl get nodes -o wide
kubectl describe node NAME
kubectl get resourcequota,limitrange -n NAMESPACE
```

Requests influence scheduling. CPU limits throttle; memory-limit violations can result in OOM kills. Do not prescribe resource changes without observing usage, requests, limits, and node capacity.

## HPA

HPA needs a scalable target and a functioning metrics API. Missing resource requests can make utilization undefined. Check HPA conditions, target reference, current/desired metrics, and `metrics.k8s.io` availability before changing replicas.

HPA, VPA, and Cluster Autoscaler are separate control loops. HPA changes replica count, VPA changes resource recommendations or requests, and Cluster Autoscaler changes node capacity. Combining them without a signal/ownership design can cause oscillation, request inflation, evictions, or slow reaction. Treat VPA as recommendation-only until its eviction and stateful-workload behavior is understood; treat Cluster Autoscaler as a provider/distribution overlay.

```sh
kubectl get hpa -A
kubectl describe hpa NAME -n NAMESPACE
kubectl top pods -n NAMESPACE
kubectl get --raw='/apis/metrics.k8s.io/v1beta1/namespaces/NAMESPACE/pods'
```

Do not diagnose “HPA is not scaling” from replica count alone. Check metrics availability, target requests, HPA conditions, stabilization/behavior policies, pending Pods, and node-group capacity.

## Persistent storage

Separate PV, PVC, StorageClass, CSI driver, attachment/mount, and application filesystem evidence:

```sh
kubectl get pvc,pv,storageclass -A
kubectl describe pvc CLAIM -n NAMESPACE
kubectl get volumeattachment -o wide
kubectl get pods -A -l app=CSI-DRIVER
```

A Pending PVC may mean no matching class/capacity. A Terminating PVC may be protected while still in use. A Bound PVC does not prove the application mounted or can write the volume.

## Sources

- https://kubernetes.io/docs/concepts/scheduling-eviction/
- https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/
- https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/
- https://kubernetes.io/docs/concepts/storage/volumes/
- https://kubernetes.io/docs/concepts/storage/persistent-volumes/
- https://kubernetes.io/docs/concepts/storage/storage-classes/
- https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/
- https://kubernetes.io/docs/concepts/scheduling-eviction/pod-priority-preemption/
