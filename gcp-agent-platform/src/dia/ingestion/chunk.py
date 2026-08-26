"""Chunking with metadata that survives into retrieval.

The single biggest RAG quality lever is not the embedding model, it is whether
your chunk boundaries respect document structure and whether the metadata you
need for filtering is attached at write time. You cannot add it later without
a reindex.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import asdict, dataclass


@dataclass
class Chunk:
    chunk_id: str
    doc_uri: str
    text: str
    ordinal: int
    heading: str | None
    char_start: int
    char_end: int

    def to_dict(self) -> dict:
        return asdict(self)


_HEADING = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)


def _sections(markdown: str) -> list[tuple[str | None, int, int]]:
    """Split on markdown headings, returning (heading, start, end) spans."""
    matches = list(_HEADING.finditer(markdown))
    if not matches:
        return [(None, 0, len(markdown))]

    spans: list[tuple[str | None, int, int]] = []
    if matches[0].start() > 0:
        spans.append((None, 0, matches[0].start()))
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(markdown)
        spans.append((m.group(2).strip(), m.start(), end))
    return spans


def chunk_markdown(
    text: str,
    doc_uri: str,
    target_chars: int = 1800,
    overlap_chars: int = 200,
) -> list[Chunk]:
    """Structure-aware chunking: never merge across a heading, split long
    sections on paragraph boundaries with a small overlap."""
    chunks: list[Chunk] = []
    ordinal = 0

    for heading, start, end in _sections(text):
        body = text[start:end]
        if not body.strip():
            continue

        if len(body) <= target_chars:
            pieces = [(body, start, end)]
        else:
            pieces = []
            cursor = 0
            body_len = len(body)
            min_step = max(target_chars // 2, 1)
            while cursor < body_len:
                window = body[cursor : cursor + target_chars]
                if cursor + len(window) >= body_len:
                    # final piece: take the remainder, never re-split it
                    split_at = len(window)
                else:
                    # prefer a paragraph break in the back half of the window
                    split_at = window.rfind("\n\n")
                    if split_at < min_step:
                        split_at = len(window)

                piece = body[cursor : cursor + split_at]
                pieces.append((piece, start + cursor, start + cursor + len(piece)))

                if cursor + split_at >= body_len:
                    break
                # guarantee forward progress even when overlap >= split_at
                cursor += max(split_at - overlap_chars, min_step)

        for piece, p_start, p_end in pieces:
            if not piece.strip():
                continue
            digest = hashlib.sha256(f"{doc_uri}:{p_start}:{p_end}".encode()).hexdigest()[:16]
            chunks.append(
                Chunk(
                    chunk_id=digest,
                    doc_uri=doc_uri,
                    text=piece.strip(),
                    ordinal=ordinal,
                    heading=heading,
                    char_start=p_start,
                    char_end=p_end,
                )
            )
            ordinal += 1

    return chunks
