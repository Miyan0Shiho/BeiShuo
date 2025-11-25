import os
import json
from typing import List, Dict, Any


INDEX_DIR = os.path.join(os.path.dirname(__file__), "index")
INDEX_PATH = os.path.join(INDEX_DIR, "rag_index.json")


def ensure_index_dir():
    if not os.path.exists(INDEX_DIR):
        os.makedirs(INDEX_DIR, exist_ok=True)


def save_index(entries: List[Dict[str, Any]]):
    ensure_index_dir()
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False)


def load_index() -> List[Dict[str, Any]]:
    if not os.path.exists(INDEX_PATH):
        return []
    try:
        with open(INDEX_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []