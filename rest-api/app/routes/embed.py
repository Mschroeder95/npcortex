from typing import Optional
import uuid
from chromadb import Metadata
from fastapi import APIRouter, Form, HTTPException, status
from pydantic import BaseModel, Field
from config import OLLAMA_EMBED_MODEL
from clients import ollama_client, chroma_client
from constants import LOW_LEVEL_TAG

router = APIRouter(tags=[LOW_LEVEL_TAG])


class EmbedResponse(BaseModel):
    ids: list[str] = Form(..., description="IDs of the embeddings.")


class EmbedRequest(BaseModel):
    collection_name: str = Field(
        ..., description="The collection to embed context into"
    )
    text: str = Field(..., description="The text to embed")
    metadatas: Optional[list[dict[str, str]]] = Field( None,
        description="Matadata for future query filtering."
    )


@router.post(
    "/embed",
    summary="Embed text into the RAG system",
    description="Low level interface for embedding text into the RAG.",
)
def post_embed(req: EmbedRequest):
    try:
        resp = ollama_client.embed(model=OLLAMA_EMBED_MODEL, input=req.text)
        embeddings = resp["embeddings"]
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ollama embed failed: {e}"
        )

    try:
        coll = chroma_client.get_collection(name=req.collection_name)
    except Exception:
        chroma_client.create_collection(name=req.collection_name)
        coll = chroma_client.get_collection(name=req.collection_name)

    new_id = str(uuid.uuid4())

    if req.metadatas is not None and len(req.metadatas) == 0 :
        instert_metadatas = None
    else:
        instert_metadatas = req.metadatas
    try:
        coll.add(
            ids=[new_id],
            embeddings=embeddings,
            documents=[req.text],
            metadatas=instert_metadatas,
        )
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Chroma add failed: {e}"
        )

    return EmbedResponse(ids=[new_id])
