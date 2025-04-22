from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import router as chroma_router

app = FastAPI(
    title="ChromaDB REST API",
    version="0.1.0",
    description="RESTful service exposing Chroma collections and documents using OpenAI embeddings",
)

# Optional: accept everything during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chroma_router)
