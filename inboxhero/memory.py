"""Small persistent standing-instruction store adapted from the supplied memory.py."""
import json
from pathlib import Path

MEMORY_FILE = Path("memory.json")

def load_memory():
    if not MEMORY_FILE.exists():
        return []
    try:
        return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []

def save_memory(memory):
    MEMORY_FILE.write_text(json.dumps(memory, indent=2), encoding="utf-8")

def remember(key, value, source, kind="standing_preference"):
    memory = load_memory()
    nk = key.strip().lower()
    item = {"key": key, "value": value, "source": source, "type": kind}
    for i, old in enumerate(memory):
        if old.get("key", "").strip().lower() == nk:
            memory[i] = item
            save_memory(memory)
            return item
    memory.append(item)
    save_memory(memory)
    return item

def recall_all():
    return load_memory()
