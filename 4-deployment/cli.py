#!/usr/bin/env python3
"""
DockerForge CLI - Generate Dockerfiles using NVIDIA NIM API

Usage:
    python cli.py "FastAPI app with PostgreSQL"
    python cli.py --model z-ai/glm4.7 "Node.js Express with MongoDB"
    cat input.txt | python cli.py --stream
"""

import os
import sys
import argparse
from openai import OpenAI

# Import config
import config

# Configuration
NIM_BASE_URL = config.NIM_BASE_URL
DEFAULT_MODEL = config.DEFAULT_MODEL

# Dockerfile generation prompt template
DOCKERFILE_SYSTEM_PROMPT = """You are an expert at writing production-ready Dockerfiles.

Guidelines:
- Use official base images (python:, node:, golang:, etc.)
- Multi-stage builds to minimize image size
- Layer caching: dependencies first, then code
- Non-root user for security
- Proper CMD/ENTRYPOINT
- Expose only needed ports

Respond ONLY with the complete Dockerfile. No markdown fences, no explanations."""


def get_api_key() -> str:
    """Get NIM API key from environment."""
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        # Try to load from .env file
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("NVIDIA_API_KEY="):
                        api_key = line.split("=", 1)[1].strip()
                        break

    if not api_key:
        raise ValueError("NVIDIA_API_KEY not set. Set via env or .env file.")
    return api_key


def get_client() -> OpenAI:
    """Create OpenAI client configured for NIM."""
    return OpenAI(base_url=NIM_BASE_URL, api_key=get_api_key())


def generate_dockerfile(
    description: str,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.3,
    max_tokens: int = 2048,
    stream: bool = False,
) -> str:
    """Generate Dockerfile using NIM API."""
    client = get_client()

    messages = [
        {"role": "system", "content": DOCKERFILE_SYSTEM_PROMPT},
        {"role": "user", "content": f"Generate a Dockerfile for: {description}"},
    ]

    extra_params = {}
    if "glm" in model.lower():
        # GLM supports thinking
        extra_params["extra_body"] = {
            "chat_template_kwargs": {"enable_thinking": False, "clear_thinking": False}
        }

    if stream:
        return stream_dockerfile(
            client, model, messages, temperature, max_tokens, extra_params
        )

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        **extra_params,
    )

    content = response.choices[0].message.content

    # Clean up - extract Dockerfile if wrapped in markdown
    if "```dockerfile" in content:
        start = content.find("```dockerfile") + len("```dockerfile")
        end = content.find("```", start)
        content = content[start:end].strip()
    elif "```" in content:
        start = content.find("```") + 3
        end = content.find("```", start)
        if end > start:
            content = content[start:end].strip()

    return content


def stream_dockerfile(client, model, messages, temperature, max_tokens, extra_params):
    """Stream generate Dockerfile."""
    use_color = sys.stdout.isatty()
    reasoning_color = "\033[90m" if use_color else ""
    reset_color = "\033[0m" if use_color else ""

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True,
        **extra_params,
    )

    full_content = ""
    for chunk in response:
        if not hasattr(chunk, "choices") or not chunk.choices:
            continue
        delta = chunk.choices[0].delta
        if not delta:
            continue

        # Handle reasoning (thinking)
        if hasattr(delta, "reasoning_content") and delta.reasoning_content:
            print(
                f"{reasoning_color}{delta.reasoning_content}{reset_color}",
                end="",
                flush=True,
            )

        # Handle content
        if hasattr(delta, "content") and delta.content:
            print(delta.content, end="", flush=True)
            full_content += delta.content

    print()  # newline
    return full_content


def main():
    parser = argparse.ArgumentParser(
        description="DockerForge - Generate Dockerfiles from natural language"
    )
    parser.add_argument(
        "description", nargs="?", help="Description of what to containerize"
    )
    parser.add_argument(
        "--model",
        "-m",
        default=DEFAULT_MODEL,
        help=f"Model to use (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--temperature",
        "-t",
        type=float,
        default=0.3,
        help="Temperature (default: 0.3)",
    )
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    parser.add_argument("--stream", action="store_true", help="Stream output")

    args = parser.parse_args()

    # Get description from args or stdin
    description = args.description
    if not description:
        if sys.stdin.isatty():
            parser.print_help()
            return
        description = sys.stdin.read().strip()

    if not description:
        print("Error: No description provided", file=sys.stderr)
        sys.exit(1)

    print("[*] Generating Dockerfile...", file=sys.stderr)
    print(f"[*] Model: {args.model}", file=sys.stderr)
    print(f"[*] Stream: {args.stream}", file=sys.stderr)

    try:
        dockerfile = generate_dockerfile(
            description=description,
            model=args.model,
            temperature=args.temperature,
            stream=args.stream,
        )

        if args.stream:
            # Already printed
            return

        # Output
        if args.output:
            with open(args.output, "w") as f:
                f.write(dockerfile)
            print(f"[✓] Saved to {args.output}", file=sys.stderr)
        else:
            print(dockerfile)

    except Exception as e:
        print(f"[!] Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
