# DockerForge Phase 2: Local Fine-tuned Model

## Objective

Add local fine-tuned model option to DockerForge CLI. Users can run the model on CPU (llama.cpp) while you fine-tune on cloud GPU.

## Current State

- ✅ API mode working (NIM: GLM-4.7, Gemma 4, etc.)
- ⏳ Local mode needed

## Architecture

```
DockerForge CLI
├── --model api      → NIM API (current)
└── --model local    → Your fine-tuned GGUF model (new)
```

## Pipeline

```
1. Data Collection
   └── HuggingFace datasets (see below)

2. Data Preparation  
   └── Format: ChatML JSON
   └── 500-2000 examples (quality > quantity)

3. Fine-tuning (Cloud GPU - T4/L4/A100)
   └── Unsloth + QLoRA
   └── Base: Qwen3 8B (from Bonsai-8B-unpacked)
   └── ~2-4 hours

4. Quantization
   └── Merge adapters → GGUF Q4_K_M (~4.7GB)

5. Integration
   └── Add --model local flag
   └── Users run on CPU via llama.cpp
```

## Available Datasets

| Dataset | Size | Best For |
|---------|------|----------|
| **codeparrot/github-code** | 366K Dockerfiles | General training |
| **bigcode/the-stack** | Large | Pre-training |
| **TahalliAnas/SafeOps** | 20K pairs | Security focus |
| **BrandonHatch/Dockerfile_Mastery** | 3K rated | Quality examples |
| **loubnabnl/dockerfile_checks** | 137K | Linting/validation |
| **LeeSek/dockerfiles-linted** | ? | Quality checked |

**Recommended start**: `BrandonHatch/Dockerfile_Mastery` (3K high-quality rated examples)
Or combine with `loubnabnl/dockerfile_checks` for more data

## Key Decisions Needed

### 1. Base Model
- **Option A**: Qwen3 8B (from Bonsai-8B-unpacked) - better quality, needs L4/A100
- **Option B**: Qwen3 4B (from Bonsai-4B-unpacked) - smaller, can use T4

### 2. Dataset
- Start with `BrandonHatch/Dockerfile_Mastery` (3K examples)
- Scale to `codeparrot/github-code` if needed

### 3. Training Config (Unsloth QLoRA)
- Rank: 16-32
- LR: 2e-4
- Epochs: 2-3

### 4. Cloud GPU for Fine-tuning
- T4 (16GB) - works with QLoRA
- L4 (24GB) - comfortable
- A100 (40GB) - fast

### 5. CPU Inference for End Users
- GGUF Q4_K_M (~4.7GB) runs on CPU via llama.cpp
- No GPU required for users!

## Execution Steps

### Phase 1: Data (Week 1)
- [ ] Load `BrandonHatch/Dockerfile_Mastery` dataset
- [ ] Convert to ChatML JSON format
- [ ] Quality check (keep ~1000 best examples)

### Phase 2: Training (Week 2)
- [ ] Setup Unsloth on cloud GPU (L4)
- [ ] Fine-tune Qwen3 8B with QLoRA
- [ ] Evaluate outputs manually
- [ ] If needed: train more epochs or add data

### Phase 3: Quantize & Deploy (Week 3)
- [ ] Merge LoRA adapters
- [ ] Export to GGUF Q4_K_M
- [ ] Add `--model local` flag to CLI
- [ ] Test locally (CPU inference)

## Deliverables

- Fine-tuned GGUF model (~4.7GB)
- Updated CLI with `--model local path/to/model.gguf`
- Documentation for users

## Open Questions

1. Which dataset to start with?
2. Full 8B or smaller 4B?
3. Training budget/GPU choice?