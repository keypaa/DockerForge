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

## Quick Start

```bash
# Basic generation
python cli.py "FastAPI with PostgreSQL"

# Interactive mode (llama.cpp style)
python cli.py -i
```

## Usage

### One-liner mode
```bash
python cli.py "FastAPI app with PostgreSQL"
python cli.py --template fastapi "with Redis"
python cli.py -o Dockerfile "Flask app"
python cli.py --validate "Go API"
python cli.py --validate --lint "FastAPI"    # with hadolint
```

### Interactive mode (recommended)
```bash
python cli.py -i
```

Commands:
```bash
# Generate
FastAPI with Redis

# Modify
change base to alpine
add postgres

# Use slash commands
/template fastapi     # Use template
/model google/gemma-4-31b-it  # Change model
/from requirements.txt  # Generate from deps file
/explain            # Explain current Dockerfile
/save Dockerfile   # Save to file
/show              # Display current
/history           # Show recent generations
/clear             # Reset chat
/help               # Show help
/feedback FastAPI uses port 5000  # Store tip for next gen
/exit
```

## Available Models

| Model | ID |
|-------|-----|
| Gemma 4 31B | `google/gemma-4-31b-it` |
| MiniMax M2.7 | `minimaxai/minimax-m2.7` |
| Nemotron 3 Super 120B | `nvidia/nemotron-3-super-120b-a12b` |
| Qwen 3.5 122B | `qwen/qwen3.5-122b-a10b` |

## Features

| Feature | Command |
|---------|---------|
| Generate | `python cli.py "description"` |
| Templates | `--template fastapi` |
| Validation | `--validate --lint` |
| Generate from file | `/from requirements.txt` |
| Explain Dockerfile | `/explain` |
| Store feedback | `/feedback FastAPI uses port 5000` |
| Show history | `/history` |

## Templates

| Template | Description | Port |
|----------|-------------|------|
| FastAPI | Python FastAPI with Uvicorn | 8000 |
| Flask | Python Flask with Gunicorn | 5000 |
| Django | Python Django | 8000 |
| Express | Node.js Express | 3000 |
| Next.js | React frontend | 3000 |
| Go | Go HTTP server | 8080 |

## Validation

```bash
# Basic validation (FROM required, no :latest)
python cli.py "FastAPI" --validate

# With hadolint (requires hadolint installed)
# Install: scoop install hadolint
python cli.py "FastAPI" --validate --lint
```

## Feedback System

Store tips that auto-apply to future generations:
```bash
/feedback FastAPI uses port 5000
/feedback #postgres PostgreSQL uses port 5432
/feedback --list    # Show stored
/feedback --clear  # Clear all
```

## History

Automatically saves generations:
```bash
/history          # Show last 5
/history 10     # Show last 10
```

## Environment Variables

```bash
# .env file
NVIDIA_API_KEY=your-key
DEFAULT_MODEL=google/gemma-4-31b-it
```