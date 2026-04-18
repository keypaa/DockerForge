# DockerForge ⚒️

> AI-powered Dockerfile generator using NVIDIA NIM API

## Overview

DockerForge generates production-ready Dockerfiles from natural language. Uses free NVIDIA NIM models to generate optimized multi-stage Dockerfiles.

## Quick Start

```bash
# Install dependencies
pip install openai

# Generate a Dockerfile
python 4-deployment/cli.py "FastAPI with PostgreSQL"

# Or use interactive mode
python 4-deployment/cli.py -i
```

## Features

- 🎯 Natural language to Dockerfile
- 🔧 Multi-stage builds (optimized image size)
- ⚡ Fast generation via NIM API
- 📦 Security best practices (non-root user)
- 📋 Interactive mode with /slash commands
- 📄 Pre-built templates (FastAPI, Django, Express, etc.)

## Interactive Mode

```bash
python 4-deployment/cli.py -i
```

```
dockerforge> FastAPI with Redis
dockerforge> change base to alpine
dockerforge> /save
dockerforge> /exit
```

Slash commands: `/template`, `/model`, `/save`, `/show`, `/clear`, `/help`, `/exit`

One-liner mode:

```bash
# Basic
python 4-deployment/cli.py "FastAPI app"

# With template
python 4-deployment/cli.py --template fastapi "with Redis"

# Stream output
python 4-deployment/cli.py "Go HTTP server" --stream
```

## Available Models

- Gemma 4 31B
- MiniMax M2.7
- Nemotron 3 Super 120B
- Qwen 3.5 122B

Set in `.env`:

```bash
# .env
NVIDIA_API_KEY=your-key
DEFAULT_MODEL=google/gemma-4-31b-it
```

## Templates

| Template | Description | Port |
|----------|-------------|------|
| FastAPI | Python FastAPI with Uvicorn | 8000 |
| Flask | Python Flask with Gunicorn | 5000 |
| Django | Python Django with Gunicorn | 8000 |
| Express | Node.js Express with JWT | 3000 |
| Next.js | React frontend | 3000 |
| Go | Go HTTP server | 8080 |

Usage:

```bash
python 4-deployment/cli.py --template fastapi "with PostgreSQL"
# Or in interactive mode:
> /template fastapi
> FastAPI with Redis
```

## Architecture

```
4-deployment/
├── cli.py           # Main CLI tool
├── config.py       # Settings
├── templates/     # Pre-built templates
└── .env.example  # Env template
```

## License

MIT - See [LICENSE](LICENSE) file

---

**Built with ❤️ by [@keypaa](https://github.com/keypaa)**