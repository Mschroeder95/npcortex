import json
from typing import List, Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from constants import HIGH_LEVEL_TAG, GAME_DATA, GAME_NAME
from clients import ollama_client, chroma_client
from config import OLLAMA_MODEL
from .embed import post_embed_single, EmbedRequest
from clients.chromadb_helpers import make_chroma_safe_name, get_chroma_document_by_id

router = APIRouter(tags=[HIGH_LEVEL_TAG])


class Game(BaseModel):
    game_name: str = Field(..., description="Title of the game world")
    plot: str = Field(..., description="Short synopsis of the main storyline")
    win_condition: str = Field(
        ..., description="What it takes for the player(s) to win"
    )
    extra_contexts: list[str] = Field(
        ..., description="Extra context attached to game object"
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
    text = json.dumps(req.model_dump())
    safe_name = make_chroma_safe_name(req.game_name)
    embed_response = await post_embed_single(
        EmbedRequest(
            id=safe_name,
            collection_name=safe_name,
            text=text,
            metadata={GAME_DATA: safe_name, GAME_NAME: req.game_name},
        )
    )

    return GameResponse(
        id=embed_response.id,
        collection_name=embed_response.collection_name,
        **req.model_dump()
    )


@router.get("/games", summary="Retrieve all games from the system")
async def get_games():
    games = []
    for coll in chroma_client.list_collections():
        document = get_chroma_document_by_id(coll.name, coll.name)
        games.append(document)

    return {"games": games}


@router.get('/game',
            summary='Retrieve game data from the system')
async def get_game(game_name: str = Query(..., description="The name of the Game")):
    return get_chroma_document_by_id(game_name, game_name)



@router.post("/add-npc-to-game")
def add_npc_to_game():
    pass
