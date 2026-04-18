# DockerForge CLI

Generate production-ready Dockerfiles using NVIDIA NIM API.

## Setup

```bash
# 1. Copy env example
cp .env.example .env

# 2. Get your API key
# Visit https://build.nvidia.com, select any model, get API key

# 3. Edit .env with your key
nano .env
```

## Usage

```bash
# Basic usage
python cli.py "FastAPI app with PostgreSQL"

# With specific model
python cli.py -m google/gemma-3-37b-it "Node.js Express with MongoDB"

# From file
cat input.txt | python cli.py

# Save to file
python cli.py "Python Flask app" -o Dockerfile

# Stream output (see reasoning)
python cli.py "FastAPI with Redis" --stream
```

## Available Models

| Model | ID | Strength |
|-------|-----|----------|
| GLM-4.7 | `z-ai/glm4.7` | Best overall |
| Gemma 3 37B | `google/gemma-3-37b-it` | Quality |
| MiniMax 27B | `minimax/minimax-27b` | Fast |
| Kimi K2 | `atatlab/kimi-k2` | Multilingual |

## Examples

```bash
# Python FastAPI
python cli.py "FastAPI with PostgreSQL, Redis for caching"

# Node.js
python cli.py "Express.js with MongoDB, JWT auth"

# Go
python cli.py "Go HTTP server with SQLite"

# Multi-stage
python cli.py "Python Django app with multi-stage build for small image"
```