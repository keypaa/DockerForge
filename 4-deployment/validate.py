"""
Dockerfile validation module.
"""

import re
import subprocess
from typing import List, Tuple

# Valid Dockerfile instructions (in order they should appear)
VALID_INSTRUCTIONS = [
    "FROM",
    "ARG",
    "LABEL",
    "ENV",
    "COPY",
    "WORKDIR",
    "RUN",
    "EXPOSE",
    "VOLUME",
    "USER",
    "ENTRYPOINT",
    "CMD",
]

# Required instructions
REQUIRED = ["FROM"]

# Best practices rules
RULES = {
    "DL3001": "Do not use :latest tag for base image",
    "DL3006": "Always specify a tag for base image",
    "DL3008": "Do not use :latest in apt-get install",
    "DL3015": "Avoid multiple RUN apt-get, combine",
    "DL3016": "Pin versions in pip install",
    "DL3018": "Don't use --no-cache-dir in pip install",
}


def validate_syntax(dockerfile: str) -> Tuple[bool, List[str]]:
    """Validate Dockerfile syntax - basic checks only.

    Returns (is_valid, errors)
    """
    errors = []
    lines = dockerfile.split("\n")

    if not dockerfile.strip():
        return False, ["Empty Dockerfile"]

    # Check FROM exists
    has_from = False
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.upper().startswith("FROM "):
            has_from = True
            # Check for :latest
            if ":latest" in line.lower() or re.match(
                r"^FROM\s+\w+$", line, re.IGNORECASE
            ):
                errors.append(f"Line {i}: Specify base image tag (not :latest)")
            break

    if not has_from:
        errors.append("FROM instruction is required")

    return len(errors) == 0, errors


def validate_hadolint(dockerfile: str) -> Tuple[bool, List[str]]:
    """Validate using hadolint if available.

    Returns (is_valid, errors)
    """
    try:
        result = subprocess.run(
            ["hadolint", "-"],
            input=dockerfile,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            return True, []

        errors = result.stdout.strip().split("\n")
        return False, [e for e in errors if e]
    except FileNotFoundError:
        return False, [
            "hadolint not installed. Install from: https://github.com/hadolint/hadolint"
        ]
    except Exception as e:
        return False, [str(e)]


def validate(dockerfile: str, use_hadolint: bool = False) -> Tuple[bool, List[str]]:
    """Validate Dockerfile.

    Args:
        dockerfile: Dockerfile content
        use_hadolint: Use hadolint if available

    Returns:
        (is_valid, errors)
    """
    # First do basic syntax check
    valid, errors = validate_syntax(dockerfile)

    # If basic check fails, return early
    if not valid:
        return False, errors

    # If basic passed and hadolint requested
    if use_hadolint:
        return validate_hadolint(dockerfile)

    return True, []


if __name__ == "__main__":
    # Test
    test_df = """FROM python:3.11-slim
RUN pip install --no-cache-dir flask
COPY . .
CMD ["python", "app.py"]
"""
    valid, errors = validate(test_df)
    print(f"Valid: {valid}")
    print(f"Errors: {errors}")
