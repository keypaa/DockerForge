"""
Multi-file output - generates .dockerignore and docker-compose.yml
"""

import os
import re
from typing import Dict, Optional


DOCKERIGNORE_TEMPLATE = """# Git
.git
.gitignore

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
.venv/
*.egg-info/
dist/
build/

# Node
node_modules/
npm-debug.log
yarn-error.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Build
Dockerfile
.dockerignore
docker-compose.yml

# Logs
*.log

# Temp
*.tmp
.cache/
"""


def get_language(dockerfile: str) -> str:
    """Detect language from Dockerfile."""
    dockerfile = dockerfile.lower()
    if "python" in dockerfile or "pip" in dockerfile:
        return "python"
    if "node" in dockerfile or "npm" in dockerfile or "yarn" in dockerfile:
        return "node"
    if "golang" in dockerfile or "go mod" in dockerfile:
        return "go"
    if "rust" in dockerfile or "cargo" in dockerfile:
        return "rust"
    if "java" in dockerfile or "maven" in dockerfile or "gradle" in dockerfile:
        return "java"
    return "generic"


def get_exposed_port(dockerfile: str) -> Optional[int]:
    """Extract exposed port from Dockerfile."""
    match = re.search(r"EXPOSE\s+(\d+)", dockerfile, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


def get_service_name(dockerfile: str) -> str:
    """Extract or infer service name."""
    # Try to find from COPY or WORKDIR
    match = re.search(r"COPY\s+\.\s+/?(\w+)", dockerfile, re.IGNORECASE)
    if match:
        return match.group(1)
    match = re.search(r"WORKDIR\s+/app/?(\w+)", dockerfile, re.IGNORECASE)
    if match:
        return match.group(1)
    # Default based on language
    lang = get_language(dockerfile)
    return {
        "python": "api",
        "node": "api",
        "go": "app",
        "rust": "app",
    }.get(lang, "app")


def generate_dockerignore(dockerfile: str) -> str:
    """Generate .dockerignore."""
    lang = get_language(dockerfile)

    base = """# Git
.git
.gitignore

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Build
Dockerfile
docker-compose.yml
"""

    if lang == "python":
        base += """
# Python
__pycache__/
*.py[cod]
*.so
.Python
venv/
.venv/
*.egg-info/
dist/
build/
"""
    elif lang == "node":
        base += """
# Node
node_modules/
npm-debug.log
"""
    elif lang == "go":
        base += """
# Go
*.sum
"""

    return base.strip()


def generate_compose(dockerfile: str) -> str:
    """Generate docker-compose.yml."""
    port = get_exposed_port(dockerfile)
    service = get_service_name(dockerfile)
    lang = get_language(dockerfile)

    # Build section
    build = f"build: ."

    # Determine run command from CMD
    cmd_match = re.search(r"CMD\s+\[(.*?)\]", dockerfile, re.IGNORECASE)
    if cmd_match:
        cmd = cmd_match.group(1).replace('"', "")
    else:
        cmd = None

    # Service config
    service_config = f"""version: '3.8'

services:
  {service}:
    {build}
"""

    if port:
        service_config += f"""    ports:
      - "{port}:{port}"
"""

    if cmd:
        service_config += f"""    command: {cmd}
"""

    # Add environment for non-root
    if "USER" in dockerfile or "appuser" in dockerfile:
        service_config += """    user: "1000:1000"
"""

    service_config += """    environment:
      - DEBUG=0
"""

    # Common volumes
    if lang == "python":
        service_config += """    volumes:
      - .:/app
"""

    service_config += """    restart: unless-stopped
"""

    return service_config


def generate_all(dockerfile: str) -> Dict[str, str]:
    """Generate all multi-file outputs."""
    return {
        ".dockerignore": generate_dockerignore(dockerfile),
        "docker-compose.yml": generate_compose(dockerfile),
    }


if __name__ == "__main__":
    test = """FROM python:3.11-slim
WORKDIR /app
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app"]
"""
    print(generate_compose(test))
