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
# Basic usage
python cli.py "FastAPI app with PostgreSQL"

# With specific model
python cli.py -m z-ai/glm4.7 "Node.js Express with MongoDB"

# With template
python cli.py --template fastapi "with Redis"

# From file
cat input.txt | python cli.py

# Save to file
python cli.py "Python Flask app" -o Dockerfile

# Stream output
python cli.py "FastAPI with Redis" --stream

# List available templates
python cli.py --list-templates
```

### Interactive mode (recommended)
```bash
# Start interactive mode
python cli.py -i

# Or with initial description
python cli.py -i "FastAPI app"
```

Then at the `dockerforge>` prompt:

```bash
# Generate a Dockerfile
FastAPI with Redis

# Change the Dockerfile
change base to alpine
make it smaller
add postgres for data

# Use slash commands
/template fastapi    # Use template
/model z-ai/glm4.7  # Change model
/save Dockerfile     # Save to file
/show               # Display current
/clear              # Reset chat
/help               # Show help
/exit               # Exit
```

## Available Models

| Model | ID | Strength |
|-------|-----|----------|
| GLM-4.7 | `z-ai/glm4.7` | Best overall (default) |
| Gemma 3 37B | `google/gemma-3-37b-it` | Quality |
| MiniMax 27B | `minimax/minimax-27b` | Fast |
| Kimi K2 | `atatlab/kimi-k2` | Multilingual |

## Templates

| Template | Description | Default Port |
|----------|-------------|-------------|
| FastAPI | Python FastAPI with Uvicorn | 8000 |
| Flask | Python Flask with Gunicorn | 5000 |
| Django | Python Django with Gunicorn | 8000 |
| Express | Node.js Express with JWT | 3000 |
| Next.js | React frontend with Next.js | 3000 |
| Go | Go HTTP server | 8080 |

Usage:
```bash
python cli.py --template fastapi "with PostgreSQL"
# Or in interactive mode:
> /template fastapi
> FastAPI with Redis
```

## Examples

### Python - FastAPI with PostgreSQL
```bash
python cli.py "FastAPI app with PostgreSQL"
```
```dockerfile
FROM python:3.11-slim as builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
RUN useradd -m -u 1000 appuser
USER appuser
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Interactive Session
```bash
$ python cli.py -i
dockerforge> Python FastAPI with Redis
[generating...]
==================================================
FROM python:3.11-slim
...
==================================================

dockerforge> change base to alpine
[modifying...]
==================================================
FROM python:3.11-alpine
...
==================================================

dockerforge> /save
[✓] Saved to Dockerfile
dockerforge> /exit
```

## Environment Variables

```bash
# .env file
NVIDIA_API_KEY=your-api-key-here
DEFAULT_MODEL=z-ai/glm4.7
```