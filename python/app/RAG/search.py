from typing import List, Dict, Any
import math
from app.RAG.store import load_index


def cosine(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def retrieve_local(query_embedding: List[float], top_k: int = 5) -> List[str]:
    index: List[Dict[str, Any]] = load_index()
    if not index:
        return []
    scored = []
    for entry in index:
        emb = entry.get("embedding") or []
        score = cosine(query_embedding, emb)
        scored.append((score, entry))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [e["text"] for _, e in scored[:top_k]]