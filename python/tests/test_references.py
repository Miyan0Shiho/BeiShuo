from app.RAG.references import contexts_to_references


def test_contexts_to_references_basic():
    contexts = ["片段一", "片段二"]
    refs = contexts_to_references(contexts)
    assert len(refs) == 2
    assert refs[0].snippet == "片段一"
    assert refs[1].type == "inscription"