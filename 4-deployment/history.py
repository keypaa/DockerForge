"""
History module - stores generated Dockerfiles.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

HISTORY_FILE = Path(__file__).parent / "history.json"
MAX_HISTORY = 50


def load_history() -> List[Dict]:
    """Load history."""
    if not HISTORY_FILE.exists():
        return []
    with open(HISTORY_FILE) as f:
        return json.load(f)


def save_history(entries: List[Dict]):
    """Save history."""
    with open(HISTORY_FILE, "w") as f:
        json.dump(entries, f, indent=2)


def add_entry(prompt: str, dockerfile: str, tags: List[str] = None) -> bool:
    """Add entry to history."""
    entries = load_history()

    # Add new entry at beginning
    entry = {
        "prompt": prompt[:200],  # Truncate long prompts
        "dockerfile": dockerfile,
        "tags": tags or [],
        "timestamp": datetime.now().isoformat(),
    }
    entries.insert(0, entry)

    # Keep only MAX_HISTORY entries
    if len(entries) > MAX_HISTORY:
        entries = entries[:MAX_HISTORY]

    save_history(entries)
    return True


def list_history(limit: int = 10) -> List[Dict]:
    """List history entries."""
    entries = load_history()
    return entries[:limit]


def search_history(query: str) -> List[Dict]:
    """Search history for matching entries."""
    entries = load_history()
    query = query.lower()
    results = []
    for entry in entries:
        if query in entry.get("prompt", "").lower():
            results.append(entry)
    return results


def get_entry(index: int) -> Optional[Dict]:
    """Get entry by index."""
    entries = load_history()
    if 0 <= index < len(entries):
        return entries[index]
    return None


def clear_history():
    """Clear all history."""
    save_history([])


if __name__ == "__main__":
    # Test
    print("History test:")
    for h in list_history(5):
        print(f"  {h.get('timestamp', '')} - {h.get('prompt', '')[:50]}")
