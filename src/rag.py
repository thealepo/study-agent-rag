from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pymupdf


DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def load_embedding_model(model_name: str = DEFAULT_EMBEDDING_MODEL):
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(model_name)


def extract_pdf_text(file_path: str | Path) -> tuple[str, int]:
    """Extract plain text from every page of a PDF."""
    with pymupdf.open(file_path) as doc:
        text = "".join(page.get_text() for page in doc)
        num_pages = len(doc)

    return text, num_pages


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 200,
) -> list[str]:
    """Split text into overlapping character chunks."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "overlap must satisfy 0 <= overlap < chunk_size"
        )

    step = chunk_size - overlap
    chunks: list[str] = []

    for i in range(0, len(text), step):
        chunk = text[i:i + chunk_size]

        if chunk.strip():
            chunks.append(chunk)

    return chunks


def embed_chunks(model: Any, chunks: list[str]) -> np.ndarray:
    """Embed all chunks and normalize them for cosine similarity."""
    if not chunks:
        return np.empty((0, 0), dtype=np.float32)

    return model.encode(
        chunks,
        normalize_embeddings=True,
    )


def similarities(
    query: str,
    model: Any,
    embeddings: np.ndarray,
    topk: int = 5,
) -> np.ndarray:
    """Return indices of the most similar chunks."""

    if embeddings is None or len(embeddings) == 0:
        return np.array([], dtype=int)

    query_embedding = model.encode(
        query,
        normalize_embeddings=True,
    )

    scores = query_embedding @ embeddings.T

    topk = min(topk, len(scores))

    return scores.argsort()[-topk:][::-1]


def retrieve(
    query: str,
    model: Any,
    chunks: list[str],
    embeddings: np.ndarray,
    topk: int = 5,
) -> list[str]:
    """Retrieve the top-k chunks most relevant to a query."""

    top_indices = similarities(
        query,
        model,
        embeddings,
        topk,
    )

    return [
        chunks[i]
        for i in top_indices
    ]


def build_knowledge_base(
    file_path: str | Path,
    model: Any,
    chunk_size: int = 1000,
    overlap: int = 200,
) -> dict[str, Any]:
    """Extract, chunk, and embed one PDF."""

    text, num_pages = extract_pdf_text(file_path)

    if not text.strip():
        raise ValueError(
            "No extractable text was found in this PDF. "
            "Scanned/image-only PDFs may require OCR."
        )

    chunks = chunk_text(
        text,
        chunk_size=chunk_size,
        overlap=overlap,
    )

    embeddings = embed_chunks(
        model,
        chunks,
    )

    return {
        "filename": Path(file_path).name,
        "pages": num_pages,
        "chunks": chunks,
        "embeddings": embeddings,
    }
