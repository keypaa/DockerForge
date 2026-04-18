# DockerForge ⚒️

> AI-powered Dockerfile generator using NVIDIA NIM API

## Overview

DockerForge generates production-ready Dockerfiles from natural language. Uses free NVIDIA NIM models (GLM-4.7, Gemma 3, etc.) to generate optimized multi-stage Dockerfiles.

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

Commands: `/template`, `/model`, `/save`, `/show`, `/clear`, `/help`, `/exit`

## Available Models

- GLM-4.7 (default)
- Gemma 3 37B
- MiniMax 27B
- Kimi K2

## Templates

- FastAPI, Flask, Django (Python)
- Express, Next.js (Node.js)
- Go

## Architecture

```
4-deployment/
├── cli.py           # Main CLI tool
├── config.py         # Settings
├── templates/       # Pre-built templates
└── .env.example   # Env template
```

## License

MIT - See [LICENSE](LICENSE) file

---

**Built with ❤️ by [@keypaa](https://github.com/keypaa)**
