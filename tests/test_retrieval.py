from pathlib import Path

from app.retrieval import Retriever


def test_retriever_finds_student_sources() -> None:
    retriever = Retriever(Path("data/sources"))
    citations = retriever.search("college MSA welcoming new students", limit=2)

    assert citations
    assert citations[0].source_id == "student-productivity"
    assert "students" in citations[0].excerpt.lower()
