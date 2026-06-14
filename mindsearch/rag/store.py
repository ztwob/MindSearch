"""Lightweight retrieval helpers for MindSearch.

This module intentionally avoids heavyweight vector-store dependencies so the
project can run out of the box. It provides a small in-memory lexical retriever
that can later be swapped for FAISS, Milvus, pgvector, or another backend.
"""

import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Dict, Iterable, List


_TOKEN_RE = re.compile(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]", re.UNICODE)


def tokenize(text: str) -> List[str]:
    """Tokenize mixed English/Chinese text into lowercase lexical units.

    English words are kept as whole terms, while CJK characters are split into
    individual terms so Chinese queries can match document snippets without
    requiring a dedicated tokenizer such as jieba.
    """
    return [token.lower() for token in _TOKEN_RE.findall(text or "")]


@dataclass(frozen=True)
class Document:
    """A document chunk stored in the RAG index."""

    id: str
    text: str
    metadata: Dict[str, str]


@dataclass(frozen=True)
class SearchResult:
    """A scored retrieval result."""

    id: str
    text: str
    score: float
    metadata: Dict[str, str]


class InMemoryRAGStore:
    """Simple BM25-like in-memory retrieval store.

    The store is process-local and is best for local development, demos, and
    tests. Production deployments should implement the same add/search contract
    using a persistent vector database.
    """

    def __init__(self) -> None:
        self._documents: Dict[str, Document] = {}
        self._term_freqs: Dict[str, Counter] = {}
        self._doc_freqs: Counter = Counter()
        self._avg_doc_len = 0.0

    def add_documents(self, documents: Iterable[Document]) -> int:
        """Add or replace documents and rebuild retrieval statistics."""
        count = 0
        for document in documents:
            if not document.id:
                raise ValueError("document id must not be empty")
            if not document.text:
                raise ValueError(f"document {document.id!r} text must not be empty")
            self._documents[document.id] = document
            count += 1
        self._rebuild()
        return count

    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """Return the highest-scoring documents for a query."""
        if top_k <= 0:
            return []
        query_terms = tokenize(query)
        if not query_terms:
            return []

        scores = defaultdict(float)
        total_docs = max(len(self._documents), 1)
        for term in query_terms:
            doc_freq = self._doc_freqs.get(term, 0)
            if doc_freq == 0:
                continue
            idf = math.log(1 + (total_docs - doc_freq + 0.5) / (doc_freq + 0.5))
            for doc_id, term_freq in self._term_freqs.items():
                freq = term_freq.get(term, 0)
                if not freq:
                    continue
                doc_len = sum(term_freq.values()) or 1
                length_norm = 0.75 + 0.25 * (doc_len / (self._avg_doc_len or 1))
                scores[doc_id] += idf * (freq / length_norm)

        ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)[:top_k]
        return [
            SearchResult(
                id=doc_id,
                text=self._documents[doc_id].text,
                score=round(score, 6),
                metadata=self._documents[doc_id].metadata,
            )
            for doc_id, score in ranked
        ]

    def clear(self) -> None:
        """Remove all indexed documents."""
        self._documents.clear()
        self._term_freqs.clear()
        self._doc_freqs.clear()
        self._avg_doc_len = 0.0

    def _rebuild(self) -> None:
        self._term_freqs.clear()
        self._doc_freqs.clear()
        total_len = 0
        for doc_id, document in self._documents.items():
            term_freq = Counter(tokenize(document.text))
            self._term_freqs[doc_id] = term_freq
            self._doc_freqs.update(term_freq.keys())
            total_len += sum(term_freq.values())
        self._avg_doc_len = total_len / len(self._documents) if self._documents else 0.0


rag_store = InMemoryRAGStore()
