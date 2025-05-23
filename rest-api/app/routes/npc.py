import json
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel, Field
import os

import yaml
from constants import HIGH_LEVEL_TAG
from .embed import post_embed, EmbedRequest, EmbedResponse
from .file import store_file
router = APIRouter(tags=[HIGH_LEVEL_TAG])

class NpcRelationship(BaseModel):
    others_name: str = Field(..., description="Name of another NPC or player")
    disposition: str = Field(..., description="e.g. neutral, friend, rival")


class Npc(BaseModel):
    name: str = Field(..., description="NPC’s name")
    bio: str = Field(..., description="Description of the NPC")
    personality_traits: list[str] = Field(..., description="A list of personality traits that belong to the character")
    relationships: list[NpcRelationship] = Field(
        default_factory=list, description="How this NPC feels about others"
    )
    extra: dict[str, str] = Field(
        default_factory=dict, description="Free-form key/value data"
    )

class NpcResponse(Npc):
    id: str
    collection_name: str
@router.post("/npc")
async def create_npc(
    npc_string: str = Form(..., description="JSON string representing the NPC object"),
    game_name: str = Form(..., description="The Game to add the NPC to"),
    voiceFile: UploadFile = File(..., description="A voice for the npc"),
):
    try:
        npc_data = json.loads(npc_string)
        npc = Npc.model_validate(npc_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid NPC data: {str(e)}")
    text = yaml.safe_dump(
        data=npc.model_dump(), sort_keys=False, allow_unicode=True, default_flow_style=False
    )

    # TODO: Fix npc name clashing. Maybe add ability to pass uuid for the id to embed and use same uuid for npc_data_for metadata
    embed_response : EmbedResponse = await post_embed(EmbedRequest(collection_name=game_name, text=text, metadatas=[{"npc_data_for": npc.name}]))

    await store_file(embed_response.collection_name, f"/npc/{npc.name}/", voiceFile)

    return NpcResponse(
        id=embed_response.ids[0], collection_name=embed_response.collection_name, **npc.model_dump()
    )
