"""
Feedback system - learns from corrections and tips.
"""

import json
import os
import re
from pathlib import Path
from typing import List, Dict, Optional

FEEDBACK_FILE = Path(__file__).parent / "feedback.json"


def load_feedback() -> List[Dict]:
    """Load all feedback entries."""
    if not FEEDBACK_FILE.exists():
        return []
    with open(FEEDBACK_FILE) as f:
        return json.load(f)


def save_feedback(entries: List[Dict]):
    """Save feedback entries."""
    with open(FEEDBACK_FILE, "w") as f:
        json.dump(entries, f, indent=2)


def add_feedback(text: str, tags: List[str] = None) -> bool:
    """Add new feedback.

    Args:
        text: Feedback text (e.g., "FastAPI uses port 5000")
        tags: Optional tags (e.g., ["fastapi", "port"])

    Returns:
        True if added successfully
    """
    # Extract tags from text if #tag format used
    found_tags = re.findall(r"#(\w+)", text)
    if tags:
        found_tags.extend(tags)

    entries = load_feedback()
    entries.append({"text": text, "tags": list(set(found_tags)), "added": "now"})
    save_feedback(entries)
    return True


def get_relevant_feedback(prompt: str, limit: int = 5) -> List[str]:
    """Get feedback relevant to the current prompt.

    Searches for matching tags or keywords in stored feedback.

    Args:
        prompt: User's description (e.g., "FastAPI with PostgreSQL")
        limit: Max number of feedback items to return

    Returns:
        List of relevant feedback texts
    """
    entries = load_feedback()
    if not entries:
        return []

    # Extract keywords from prompt
    words = set(re.findall(r"\w+", prompt.lower()))

    # Score each entry
    scored = []
    for entry in entries:
        score = 0
        entry_text = entry.get("text", "").lower()
        entry_tags = entry.get("tags", [])

        # Tag match (high score)
        for tag in entry_tags:
            if tag.lower() in words:
                score += 10

        # Keyword in text (medium score)
        for word in words:
            if len(word) > 3 and word in entry_text:
                score += 1

        if score > 0:
            scored.append((score, entry["text"]))

    # Sort by score, return top results
    scored.sort(reverse=True, key=lambda x: x[0])
    return [text for _, text in scored[:limit]]


def list_feedback() -> List[Dict]:
    """List all feedback entries."""
    return load_feedback()


def clear_feedback():
    """Clear all feedback."""
    save_feedback([])


def format_for_prompt(prompt: str) -> str:
    """Format relevant feedback for injection into prompt.

    Returns a string to prepend to the prompt, or empty string.
    """
    relevant = get_relevant_feedback(prompt)
    if not relevant:
        return ""

    formatted = "\n".join([f"- {fb}" for fb in relevant])
    return f"\nRemember:\n{formatted}\n"


if __name__ == "__main__":
    # Test
    add_feedback("FastAPI uses port 5000, not 8000", ["fastapi", "port"])
    add_feedback("PostgreSQL uses port 5432", ["postgres", "db"])
    add_feedback("Use alpine for smaller images", ["security", "size"])

    print("All feedback:")
    for fb in list_feedback():
        print(f"  {fb}")

    print("\nRelevant to 'FastAPI with PostgreSQL':")
    for fb in get_relevant_feedback("FastAPI with PostgreSQL"):
        print(f"  {fb}")
