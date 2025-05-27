from typing import Any

from ollama import Message
from . import chroma_client
import json
from util.helper_functions import safe_string
from routes.embed import post_embed_single, EmbedRequest
from constants import CHAT_HISTORY, NPC_NAME
import json


def get_chroma_document_by_id(id: str, collection_name: str) -> Any:
    coll = chroma_client.get_collection(name=safe_string(collection_name))
    game_data = coll.get(ids=[safe_string(id)])
    return json.loads(game_data["documents"][0])


async def update_chat_history(collection_name: str, npc_name: str, chat_history: list[Message]):
    await post_embed_single(
        EmbedRequest(
            id=f"{safe_string(npc_name)}-chat",
            collection_name=collection_name,
            text=json.dumps({'chat_history', chat_history}),
            metadata={CHAT_HISTORY: True, NPC_NAME: safe_string(npc_name)},
        )
    )
    return


def get_chat_history(collection_name: str, npc_name: str) -> list[Message]:
    coll = chroma_client.get_collection(name=safe_string(collection_name))
    response = coll.get(ids=[f"{safe_string(npc_name)}-chat"])
    chat_history = json.loads(response["documents"][0])
    return chat_history['chat_history']
