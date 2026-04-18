# DockerForge QuickStart ⚒️

> Generate production-ready Dockerfiles in seconds

## TL;DR

```bash
# Generate a Dockerfile
python 4-deployment/cli.py "FastAPI with PostgreSQL"

# Or start interactive mode
python 4-deployment/cli.py -i
```

---

## Quick Examples

### One-liner Mode

```bash
# Basic
python cli.py "FastAPI with Redis"

# With template
python cli.py --template fastapi "with MongoDB"

# Save to file
python cli.py "Go API" -o Dockerfile

# Validate
python cli.py "Node app" --validate --lint

# Generate all (Dockerfile + compose + dockerignore)
python cli.py "Flask app" --compose
```

### Interactive Mode

```bash
python cli.py -i
```

```
dockerforge> FastAPI with Redis
[generates...]
dockerforge> change base to alpine
dockerforge> /save
dockerforge> /exit
```

---

## Commands in Interactive Mode

| Command | Description |
|---------|-------------|
| `FastAPI with Redis` | Generate from natural language |
| `change base to alpine` | Modify the Dockerfile |
| `/template fastapi` | Use FastAPI template |
| `/from requirements.txt` | Generate from deps file |
| `/explain` | Explain current Dockerfile |
| `/save myfile` | Save to file |
| `/history` | Show recent generations |
| `/feedback FastAPI uses port 5000` | Store a tip |
| `/compose` | Generate docker-compose.yml + .dockerignore |
| `/help` | Show all commands |
| `/exit` | Exit |

---

## Tips & Tricks

### 1. Feedback System (Auto-Learning)

Store corrections once, applies to all future generations:

```
/feedback FastAPI uses port 5000
/feedback #postgres PostgreSQL uses port 5432
/feedback #security Use alpine for smaller images
```

Next time you generate "FastAPI", it remembers port 5000!

### 2. Templates for Common Stacks

```bash
/template fastapi    # Python FastAPI
/template flask      # Python Flask  
/template django    # Python Django
/template express   # Node.js Express
/template nextjs    # Next.js
/template go        # Go
```

### 3. Generate from Existing Files

Don't type dependencies manually:

```bash
# Looks for requirements.txt, package.json, go.mod automatically
/from

# Or specify file
/from requirements.txt
/from package.json
```

### 4. Validation (Important!)

Always validate with hadolint:

```bash
python cli.py "FastAPI" --validate --lint
```

Fixes common issues:
- Using `:latest` tag
- Not pinning pip versions
- Running as root
- Missing multi-stage builds

### 5. Multi-File Output

Generate complete setup:

```bash
python cli.py "FastAPI" --compose
```

Creates:
- `Dockerfile`
- `docker-compose.yml`
- `.dockerignore`

### 6. History

See what you've generated:

```bash
/history      # Last 5
/history 10   # Last 10
```

### 7. Model Selection

Switch models for different needs:

```
/model google/gemma-4-31b-it   # Best overall
/minimaxai/minimax-m2.7       # Fast
/nvidia/nemotron-3-super-120b-a12b  # Large
/qwen/qwen3.5-122b-a10b       # Code-heavy
```

---

## Workflows

### New Project (from scratch)
```bash
python cli.py -i
> /template fastapi
> My new API with Redis and PostgreSQL
> /save
> /compose
> /exit
```

### New Project (existing deps)
```bash
python cli.py -i
> /from
> add Redis caching
> /save
> /exit
```

### Fix Issues
```bash
python cli.py "FastAPI" --validate --lint
# See errors, then in interactive:
> change base to alpine
> remove --no-cache-dir
> /feedback Use alpine for smaller images
```

---

## Setup

```bash
# 1. Get API key
# Visit https://build.nvidia.com → Select model → Get API Key

# 2. Configure
cp 4-deployment/.env.example 4-deployment/.env
# Edit .env with your NVIDIA_API_KEY
# Optionally set DEFAULT_MODEL
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No API key | Set `NVIDIA_API_KEY` in .env |
| Hadolint not found | `scoop install hadolint` (Windows) |
| Model not working | Try different model with `/model` |
| Bad output | Use interactive mode to iterate |

---

**Pro Tip:** Use `--stream` to see the model thinking in real-time:

```bash
python cli.py "Complex API" --stream
```