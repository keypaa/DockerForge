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
| Validation | ✅ Done | Basic + hadolint (`--validate --lint`) |

---

## Ideas for Future

| # | Feature | Priority | Notes |
|---|---------|----------|-------|
| 4 | **Generate FROM existing** | Medium | From requirements.txt / package.json |
| 5 | **Feedback system** | Medium | Auto-learns from corrections & tips, retrieves relevant on next gen |
| 6 | **History & favorites** | Medium | Save/reuse generations |
| 7 | **Analysis mode** | Medium | Optimize existing Dockerfiles |
| 8 | **Dockerfile → description** | Low | Explain what a Dockerfile does |
| 9 | **Multi-file output** | Low | .dockerignore, docker-compose.yml |
| 10 | **Preset flags** | Low | `--security`, `--small` |
| 11 | **Share via QR** | Low | Shareable URL |

---

## Priorities

### Next
- Generate FROM existing (from requirements.txt/package.json)
- History

### Later
- Analysis mode
- Multi-file output
