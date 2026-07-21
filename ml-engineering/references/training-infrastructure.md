# Training Infrastructure

## GPU Selection

| GPU | VRAM | Best For | Notes |
|-----|------|----------|-------|
| RTX 4090 | 24 GB | LoRA/QLoRA 7B–13B, inference | Consumer, no NVLink |
| RTX 5090 | 32 GB | LoRA 13B–30B, QLoRA 70B | Consumer, no NVLink |
| A6000 | 48 GB | Full fine-tune 7B, LoRA 30B–70B | Prosumer, NVLink pair |
| A100 80GB | 80 GB | Full fine-tune 13B–30B, multi-GPU | Datacenter, NVLink |
| H100 80GB | 80 GB | Full fine-tune 30B–70B, RLHF | Datacenter, NVLink, FP8 |
| H200 141GB | 141 GB | Full fine-tune 70B+, long context | Datacenter, NVLink |

## VRAM Budgeting

Rule of thumb for training memory (mixed precision, AdamW):

```
VRAM ≈ params × (2 + 2 + 4 + 4) bytes  [weights + grads + optimizer states]
     + activation memory (batch-dependent)
```

| Technique | VRAM multiplier | Example: 7B model |
|-----------|----------------|-------------------|
| Full fine-tune (FP16 + Adam) | ~16× params | ~112 GB |
| LoRA (rank 64) | ~2.5× params | ~18 GB |
| QLoRA (4-bit + LoRA) | ~0.8× params | ~6 GB |
| Inference only (FP16) | ~2× params | ~14 GB |
| Inference only (4-bit) | ~0.5× params | ~4 GB |

## Multi-GPU Training

| Strategy | When | Framework |
|----------|------|-----------|
| DataParallel (DP) | Single node, quick experiments | PyTorch native |
| DistributedDataParallel (DDP) | Single node, production training | `torchrun --nproc_per_node=N` |
| FSDP / DeepSpeed ZeRO | Model doesn't fit one GPU | `accelerate`, DeepSpeed config |
| Pipeline parallelism | Very large models (>70B) | DeepSpeed, Megatron-LM |
| Tensor parallelism | Latency-critical inference | vLLM, TensorRT-LLM |

### DDP Launch Pattern

```bash
torchrun --nproc_per_node=4 --master_port=29500 train.py \
  --model_name meta-llama/Llama-3-8B \
  --per_device_train_batch_size 4 \
  --gradient_accumulation_steps 8 \
  --bf16 true
```

Effective batch size = `per_device × nproc × grad_accum` = 4 × 4 × 8 = 128.

### FSDP Config (accelerate)

```yaml
# accelerate_config.yaml
compute_environment: LOCAL_MACHINE
distributed_type: FSDP
fsdp_config:
  fsdp_auto_wrap_policy: TRANSFORMER_BASED_WRAP
  fsdp_sharding_strategy: FULL_SHARD  # ZeRO-3 equivalent
  fsdp_state_dict_type: SHARDED_STATE_DICT
  fsdp_cpu_ram_efficient_loading: true
mixed_precision: bf16
num_processes: 4
```

## Cloud vs On-Prem Decision

| Factor | Cloud (Lambda, RunPod, Vast) | On-Prem |
|--------|------------------------------|---------|
| Utilization < 30% | ✅ Pay per hour | ❌ Idle hardware |
| Utilization > 60% | ❌ Expensive at scale | ✅ Amortizes in ~8 months |
| Data sensitivity | ❌ Data leaves premises | ✅ Stays local |
| Burst capacity | ✅ Scale to 8×H100 on demand | ❌ Fixed ceiling |
| Ops burden | ❌ Zero (managed) | ✅ You maintain cooling, power, drivers |
| Experiment velocity | ✅ Spin up, tear down | ⚠️ Queue contention on shared cluster |

### Cloud Cost Reference (spot/on-demand, 2025)

| GPU | On-demand $/hr | Spot $/hr |
|-----|----------------|-----------|
| A100 80GB | $1.80–$2.50 | $0.90–$1.40 |
| H100 80GB | $3.50–$5.00 | $2.00–$3.00 |
| RTX 4090 | $0.40–$0.70 | $0.25–$0.45 |

## Storage and Data Pipeline

- Training data on NVMe or tmpfs — network storage stalls GPUs
- Checkpoints to object storage (S3/GCS) or NAS — never only local disk
- Use `safetensors` format — faster load, no pickle security risk
- Pre-tokenize datasets for large corpora — tokenization at load time wastes GPU-hours

## Monitoring Training

| Metric | Healthy Range | Red Flag |
|--------|--------------|----------|
| GPU utilization | > 90% | < 70% = data pipeline bottleneck |
| GPU memory | Stable after warmup | Growing = leak (check grad accumulation) |
| Loss curve | Smooth decrease | Spikes = LR too high; plateau = converged or stuck |
| Grad norm | Stable or decreasing | Exploding = reduce LR or add clipping |
| Throughput (samples/sec) | Consistent | Degrading = thermal throttle or I/O |
