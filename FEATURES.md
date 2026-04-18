# DockerForge Features

Tracking ideas and implementation status.

---

## ✅ Implemented

| Feature | Status | Notes |
|---------|--------|-------|
| CLI tool | ✅ Done | `python cli.py "description"` |
| Streaming | ✅ Done | `--stream` flag |
| Multiple models | ✅ Done | Gemma 4, MiniMax M2.7, Nemotron, Qwen |
| Interactive mode | ✅ Done | `-i` with /slash commands |
| Template library | ✅ Done | FastAPI, Django, Express, Next.js, Go, Flask |
| .env config | ✅ Done | DEFAULT_MODEL reads from .env |

---

## Ideas for Future

| # | Feature | Priority | Notes |
|---|---------|----------|-------|
| 3 | **Dockerfile validation** | High | `docker build --dry-run` to verify |
| 4 | **Generate FROM existing** | Medium | From requirements.txt / package.json |
| 5 | **History & favorites** | Medium | Save/reuse generations |
| 6 | **Analysis mode** | Medium | Optimize existing Dockerfiles |
| 7 | **Dockerfile → description** | Low | Explain what a Dockerfile does |
| 8 | **Multi-file output** | Low | .dockerignore, docker-compose.yml |
| 9 | **Preset flags** | Low | `--security`, `--small` |
| 10 | **Share via QR** | Low | Shareable URL |

---

## Priorities

### Next
- Dockerfile validation

### Later
- Generate FROM existing
- Analysis mode
- History
