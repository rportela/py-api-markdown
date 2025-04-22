from __future__ import annotations

from typing import Any, Dict, List

from app.repositories.ChromaRepository import ChromaRepository


class ChromaService:
    """Business‑logic layer that orchestrates repository calls."""

    def __init__(self, repo: ChromaRepository | None = None):
        self.repo = repo or ChromaRepository()

    # —— Collections ——
    def list_collections(self) -> List[str]:
        return self.repo.list_collections()

    def create_collection(self, name: str) -> Dict[str, str]:
        self.repo.create_collection(name)
        return {"name": name}

    def delete_collection(self, name: str) -> None:
        self.repo.delete_collection(name)

    # —— Documents ——
    def add_documents(
        self,
        collection_name: str,
        ids: List[str],
        documents: List[str],
        metadatas: List[Dict[str, Any]] | None = None,
    ) -> Dict[str, Any]:
        self.repo.add_documents(collection_name, ids, documents, metadatas)
        return {"inserted": len(ids)}

    def get_document(self, collection_name: str, doc_id: str) -> Dict[str, Any]:
        res = self.repo.get_document(collection_name, doc_id)
        return res.items()  # type: ignore

    def delete_document(self, collection_name: str, doc_id: str) -> None:
        self.repo.delete_document(collection_name, doc_id)

    # —— Query ——
    def query(
        self,
        collection_name: str,
        query_texts: List[str],
        top_k: int = 5,
        where: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        res = self.repo.query(
            collection_name, query_texts, n_results=top_k, where=where
        )
        return res.items()  # type: ignore
