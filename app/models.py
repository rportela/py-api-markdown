from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class CollectionCreateRequest(BaseModel):
    name: str = Field(..., description="Unique collection name")


class DocumentAddRequest(BaseModel):
    ids: List[str]
    documents: List[str]
    metadatas: Optional[List[Dict[str, Any]]] = None


class QueryRequest(BaseModel):
    query_texts: List[str]
    top_k: int = 5
    where: Optional[Dict[str, Any]] = None
