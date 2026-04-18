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
| Feedback system | ✅ Done | /feedback command with auto-retrieval |
| /explain | ✅ Done | Describe what a Dockerfile does |

---

## Ideas for Future

| # | Feature | Priority | Notes |
|---|---------|----------|-------|
| 4 | **Generate FROM existing** | ✅ Done | /from command parses requirements.txt etc. |
| 5 | **History & favorites** | Medium | Save/reuse generations |
| 6 | **Analysis mode** | Medium | Optimize existing Dockerfiles |
| 7 | **Multi-file output** | Low | .dockerignore, docker-compose.yml |
| 8 | **Preset flags** | Low | `--security`, `--small` |
| 9 | **Share via QR** | Low | Shareable URL |

---

## Priorities

### Next
- Generate FROM existing (from requirements.txt/package.json)
- History

### Later
- Analysis mode
- Multi-file output
