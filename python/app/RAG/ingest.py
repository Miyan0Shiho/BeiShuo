import os
import uuid
from typing import List, Dict, Any, Optional
from app.client.embedding_client import EmbeddingClient
from app.RAG.store import save_index


def read_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def split_text(text: str) -> List[Dict[str, Any]]:
    sections = ["原文：", "翻译：", "故事：", "知识点："]
    chunks: List[Dict[str, Any]] = []
    for sec in sections:
        if sec in text:
            start = text.find(sec) + len(sec)
            # 查找下一个标签作为结束
            end = len(text)
            for other in sections:
                if other == sec:
                    continue
                pos = text.find(other, start)
                if pos != -1:
                    end = min(end, pos)
            content = text[start:end].strip()
            if content:
                chunks.append({"section": sec, "text": content})
    if not chunks:
        # 回退：按定长分块
        step = 1200
        s = 0
        while s < len(text):
            piece = text[s:s + step].strip()
            if piece:
                chunks.append({"section": "全文", "text": piece})
            s += step
    return chunks


async def build_index_from_path(path: str, dimensions: Optional[int] = 1024):
    entries: List[Dict[str, Any]] = []
    files: List[str] = []
    if os.path.isdir(path):
        for name in os.listdir(path):
            fp = os.path.join(path, name)
            if os.path.isfile(fp) and fp.lower().endswith((".txt", ".md")):
                files.append(fp)
    else:
        files.append(path)

    texts: List[str] = []
    metas: List[Dict[str, Any]] = []

    for fp in files:
        content = read_text_file(fp)
        chunks = split_text(content)
        for c in chunks:
            texts.append(c["text"])
            metas.append({"source_path": fp, "section": c["section"]})

    if not texts:
        save_index([])
        return

    client = EmbeddingClient()
    try:
        embeddings = await client.embed_texts(texts, dimensions=dimensions)
    finally:
        await client.close()

    for i, emb in enumerate(embeddings):
        entries.append({
            "id": str(uuid.uuid4()),
            "text": texts[i],
            "meta": metas[i],
            "embedding": emb,
        })

    save_index(entries)