from typing import Literal, Optional
from ollama import GenerateResponse, Options
from pydantic import BaseModel, Field
from constants import HIGH_LEVEL_TAG
from fastapi import APIRouter, Depends
from clients import ollama_client
from config import OLLAMA_MODEL
import json
import yaml
from clients.chromadb_helpers import get_chroma_document_by_id
from .game import post_game, Game
from .npc import post_npc, NpcRequest, Npc

router = APIRouter(tags=[HIGH_LEVEL_TAG])

class GenerateRequest(BaseModel):
    prompt: str = Field(..., description="The prompt used to generate the object")
    option: Literal['Game', 'NPC'] = Field('Game', description="The name of the object to generate")
    randomness: Optional[str] = Field(0, description="Value between between 0 and 1. Higher values produce more random results")
    using_game: Optional[str] = Field(None, description="If provided will find the game by name and use it as context to make the new object")
@router.get(
    "/generate",
    summary="Generates objects by class name",
    description="Generates objects, but does not save them. This endpoint is so you can genrate some data to use in other endpoints that persist data.",
)
async def generate(req: GenerateRequest = Depends()):
    match req.option:
        case 'Game':
            model_class = Game
        case 'NPC':
            model_class = Npc

    if req.using_game is not None:
        game_data = get_chroma_document_by_id(req.using_game, req.using_game)
        game_prompt = f'Use this game as inspiration:\n{yaml.dump(game_data)}'
    else:
        game_prompt = ''
    format_prompt = model_format_prompt(model_class)
    full_prompt = f"""
    Using this description of the response format, all fields are required:
    {format_prompt}
    {game_prompt}
    Generate a new {req.option} with new names using the following prompt for inspiration:
    {req.prompt}
    """
    print(format_prompt)
    output: GenerateResponse = ollama_client.generate(
        model=OLLAMA_MODEL, prompt=full_prompt, format=model_class.model_json_schema(),options=Options(temperature=float(req.randomness))
    )
    return json.loads(output["response"])


class GenerateAndCreateRequest(BaseModel):
    prompt: str = Field(..., description='The prompt to use when generating game objects ')
@router.post(
    '/generate-and-create-all',
    summary='Generate and create all game objects',
    description='Generates game objects from the prompt and creates them in the RAG database'
)
async def generate_and_create_all(
        req: GenerateAndCreateRequest = Depends()
):
    game = await generate(GenerateRequest(prompt=req.prompt, option='Game'))
    game = Game(**game)
    await post_game(game)
    npcs = []
    for i in range(5):
        npc = await generate(GenerateRequest(prompt=f'(Make an npc based on this prompt: {req.prompt}) (existing npcs: {yaml.dump(npcs)})', option='NPC', using_game=game.game_name, randomness='1'))
        npc = Npc(**npc)
        print(npc)
        await post_npc(NpcRequest(npc=npc, game_name=game.game_name))
        npcs.append(npc)

    print(npcs)
    return {
        'game': game,
        'npcs': npcs
    }


def model_format_prompt(model_class):
    prompt = f"Fields and descriptions for response format: {model_class.__name__}"
    for field_name, field in model_class.model_fields.items():
        prompt += f"(field={field_name}, description={field.description})"