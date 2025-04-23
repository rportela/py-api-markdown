from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.services.ChromaService import (
    ChromaService,
    CollectionCreateRequest,
    DocumentAddRequest,
    QueryRequest,
)

router = APIRouter()
service = ChromaService()

# —— Collection endpoints ——


@router.get("/v1/collections", response_model=list[str])
async def list_collections():
    """List all collection names."""
    return service.list_collections()


@router.post("/v1/collections", status_code=status.HTTP_201_CREATED)
async def create_collection(body: CollectionCreateRequest):
    return service.create_collection(body.name)


@router.delete("/v1/collections/{name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_collection(name: str):
    service.delete_collection(name)


# —— Document endpoints ——


@router.post("/v1/collections/{name}/documents", status_code=status.HTTP_201_CREATED)
async def add_documents(name: str, body: DocumentAddRequest):
    return service.add_documents(name, body.ids, body.documents, body.metadatas)


@router.get("/v1/collections/{name}/documents/{doc_id}")
async def get_document(name: str, doc_id: str):
    result = service.get_document(name, doc_id)
    if not result.get("ids"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )
    return result


@router.delete(
    "/v1/collections/{name}/documents/{doc_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_document(name: str, doc_id: str):
    service.delete_document(name, doc_id)


# —— Query endpoint ——


@router.post("/v1/collections/{name}/query")
async def query(name: str, body: QueryRequest):
    return service.query(name, body.query_texts, body.top_k, body.where)
