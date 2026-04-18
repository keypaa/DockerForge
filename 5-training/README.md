# DockerForge Fine-tuning

Fine-tune a model for Dockerfile generation using Unsloth.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Prepare your data (see data/sample.json for format)

# 3. Run training
python train.py \
    --data_path ./data/train.json \
    --output_dir ./output \
    --num_epochs 3

# 4. Export to GGUF
python export_gguf.py --adapter_path ./output --output ./dockerforge
```

## Data Format

Expected JSON format (ChatML):

```json
[
  {
    "messages": [
      {"role": "user", "content": "Write a Dockerfile for FastAPI"},
      {"role": "assistant", "content": "FROM python:3.11-slim..."}
    ]
  }
]
```

Or simple format:

```json
[
  {"prompt": "Write a Dockerfile for FastAPI", "response": "FROM python:3.11-slim..."}
]
```

## GPU Memory Requirements

| Model | Batch Size | VRAM |
|-------|-----------|------|
| Qwen2.5-Coder-7B | 2 | ~16GB |
| Qwen2.5-Coder-7B | 4 | ~20GB |
| Qwen2.5-Coder-7B | 8 | ~24GB |

Use `--batch_size` to adjust.

## Training Commands

### On 16GB GPU (T4)
```bash
python train.py \
    --data_path ./data/train.json \
    --output_dir ./output \
    --batch_size 2 \
    --gradient_accumulation 8 \
    --num_epochs 3
```

### On 24GB GPU (L4/A100)
```bash
python train.py \
    --data_path ./data/train.json \
    --output_dir ./output \
    --batch_size 4 \
    --gradient_accumulation 4 \
    --num_epochs 3
```

## Export Options

```bash
# Q4 quantization (recommended, ~4.7GB)
python export_gguf.py --adapter_path ./output --output ./dockerforge --quantization q4_k_m

# Q5 quantization (better quality, ~5.7GB)
python export_gguf.py --adapter_path ./output --output ./dockerforge --quantization q5_k_m

# FP16 (best quality, ~16GB)
python export_gguf.py --adapter_path ./output --output ./dockerforge --quantization f16
```

## Datasets

Recommended HuggingFace datasets:
- `BrandonHatch/Dockerfile_Mastery` (3K rated examples)
- `loubnabnl/dockerfile_checks` (137K)
- `codeparrot/github-code` (filter for Dockerfile)

## Models

Tested base models:
- `Qwen/Qwen2.5-Coder-7B-Instruct` (recommended)
- `Qwen/Qwen2.5-Coder-1.5B-Instruct` (smaller, faster)
- `meta-llama/Llama-3.1-8B-Instruct` (if you have more VRAM)
