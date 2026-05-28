from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from app.schemas import Citation, SourceSummary

TOKEN_RE = re.compile(r"[a-zA-Z0-9']+")


@dataclass(frozen=True)
class SourceChunk:
    source_id: str
    title: str
    tags: tuple[str, ...]
    path: str
    heading: str
    text: str


def tokenize(value: str) -> set[str]:
    return {token.lower() for token in TOKEN_RE.findall(value)}


def _parse_metadata(lines: list[str]) -> tuple[dict[str, str], list[str]]:
    metadata: dict[str, str] = {}
    body_start = 0
    for index, line in enumerate(lines):
        if not line.strip():
            body_start = index + 1
            break
        if ":" not in line:
            break
        key, value = line.split(":", 1)
        metadata[key.strip().lower()] = value.strip()
    return metadata, lines[body_start:]


def _chunk_body(body: str) -> list[tuple[str, str]]:
    chunks: list[tuple[str, str]] = []
    current_heading = "Overview"
    current_lines: list[str] = []

    for line in body.splitlines():
        if line.startswith("## "):
            if current_lines:
                chunks.append((current_heading, "\n".join(current_lines).strip()))
                current_lines = []
            current_heading = line.replace("## ", "", 1).strip()
        else:
            current_lines.append(line)

    if current_lines:
        chunks.append((current_heading, "\n".join(current_lines).strip()))

    return [(heading, text) for heading, text in chunks if text]


def load_sources(data_dir: Path) -> list[SourceChunk]:
    chunks: list[SourceChunk] = []
    for path in sorted(data_dir.glob("*.md")):
        lines = path.read_text(encoding="utf-8").splitlines()
        metadata, body_lines = _parse_metadata(lines)
        title = metadata.get("title", path.stem.replace("-", " ").title())
        source_id = metadata.get("source_id", path.stem)
        tags = tuple(tag.strip() for tag in metadata.get("tags", "").split(",") if tag.strip())
        body = "\n".join(body_lines)
        for heading, text in _chunk_body(body):
            chunks.append(
                SourceChunk(
                    source_id=source_id,
                    title=title,
                    tags=tags,
                    path=str(path),
                    heading=heading,
                    text=text,
                )
            )
    return chunks


class Retriever:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.chunks = load_sources(data_dir)

    def list_sources(self) -> list[SourceSummary]:
        seen: dict[str, SourceSummary] = {}
        for chunk in self.chunks:
            seen.setdefault(
                chunk.source_id,
                SourceSummary(
                    source_id=chunk.source_id,
                    title=chunk.title,
                    tags=list(chunk.tags),
                    path=chunk.path,
                ),
            )
        return list(seen.values())

    def search(self, query: str, limit: int = 4) -> list[Citation]:
        query_tokens = tokenize(query)
        scored: list[tuple[float, SourceChunk]] = []
        for chunk in self.chunks:
            chunk_tokens = tokenize(" ".join([chunk.title, chunk.heading, " ".join(chunk.tags), chunk.text]))
            overlap = query_tokens & chunk_tokens
            if not overlap:
                continue
            title_boost = len(query_tokens & tokenize(chunk.title)) * 1.5
            tag_boost = len(query_tokens & tokenize(" ".join(chunk.tags))) * 1.25
            heading_boost = len(query_tokens & tokenize(chunk.heading))
            score = len(overlap) + title_boost + tag_boost + heading_boost
            scored.append((score, chunk))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [self._to_citation(chunk, score) for score, chunk in scored[:limit]]

    def _to_citation(self, chunk: SourceChunk, score: float) -> Citation:
        compact_text = " ".join(chunk.text.split())
        excerpt = compact_text[:240] + ("..." if len(compact_text) > 240 else "")
        return Citation(
            source_id=chunk.source_id,
            title=chunk.title,
            path=chunk.path,
            heading=chunk.heading,
            score=round(score, 2),
            excerpt=excerpt,
        )
