from app.RAG.search import cosine, retrieve_local
from app.RAG.store import save_index


def test_cosine_basic():
    a = [1.0, 0.0]
    b = [1.0, 0.0]
    c = [0.0, 1.0]
    assert abs(cosine(a, b) - 1.0) < 1e-6
    assert abs(cosine(a, c) - 0.0) < 1e-6


def test_retrieve_local_topk():
    save_index([
        {"id": "1", "text": "九成宫醴泉铭 原文片段", "meta": {}, "embedding": [0.9, 0.1]},
        {"id": "2", "text": "多宝塔碑 原文片段", "meta": {}, "embedding": [0.1, 0.9]},
    ])
    res = retrieve_local([1.0, 0.0], top_k=1)
    assert len(res) == 1
    assert "九成宫" in res[0]