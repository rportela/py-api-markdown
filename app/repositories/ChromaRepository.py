from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.api.models.Collection import Collection
from chromadb.api.types import Documents, IDs, GetResult, QueryResult
from chromadb.utils.embedding_functions.openai_embedding_function import (
    OpenAIEmbeddingFunction,
)

EMBEDDING_MODEL = "text-embedding-3-small"


class ChromaRepository:
    """Low‑level wrapper around *chromadb.PersistentClient* operating in
    persistent mode and hiding embedding‑function plumbing.
    """

    def __init__(self, persist_directory: str = "./chroma_db") -> None:
        self.client = chromadb.PersistentClient(path=persist_directory)
        self._embedding_fns: dict[str, Any] = {}

    # —— Embeddings helper ——
    def _embedding_fn(
        self, model_name: str = EMBEDDING_MODEL
    ) -> chromadb.EmbeddingFunction:
        if model_name not in self._embedding_fns:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")
            self._embedding_fns[model_name] = OpenAIEmbeddingFunction(
                api_key=api_key, model_name=model_name
            )
        return self._embedding_fns[model_name]

    # —— Collection operations ——
    def list_collections(self) -> List[str]:
        return self.client.list_collections()  # type: ignore

    def create_collection(self, name: str) -> Collection:
        return self.client.create_collection(
            name=name, embedding_function=self._embedding_fn(EMBEDDING_MODEL)
        )

    def get_collection(self, name: str) -> Collection:
        return self.client.get_collection(
            name=name, embedding_function=self._embedding_fn(EMBEDDING_MODEL)
        )

    def delete_collection(self, name: str) -> None:
        self.client.delete_collection(name)

    # —— Document operations ——
    def add_documents(
        self,
        collection_name: str,
        ids: IDs,
        texts: Documents,
        metadatas: List[Dict[str, Any]] | None = None,
    ) -> None:
        mdata = [chromadb.Metadata(**d) for d in metadatas] if metadatas else None
        col = self.get_collection(collection_name)
        col.add(ids=ids, documents=texts, metadatas=mdata)

    def get_document(
        self,
        collection_name: str,
        doc_id: str,
    ) -> GetResult:
        col = self.get_collection(collection_name)
        return col.get(ids=[doc_id])

    def delete_document(self, collection_name: str, doc_id: str) -> None:
        col = self.get_collection(collection_name)
        col.delete(ids=[doc_id])

    def query(
        self,
        collection_name: str,
        query_texts: Documents,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
    ) -> QueryResult:
        col = self.get_collection(collection_name)
        return col.query(query_texts=query_texts, n_results=n_results, where=where)
