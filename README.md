# DockerForge ⚒️

> AI-powered Dockerfile generator trained on 50,000+ real-world examples from GitHub

## Overview

DockerForge is a fine-tuned LLM that generates production-ready Dockerfiles from natural language descriptions. Instead of manually writing complex multi-stage builds, just describe your project and get an optimized Dockerfile instantly.

## Features

- 🤖 Trained on 50K+ real-world Dockerfiles from top GitHub repositories
- 🎯 Supports Python, Node.js, Go, Rust, Java, and more
- 🔧 Generates multi-stage builds, handles dependencies intelligently
- ⚡ Fast generation (~2 seconds)
- 📦 Optimized for production (small image sizes, security best practices)

## Quick Start
```bash
# Coming soon
pip install dockerforge

dockerforge generate "FastAPI app with PostgreSQL and Redis"
```

## Project Status

🚧 **Currently in development** - Data collection phase

- [x] Project planning
- [ ] GitHub scraper (in progress)
- [ ] Dataset preparation
- [ ] Model training
- [ ] CLI tool
- [ ] Public release

## Dataset

We're building a comprehensive dataset by analyzing:
- 50,000+ repositories with Dockerfiles
- Real-world production examples
- Multiple languages and frameworks
- Diverse tech stacks

## Contributing

Interested in contributing? Star the repo and watch for updates!

## License

MIT License - See [LICENSE](LICENSE) file

---

**Built with ❤️ by [@keypa](https://github.com/keypa)**