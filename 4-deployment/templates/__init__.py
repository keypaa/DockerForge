"""
Template library loader.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional

TEMPLATES_DIR = Path(__file__).parent


def list_templates() -> List[Dict]:
    """List all available templates."""
    templates = []
    for path in TEMPLATES_DIR.glob("*.json"):
        if path.stem == "__init__":
            continue
        with open(path) as f:
            templates.append(json.load(f))
    return sorted(templates, key=lambda t: t["name"])


def get_template(name: str) -> Optional[Dict]:
    """Get template by name (case-insensitive)."""
    name_lower = name.lower()
    for path in TEMPLATES_DIR.glob("*.json"):
        if path.stem == "__init__":
            continue
        with open(path) as f:
            template = json.load(f)
        if template["name"].lower() == name_lower:
            return template
    return None


def render_prompt(template: Dict, custom_description: str = "") -> str:
    """Render template prompt with optional custom description."""
    base = template.get("prompt", "")
    if custom_description:
        return f"{base}\n\nAdditional requirements: {custom_description}"
    return base


def list_names() -> List[str]:
    """List template names."""
    return [t["name"] for t in list_templates()]


if __name__ == "__main__":
    # List all templates
    print("Available templates:")
    for t in list_templates():
        print(f"  {t['name']:12} - {t['description']}")
