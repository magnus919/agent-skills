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
