import json
from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile, status
from pydantic import BaseModel, Field

from constants import HIGH_LEVEL_TAG, NPC_DATA, NPC_NAME
from .embed import post_embed_single, EmbedRequest, EmbedResponse
from clients.chromadb_helpers import get_chroma_document_by_id

router = APIRouter(tags=[HIGH_LEVEL_TAG])


class Npc(BaseModel):
    npc_name: str = Field(..., description="NPC’s name")
    bio: str = Field(..., description="Description of the NPC")
    personality_traits: list[str] = Field(
        ..., description="A list of personality traits that belong to the character"
    )
    extra: dict[str, str] = Field(
        default_factory=dict, description="Free-form key/value data"
    )


class NpcResponse(Npc):
    id: str
    collection_name: str

class NpcRequest(BaseModel):
    npc: Npc
    game_name: str = Field(..., description="The Game to add the NPC to")
@router.post("/npc")
async def post_npc(
    req: NpcRequest
):
    # TODO: Fix npc name clashing. Maybe add ability to pass uuid for the id to embed and use same uuid for npc_data_for metadata
    embed_response: EmbedResponse = await post_embed_single(
        EmbedRequest(
            id=req.npc.npc_name,
            collection_name=req.game_name,
            text=req.npc.model_dump_json(),
            metadata={NPC_DATA: True, NPC_NAME: req.npc.npc_name},
        )
    )

    return NpcResponse(
        id=embed_response.id,
        collection_name=embed_response.collection_name,
        **req.npc.model_dump(),
    )


@router.get("/npc")
async def get_npc(
    game_name: str = Query(
        ..., description="The name of the game that the NPC belongs to"
    ),
    npc_name: str = Query(..., description="The name of the NPC")
):
    return get_chroma_document_by_id(npc_name, game_name)