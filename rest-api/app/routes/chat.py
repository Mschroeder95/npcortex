import json
from chromadb import QueryResult
from fastapi import APIRouter, HTTPException, status
from ollama import ChatResponse, GenerateResponse
from pydantic import BaseModel, Field
import yaml
from config import OLLAMA_EMBED_MODEL, OLLAMA_MODEL
from clients import ollama_client, chroma_client
from constants import HIGH_LEVEL_TAG, NPC_NAME
from clients.chromadb_helpers import get_chroma_document_by_id, update_chat_history, get_chat_history
from .npc import Npc
from .game import Game
from .file import save_file
from util.helper_functions import safe_string

router = APIRouter(tags=[HIGH_LEVEL_TAG])


class ChatRequest(BaseModel):
    game_name: str = Field(
        ..., description="The name of the game that the NPC belongs to"
    )
    npc_name: str = Field(..., description="The name of the npc to talk to")
    words: str = Field(..., description="The words to say to the NPC.")


class NpcResponse(BaseModel):
    npc_response: str
    npc_name: str


@router.post("/chat",
             summary="Chat with an NPC",
             description="Used to have a conversation with an NPC. Automatically includes various required contexts for the game.")
async def post_chat(req: ChatRequest):

    embedding = ollama_client.embed(model=OLLAMA_EMBED_MODEL, input=req.words)
    safe_game_name = safe_string(req.game_name)
    safe_npc_name = safe_string(req.npc_name)

    try:
        coll = chroma_client.get_collection(name=safe_game_name)
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
        where={NPC_NAME: {"$eq": req.npc_name}},
    )

    npc = Npc(**json.loads(query_result["documents"][0][0]))

    # TODO: Add metadata to game post and filter to it for base game context

    # TODO: Add general game/world knowledge

    # TODO: Add long term memory NPC specific

    # TODO: is converstation about metadata tag like an npc, loction, etc. -> go grab that context
    
    # TODO: Keep track of time since last time you spoke in respect to things that have happen in the game, not real world time that has passed

    game_data = Game(
        **get_chroma_document_by_id(id=req.game_name, collection_name=req.game_name)
    )

    chat_history = get_chat_history(collection_name=safe_game_name, npc_name=safe_npc_name)
    messages = [
        {
            "role": "system",
            "content": f"""
        Assume the role of {npc.npc_name}.
        {yaml.safe_dump(npc.model_dump())}

        Drive narrative for {game_data.game_name} without giving away too much information:
        {yaml.safe_dump(game_data.model_dump())}

        Respond only with the provided context.
""",
        },
        {"role": "user", "content": f"{req.words}"},
    ]

    full_chat = []
    full_chat.append(chat_history)
    full_chat.append(messages)
    print("model: ", OLLAMA_MODEL)
    output: ChatResponse = ollama_client.chat(
        model=OLLAMA_MODEL, messages=full_chat, format=NpcResponse.model_json_schema()
    )

    full_chat.append(output.message)
    
    await update_chat_history(safe_game_name, safe_npc_name, full_chat)

    print(output)
    npc_response = NpcResponse(**json.loads(output.message.content))

    return {npc_response: npc_response, chat_history: full_chat}
