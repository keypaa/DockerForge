# DockerForge Features

Tracking ideas and implementation status.

---

## Implemented

| # | Feature | Status | Notes |
|---|---------|--------|-------|
| - | CLI tool | ✅ Done | `python cli.py " description "` |
| - | Streaming with reasoning | ✅ Done | `--stream` flag |
| - | Multiple models | ✅ Done | GLM-4.7, Gemma, MiniMax, Kimi |

---

## Ideas for Future

| # | Feature | Priority | Real Purpose | Notes |
|---|---------|----------|--------------|-------|
| 1 | **Interactive mode** | ✅ Done | llama.cpp style: /template /model /save + natural language | ✅ Done |
| 2 | **Template library** | ✅ Done | Templates for FastAPI, Django, Express, Next.js, Go, Flask | ✅ Done |
| 3 | **Dockerfile validation** | High | Run `docker build --dry-run` to verify it actually works | Quality assurance, differentiator |
| 4 | **Generate FROM existing** | Medium | Paste a `requirements.txt` or `package.json` and it generates the Dockerfile | Low-friction start |
| 5 | **History & favorites** | Medium | Save/reuse previous generations with tags | Productivity |
| 6 | **Analysis mode** | Medium | Paste existing Dockerfile, get optimization suggestions | Help users improve |
| 7 | **Dockerfile → description** | Low | Reverse: given a Dockerfile, explain what it does | Learning |
| 8 | **Multi-file output** | Low | Also generate `.dockerignore`, `docker-compose.yml` | Complete setup |
| 9 | **Preset flags** | Low | `--security`, `--small`, `--debug` to tweak output style | Control |
| 10 | **Share via QR** | Low | Generate a shareable URL with the Dockerfile embedded | Sharing |

---

## Priority Queue

### Next
1. Template library
2. Chat mode

### Later
3. Dockerfile validation
4. Generate FROM existing
5. Analysis mode