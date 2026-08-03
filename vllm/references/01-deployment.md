# vLLM Deployment: Docker and Kubernetes

> **Last Updated:** 2026-08-03
> Sources: https://docs.vllm.ai/en/latest/deployment/docker/ and
> https://docs.vllm.ai/en/latest/deployment/k8s/

## Docker

The official image is `vllm/vllm-openai` (NVIDIA CUDA), with
`vllm/vllm-openai-rocm` (AMD) and `vllm/vllm-openai-xpu` (Intel) variants. The
image entrypoint is `vllm serve`, so engine arguments follow the image tag.

```bash
docker run --runtime nvidia --gpus all \
    -v ~/.cache/huggingface:/root/.cache/huggingface \
    --env "HF_TOKEN=$HF_TOKEN" \
    -p 8000:8000 \
    --ipc=host \
    vllm/vllm-openai:v0.26.0 \
    --model Qwen/Qwen3-0.6B
```

### Container details that matter

- **Shared memory**: use `--ipc=host` or a `--shm-size` (for example `--shm-size=2g`).
  PyTorch uses shared memory between processes, particularly for tensor-parallel
  inference; the default 64 MB `/dev/shm` in a container is too small and causes
  obscure crashes at load time.
- **HF token**: pass `--env "HF_TOKEN=$HF_TOKEN"` for gated models. Never commit
  the token; mount the cache volume so weights are reused across restarts.
- **CUDA compatibility**: on hosts whose driver is older than the toolkit in the
  image, set `VLLM_ENABLE_CUDA_COMPATIBILITY=1` (only for select datacenter GPUs).
- **Compile cache**: vLLM compiles `torch.compile` artifacts into
  `VLLM_CACHE_ROOT` (default `~/.cache/vllm`). Mount a named volume there so the
  second and later containers start fast instead of recompiling.
- **Non-root**: the image ships a `vllm` user (UID 2000, GID 0). Run with
  `--user 2000:0` and mount writable paths under `/home/vllm` (for example
  `/home/vllm/.cache/huggingface`) rather than `/root`. The `vllm-openai-nonroot`
  image target supports OpenShift-style arbitrary UIDs within group 0.
- **Pin tags**: use a release tag (`vllm/vllm-openai:v0.26.0`), not `latest`.
  Optional dependencies (audio, gRPC, etc.) are not in the base image; layer
  them on with `uv pip install --system vllm[extra]==<same-version>`.

## Kubernetes

A native deployment: Deployment + Service, GPU resource limits, a model-cache
volume, an `emptyDir` shared-memory volume, and `/health` probes.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vllm-server
spec:
  replicas: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: vllm
  template:
    metadata:
      labels:
        app.kubernetes.io/name: vllm
    spec:
      volumes:
        - name: cache-volume
          persistentVolumeClaim:
            claimName: vllm-models
        - name: shm
          emptyDir:
            medium: Memory
            sizeLimit: "2Gi"
      containers:
        - name: vllm
          image: vllm/vllm-openai:v0.26.0
          command: ["/bin/sh", "-c"]
          args:
            - "vllm serve <model> --served-model-name <name> --trust-remote-code"
          env:
            - name: HF_TOKEN
              valueFrom:
                secretKeyRef:
                  name: hf-token-secret
                  key: token
          ports:
            - containerPort: 8000
          resources:
            limits:
              nvidia.com/gpu: "1"
            requests:
              nvidia.com/gpu: "1"
          volumeMounts:
            - mountPath: /root/.cache/huggingface
              name: cache-volume
            - mountPath: /dev/shm
              name: shm
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 60
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 60
            periodSeconds: 5
```

### K8s details that matter

- **GPU scheduling**: request `nvidia.com/gpu: "1"` (NVIDIA device plugin) or
  `amd.com/gpu` (AMD k8s device plugin). Tensor parallelism across GPUs in one
  pod uses `--tensor-parallel-size` equal to the GPU count; the pod then needs
  a larger `/dev/shm` (size it at 2-8 GiB) and, on some platforms, host IPC.
- **Probes**: vLLM's `/health` endpoint reports ready only after the model
  finishes loading, which can take minutes for large models. Set
  `initialDelaySeconds` and `failureThreshold` high enough; a container killed
  by the probe loop logs `KeyboardInterrupt: terminated` and shows
  `failed startup probe, will be restarted` in `kubectl get events`. To find
  the right threshold, remove the probes, time startup, then restore them.
- **gRPC**: pass `--grpc` (requires `vllm[grpc]` in the image) and replace the
  HTTP probes with `grpc` probes; the server then implements the standard
  gRPC health-checking protocol and returns `NOT_SERVING` while loading or
  shutting down.
- **Alternatives**: the upstream docs also cover Helm, KServe, KubeRay,
  NVIDIA Dynamo, and the vllm-project production-stack integrations. For this
  skill's scope, the native manifest above is the reference pattern; the
  infrastructure for those frameworks routes to `kubernetes`.

## Verification at the delivery boundary

- `kubectl logs -l app.kubernetes.io/name=vllm` shows `Application startup
  complete` and `Uvicorn running on http://0.0.0.0:8000`.
- `vllm-health --url <service-url> --check health --check models --json` shows
  `/health` 200 and the served model.
- A bounded request returns generated tokens; a PVC-backed model cache means
  the next pod starts without re-downloading weights.
