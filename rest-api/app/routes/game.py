from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from constants import HIGH_LEVEL_TAG, GAME_DATA
from clients import chroma_client
from .embed import post_embed_single, EmbedRequest
from clients.chromadb_helpers import get_chroma_document_by_id
from util import safe_string

router = APIRouter(tags=[HIGH_LEVEL_TAG])


class Game(BaseModel):
    """
    Represents the overall game world and its high-level story framing.
    """

    game_name: str = Field(..., description="Title of the game world")
    synopsis: str = Field(
        ..., description="A one-paragraph overview of the story’s setup and stakes"
    )
    win_condition: str = Field(
        ..., description="What players must accomplish in order to win"
    )
    extra_contexts: list[str] = Field(
        default_factory=list,
        description="Additional world-building details or flavor text",
    )
    all_npc_names: list[str] = Field(
        default_factory=list,
        description="List of all NPC names that exist in this game",
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
    text = req.model_dump_json()
    safe_name = safe_string(req.game_name)
    embed_response = await post_embed_single(
        EmbedRequest(
            id=safe_name,
            collection_name=safe_name,
            text=text,
            metadata={GAME_DATA: safe_name},
        )
    )

    return GameResponse(
        id=embed_response.id,
        collection_name=embed_response.collection_name,
        **req.model_dump()
    )


@router.get("/game", summary="Retrieve game data from the system")
async def get_game(
    game_name: str = Query(..., description="The name of the Game")
) -> Game:
    return Game(**get_chroma_document_by_id(game_name, game_name))


@router.get("/games", summary="Retrieve all games from the system")
async def get_games():
    games = []
    for coll in chroma_client.list_collections():
        document = get_chroma_document_by_id(coll.name, coll.name)
        games.append(document)

    return {"games": games}
