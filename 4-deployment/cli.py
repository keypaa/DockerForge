#!/usr/bin/env python3
"""
DockerForge CLI - Generate Dockerfiles using NVIDIA NIM API

Usage:
    python cli.py "FastAPI app with PostgreSQL"
    python cli.py --model google/gemma-4-31b-it "Node.js Express with MongoDB"
    python cli.py --template fastapi "with PostgreSQL"
    python cli.py --chat "FastAPI app"
    cat input.txt | python cli.py --stream
"""

import os
import sys
import argparse
from openai import OpenAI

# Import config and templates
import config
import templates as template_lib
import validate
import feedback

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

Respond ONLY with the Dockerfile. No explanations."""


class ChatSession:
    """Interactive chat session for iterating on Dockerfiles."""

    def __init__(self, model: str, temperature: float = 0.3):
        self.model = model
        self.temperature = temperature
        self.client = get_client()
        self.dockerfile = ""
        self.messages = []

    def start(self, description: str, template: str = None):
        """Start a new chat with initial description."""
        # Build system message
        system_msg = DOCKERFILE_SYSTEM_PROMPT

        # Add template context if provided
        if template:
            t = template_lib.get_template(template)
            if t:
                description = template_lib.render_prompt(t, description)
                system_msg += f"\n\nTemplate: {t['name']}"

        self.messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": f"Generate a Dockerfile for: {description}"},
        ]

    def generate(self) -> str:
        """Generate Dockerfile from current context."""
        # Get extra params for GLM
        extra_params = {}
        if "glm" in self.model.lower():
            extra_params["extra_body"] = {
                "chat_template_kwargs": {
                    "enable_thinking": False,
                    "clear_thinking": False,
                }
            }

        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            temperature=self.temperature,
            max_tokens=2048,
            **extra_params,
        )

        content = response.choices[0].message.content
        self.dockerfile = self._clean_dockerfile(content)
        return self.dockerfile

    def modify(self, instruction: str) -> str:
        """Modify current Dockerfile with instruction."""
        # Add current Dockerfile to context
        self.messages.append(
            {"role": "assistant", "content": f"```dockerfile\n{self.dockerfile}\n```"}
        )
        self.messages.append({"role": "user", "content": instruction})

        # Generate with updated context
        return self.generate()

    def _clean_dockerfile(self, content: str) -> str:
        """Clean up Dockerfile from response."""
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

    def print_dockerfile(self):
        """Print current Dockerfile."""
        print("\n" + "=" * 50)
        print(self.dockerfile)
        print("=" * 50)


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


def get_default_model() -> str:
    """Get default model from environment or config."""
    # First check env var
    model = os.getenv("DEFAULT_MODEL")
    if model:
        return model

    # Then check .env file
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("DEFAULT_MODEL="):
                    model = line.split("=", 1)[1].strip()
                    if model:
                        return model

    # Fall back to config default
    return config.DEFAULT_MODEL


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
        default=None,
        help=f"Model to use (default: from .env or config)",
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
    parser.add_argument(
        "--template",
        "-T",
        help=f"Use template (templates: {', '.join(template_lib.list_names())})",
    )
    parser.add_argument(
        "--list-templates", "-L", action="store_true", help="List available templates"
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Start interactive mode (llama.cpp style)",
    )
    parser.add_argument(
        "--chat", "-C", action="store_true", help="Alias for --interactive"
    )
    parser.add_argument(
        "--validate", "-V", action="store_true", help="Validate generated Dockerfile"
    )
    parser.add_argument(
        "--lint",
        action="store_true",
        help="Validate with hadolint (requires hadolint installed)",
    )

    args = parser.parse_args()

    # INTERACTIVE MODE - drops directly into prompt
    if args.interactive or args.chat:
        run_chat(args.description, args.template, args.model, args.temperature)
        return

    # List templates and exit
    if args.list_templates:
        print("Available templates:")
        for t in template_lib.list_templates():
            print(f"  {t['name']:12} - {t['description']}")
        return

    # Handle template
    base_prompt = None
    if args.template:
        template = template_lib.get_template(args.template)
        if not template:
            print(f"[!] Template not found: {args.template}", file=sys.stderr)
            print(
                f"[!] Available: {', '.join(template_lib.list_names())}",
                file=sys.stderr,
            )
            sys.exit(1)
        base_prompt = template_lib.render_prompt(template, args.description)
        print(f"[*] Using template: {template['name']}", file=sys.stderr)
        print(f"[*] Port: {template.get('defaultPort', 'N/A')}", file=sys.stderr)

    # Get model from args or .env
    model = args.model or get_default_model()

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

    # VALIDATE FILE MODE (when --validate used with a file path, not description)
    if args.validate and os.path.isfile(description):
        with open(description) as f:
            dockerfile = f.read()
        print("[*] Validating Dockerfile...", file=sys.stderr)
        if args.lint:
            print("[*] Using hadolint...", file=sys.stderr)
            valid, errors = validate.validate(dockerfile, use_hadolint=True)
        else:
            valid, errors = validate.validate(dockerfile, use_hadolint=False)

        if valid:
            print("[✓] Valid Dockerfile", file=sys.stderr)
        else:
            print("[!] Validation errors:", file=sys.stderr)
            for e in errors:
                print(f"  {e}", file=sys.stderr)
            sys.exit(1)
        return

    print("[*] Generating Dockerfile...", file=sys.stderr)
    print(f"[*] Model: {model}", file=sys.stderr)
    print(f"[*] Stream: {args.stream}", file=sys.stderr)

    try:
        final_description = base_prompt or description
        dockerfile = generate_dockerfile(
            description=final_description,
            model=model,
            temperature=args.temperature,
            stream=args.stream,
        )

        if args.stream:
            # Already printed
            return

        # Validate if requested
        if args.validate:
            print("[*] Validating...", file=sys.stderr)
            valid, errors = validate.validate(dockerfile)
            print("-" * 30, file=sys.stderr)
            if valid:
                print("[✓] Valid Dockerfile", file=sys.stderr)
                print("  - FROM instruction present", file=sys.stderr)
                print("  - Base image tag specified", file=sys.stderr)
            else:
                print("[!] Validation errors:", file=sys.stderr)
                for e in errors:
                    print(f"  - {e}", file=sys.stderr)
            print("-" * 30, file=sys.stderr)
            print()  # newline before output

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


def run_chat(
    initial_description: str = None,
    template: str = None,
    model: str = None,
    temperature: float = 0.3,
):
    """Run interactive chat mode - like llama.cpp."""
    try:
        import readline
    except ImportError:
        readline = None

    # Start with model client
    model = model or get_default_model()
    client = get_client()
    messages = []

    def build_system():
        """Build system prompt."""
        base = DOCKERFILE_SYSTEM_PROMPT
        if template:
            t = template_lib.get_template(template)
            if t:
                base += f"\n\nTemplate: {t['name']} - {t.get('prompt', '')}"
        return base

    # If initial description provided, use it
    if initial_description:
        messages = [
            {"role": "system", "content": build_system()},
            {
                "role": "user",
                "content": f"Generate a Dockerfile for: {initial_description}",
            },
        ]
    else:
        messages = [{"role": "system", "content": build_system()}]

    print("[*] DockerForge Interactive", file=sys.stderr)
    print("[*] Commands: /template /model /save /show /help /exit", file=sys.stderr)
    print("[*] Natural language goes directly to the model", file=sys.stderr)
    print("", file=sys.stderr)

    def generate(prompt: str):
        """Generate from model."""
        # Inject relevant feedback into prompt
        fb_context = feedback.format_for_prompt(prompt)
        full_prompt = f"{fb_context}\n{prompt}" if fb_context else prompt

        extra_params = {}
        if "glm" in model.lower():
            extra_params["extra_body"] = {
                "chat_template_kwargs": {
                    "enable_thinking": False,
                    "clear_thinking": False,
                }
            }

        response = client.chat.completions.create(
            model=model,
            messages=messages + [{"role": "user", "content": full_prompt}],
            temperature=temperature,
            max_tokens=2048,
            **extra_params,
        )
        return response.choices[0].message.content

    def clean(content: str) -> str:
        """Clean Dockerfile from response."""
        if "```dockerfile" in content:
            start = content.find("```dockerfile") + len("```dockerfile")
            end = content.find("```", start)
            return content[start:end].strip()
        if "```" in content:
            start = content.find("```") + 3
            end = content.find("```", start)
            if end > start:
                return content[start:end].strip()
        return content

    def print_dockerfile(df: str):
        print("\n" + "=" * 50)
        print(df)
        print("=" * 50 + "\n")

    # Generate initial if description provided
    current_dockerfile = ""
    if initial_description:
        print("[*] Generating...", file=sys.stderr)
        content = generate(f"Generate a Dockerfile for: {initial_description}")
        current_dockerfile = clean(content)
        messages.append(
            {
                "role": "assistant",
                "content": f"```dockerfile\n{current_dockerfile}\n```",
            }
        )
        print_dockerfile(current_dockerfile)

    # Chat loop
    while True:
        try:
            line = input("dockerforge> ").strip()
            if not line:
                continue

            # SLASH COMMANDS
            if line.startswith("/"):
                parts = line.split()
                cmd = parts[0].lower()

                if cmd == "/exit" or cmd == "/q":
                    break
                elif cmd == "/help":
                    print("  Commands:", file=sys.stderr)
                    print(
                        "    /template [name]  - use template (e.g., /template fastapi)",
                        file=sys.stderr,
                    )
                    print("    /model [name]    - change model", file=sys.stderr)
                    print("    /save [file]    - save Dockerfile", file=sys.stderr)
                    print(
                        "    /show          - display current Dockerfile",
                        file=sys.stderr,
                    )
                    print("    /clear        - clear chat history", file=sys.stderr)
                    print(
                        "    /feedback    - store tip (e.g., /feedback FastAPI uses port 5000)",
                        file=sys.stderr,
                    )
                    print("    /help         - show this help", file=sys.stderr)
                    print("  Examples:", file=sys.stderr)
                    print("    FastAPI with Redis", file=sys.stderr)
                    print("    make it smaller", file=sys.stderr)
                    print("    change base to alpine", file=sys.stderr)
                    continue
                elif cmd == "/save":
                    filename = parts[1] if len(parts) > 1 else "Dockerfile"
                    with open(filename, "w") as f:
                        f.write(current_dockerfile)
                    print(f"[✓] Saved to {filename}", file=sys.stderr)
                    continue
                elif cmd == "/explain":
                    # Explain the current Dockerfile
                    if not current_dockerfile:
                        print("[ ] No Dockerfile to explain", file=sys.stderr)
                        continue
                    print("[*] Analyzing Dockerfile...", file=sys.stderr)
                    explain_prompt = f"""Explain this Dockerfile in simple terms:
- What does it do?
- What language/framework?
- What are the key steps?
- Any security considerations?

Dockerfile:
{current_dockerfile}"""
                    content = generate(explain_prompt)
                    print("\n" + "=" * 50)
                    print(content)
                    print("=" * 50 + "\n")
                    continue
                elif cmd == "/show":
                    if current_dockerfile:
                        print_dockerfile(current_dockerfile)
                    else:
                        print("[ ] No Dockerfile generated yet", file=sys.stderr)
                    continue
                elif cmd == "/clear":
                    messages = [{"role": "system", "content": build_system()}]
                    current_dockerfile = ""
                    print("[*] Chat cleared", file=sys.stderr)
                    continue
                elif cmd == "/feedback":
                    # Parse: /feedback [--list|--clear] [text]
                    cmd_parts = parts[1:]
                    if "--list" in cmd_parts:
                        all_fb = feedback.list_feedback()
                        if all_fb:
                            print("  Stored feedback:", file=sys.stderr)
                            for fb in all_fb:
                                tags = fb.get("tags", [])
                                print(
                                    f"    {fb['text'][:60]} [{', '.join(tags)}]",
                                    file=sys.stderr,
                                )
                        else:
                            print("  No feedback stored yet", file=sys.stderr)
                    elif "--clear" in cmd_parts:
                        feedback.clear_feedback()
                        print("[*] Feedback cleared", file=sys.stderr)
                    elif len(cmd_parts) > 0:
                        # Store feedback text
                        fb_text = " ".join(cmd_parts)
                        feedback.add_feedback(fb_text)
                        print(f"[✓] Feedback stored", file=sys.stderr)
                    else:
                        print("  /feedback <text>   - store feedback", file=sys.stderr)
                        print("  /feedback --list   - show stored", file=sys.stderr)
                        print("  /feedback --clear - clear all", file=sys.stderr)
                    continue
                elif cmd == "/template":
                    if len(parts) > 1:
                        t = template_lib.get_template(parts[1])
                        if t:
                            template = parts[1]
                            messages[0] = {"role": "system", "content": build_system()}
                            print(f"[*] Template: {t['name']}", file=sys.stderr)
                        else:
                            print(
                                f"[!] Template not found: {parts[1]}", file=sys.stderr
                            )
                            print(
                                f"[!] Available: {', '.join(template_lib.list_names())}",
                                file=sys.stderr,
                            )
                    else:
                        print("  Templates:", file=sys.stderr)
                        for t in template_lib.list_templates():
                            print(f"    {t['name']:12} - {t['description']}")
                    continue
                elif cmd == "/model":
                    if len(parts) > 1:
                        model = parts[1]
                        print(f"[*] Model: {model}", file=sys.stderr)
                    else:
                        print(f"[*] Current model: {model}", file=sys.stderr)
                    continue
                else:
                    print(f"[!] Unknown command: {cmd}", file=sys.stderr)
                    continue

            # NATURAL LANGUAGE -> MODEL
            print("[*] Generating...", file=sys.stderr)
            content = generate(line)
            current_dockerfile = clean(content)

            messages.append(
                {
                    "role": "assistant",
                    "content": f"```dockerfile\n{current_dockerfile}\n```",
                }
            )
            print_dockerfile(current_dockerfile)

        except KeyboardInterrupt:
            print("\nbye!", file=sys.stderr)
            break
        except EOFError:
            break


if __name__ == "__main__":
    main()
