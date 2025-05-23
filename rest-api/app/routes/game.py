import json
import yaml
from typing import List, Optional
from fastapi import APIRouter
from ollama import GenerateResponse
from pydantic import BaseModel, Field
from constants import HIGH_LEVEL_TAG
from clients import ollama_client
from config import OLLAMA_MODEL
from .embed import post_embed, EmbedRequest

router = APIRouter(tags=[HIGH_LEVEL_TAG])


class Location(BaseModel):
    name: str = Field(..., description="Name of this in-game location")
    description: Optional[str] = Field(
        None, description="Optional description or lore blurb"
    )


class Game(BaseModel):
    name: str = Field(..., description="Title of the game")
    setting: str = Field(
        ..., description="High-level world setting (e.g. medieval fantasy)"
    )
    plot: str = Field(..., description="Short synopsis of the main storyline")
    locations: List[Location] = Field(
        default_factory=list, description="List of key locations in the game"
    )
    win_condition: str = Field(
        ..., description="What it takes for the player(s) to win"
    )
    extra_contexts: list[str] = Field(
        ..., description="Extra context that you want in your game world"
    )


class GenerateGameRequest(BaseModel):
    prompt: str = Field(
        ..., description="A free form prompt that will be used to generate the game"
    )


class GameResponse(Game):
    id: str
    collection_name: str


@router.post(
    "/game",
    summary="Creates a game and it's necessary files",
)
async def post_game(req: Game):

    text = yaml.safe_dump(
        data=req.model_dump(), sort_keys=False, allow_unicode=True, default_flow_style=False
    )

    embed_response = await post_embed(EmbedRequest(collection_name=req.name, text=text))

    return GameResponse(
        id=embed_response.ids[0], collection_name=embed_response.collection_name, **req.model_dump()
    )

@router.post(
    "/inject-npcs-into-game"
)
def inject_npcs_into_game():
    pass