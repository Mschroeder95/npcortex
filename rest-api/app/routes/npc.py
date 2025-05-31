from typing import Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from constants import HIGH_LEVEL_TAG, NPC_DATA, NPC_NAME
from .embed import post_embed_single, EmbedRequest, EmbedResponse
from clients.chromadb_helpers import get_chroma_document_by_id
from util import safe_string
from .game import get_game, post_game

router = APIRouter(tags=[HIGH_LEVEL_TAG])


class Npc(BaseModel):
    """
    Represents a non-player character with motivations, backstory, and what they know.
    """

    npc_name: str = Field(..., description="The character’s name")
    bio: str = Field(..., description="Brief backstory or description of who they are")
    personality_traits: list[str] = Field(
        default_factory=list,
        description="A list of evocative traits (e.g. ‘cunning’, ‘loyal’, ‘impulsive’)",
    )
    main_goal: Optional[str] = Field(
        None,
        description="Primary objective that drives this NPC’s role in the main story. Can be blank if they are not a main NPC",
    )
    side_goals: list[str] = Field(
        default_factory=list,
        description="Secondary personal objectives that add depth and optional side-quests",
    )
    knowledge: list[str] = Field(
        default_factory=list,
        description="Key facts or lore this NPC holds and may reveal",
    )
    extra: dict[str, str] = Field(
        default_factory=dict,
        description="Free-form metadata (e.g. faction, title, possessions)",
    )


class NpcResponse(Npc):
    id: str
    collection_name: str


class NpcRequest(BaseModel):
    npc: Npc
    game_name: str = Field(..., description="The Game to add the NPC to")


@router.post("/npc")
async def post_npc(req: NpcRequest):
    game_name = safe_string(req.game_name)
    # TODO: Fix npc name clashing. Maybe add ability to pass uuid for the id to embed and use same uuid for npc_data_for metadata
    embed_response: EmbedResponse = await post_embed_single(
        EmbedRequest(
            id=req.npc.npc_name,
            collection_name=game_name,
            text=req.npc.model_dump_json(),
            metadata={NPC_DATA: True, NPC_NAME: req.npc.npc_name},
        )
    )

    game = await get_game(game_name)
    print(game)
    if not game.all_npc_names.count(req.npc.npc_name):
        game.all_npc_names.append(req.npc.npc_name)
        await post_game(game)

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


@router.get("/npcs")
async def get_npcs(
    game_name: str = Query(
        ..., description="The name of the game that the NPC belongs to"
    ),
):
    game_name = safe_string(game_name)
    game = await get_game(game_name)
    npcs = []
    for npc_name in game.all_npc_names:
        npcs.append(get_chroma_document_by_id(npc_name, game_name))

    return {"npcs": npcs}
