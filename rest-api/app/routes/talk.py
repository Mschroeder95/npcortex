import json
from chromadb import QueryResult
from fastapi import APIRouter, HTTPException, status
from ollama import GenerateResponse
from pydantic import BaseModel, Field
from config import OLLAMA_MODEL, OLLAMA_EMBED_MODEL
from clients import ollama_client, chroma_client
from constants import HIGH_LEVEL_TAG
from .embed import make_chroma_safe_name

router = APIRouter(tags=[HIGH_LEVEL_TAG])


class TalkRequest(BaseModel):
    game_name: str
    talk_to_npc: str
    words: str


@router.post("/talk")
def post_talk(req: TalkRequest):

    embedding = ollama_client.embed(model=OLLAMA_EMBED_MODEL, input=req.words)

    try:
        coll = chroma_client.get_collection(name=make_chroma_safe_name(req.game_name))
    except ValueError as e:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chroma add failed: {e}",
        )

    query_result = coll.query(query_embeddings=embedding["embeddings"], n_results=1)
    general_data = query_result["documents"][0][0]

    query_result = coll.query(
        query_embeddings=embedding["embeddings"],
        n_results=1,
        where={"npc_data_for": {"$eq": req.talk_to_npc}},
    )

    npc_object = query_result["documents"][0][0]

    # TODO: Add metadata to game post and filter to it for base game context

    # TODO: Add general game/world knowledge

    # TODO: Add long term memory NPC specific

    # TODO: add short term/chat memory for NPC

    print(general_data)
    print(npc_object)

    messages = [
        {"role": "system", "content": f"You are {npc_object}"},
        {"role": "user", "content": f"{req.words}"}
    ]

    print(messages)
    ollama_client.chat()
    output: GenerateResponse = ollama_client.chat(
        model=OLLAMA_MODEL,
        messages=messages,
    )

    return output["response"]
