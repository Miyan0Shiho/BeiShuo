from typing import List
from app.LLM.models import ReferenceCard


def contexts_to_references(contexts: List[str]) -> List[ReferenceCard]:
    refs: List[ReferenceCard] = []
    for i, c in enumerate(contexts):
        refs.append(ReferenceCard(
            id=f"ref_{i}",
            title=None,
            type="inscription",
            snippet=c,
            meta={"relevance": 1.0}
        ))
    return refs