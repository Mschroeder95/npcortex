from typing import Optional
import uuid
from chromadb import Metadata
from fastapi import APIRouter, Form, HTTPException, status
from pydantic import BaseModel, Field
from config import OLLAMA_EMBED_MODEL
from clients import ollama_client, chroma_client
from constants import LOW_LEVEL_TAG
from clients.chromadb_helpers import make_chroma_safe_name

router = APIRouter(tags=[LOW_LEVEL_TAG])


class EmbedResponse(BaseModel):
    collection_name: str
    id: str


class EmbedRequest(BaseModel):
    id: str = Field(None, description="Optional ID for the new embedding")
    collection_name: str = Field(
        ..., description="The collection to embed context into"
    )
    text: str = Field(..., description="The text to embed")
    metadata: Optional[Metadata] = Field(
        None, description="Matadata for future query filtering."
    )


@router.post(
    "/embed-single",
    summary="Embed text into the RAG system",
    description="Low level interface for embedding text into the RAG.",
)
async def post_embed_single(req: EmbedRequest):
    collection_name = make_chroma_safe_name(req.collection_name)
    try:
        resp = ollama_client.embed(model=OLLAMA_EMBED_MODEL, input=req.text)
        embeddings = resp["embeddings"]
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ollama embed failed: {e}"
        )

    try:
        coll = chroma_client.get_collection(name=collection_name)
    except Exception:
        chroma_client.create_collection(name=collection_name)
        coll = chroma_client.get_collection(name=collection_name)

    if req.metadata is not None:
        instert_metadatas = None
    else:
        instert_metadatas = [req.metadatas]

    if req.id is not None:
        insert_ids = [make_chroma_safe_name(req.id)]
    else:
        insert_ids = [str(uuid.uuid4())]

    try:
        coll.add(
            ids=insert_ids,
            embeddings=embeddings,
            documents=[req.text],
            metadatas=instert_metadatas,
        )
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Chroma add failed: {e}"
        )

    return EmbedResponse(id=insert_ids[0], collection_name=collection_name)


