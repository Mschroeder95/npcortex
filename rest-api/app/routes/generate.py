from typing import Literal
from ollama import GenerateResponse
from pydantic import BaseModel, Field
from constants import LOW_LEVEL_TAG
from fastapi import APIRouter, Depends
from .game import Game
from .npc import Npc
from clients import ollama_client
from config import OLLAMA_MODEL
import json

router = APIRouter(tags=[LOW_LEVEL_TAG])

class GenerateRequest(BaseModel):
    prompt: str = Field(..., description="The prompt used to generate the object")
    option: Literal['Game', 'NPC'] = Field('Game', description="The name of the object to generate")
@router.get(
    "/generate",
    summary="Generates objects by class name",
    description="Generates objects, but does not save them. This endpoint is so you can genrate some data to use in other endpoints that persist data.",
)
def generate(req: GenerateRequest = Depends()):
    match req.option:
        case 'Game':
            model_class = Game
        case 'NPC':
            model_class = Npc

    format_prompt = model_format_prompt(model_class)
    full_prompt = f"""
    Using this description of the response format, all fields are required:
        {format_prompt}

    Generate a {req.option} using the following prompt for inspiration:
        {req.prompt}
    """
    print(format_prompt)
    output: GenerateResponse = ollama_client.generate(
        model=OLLAMA_MODEL, prompt=full_prompt, format=model_class.model_json_schema()
    )
    return json.loads(output["response"])


def model_format_prompt(model_class):
    prompt = f"Fields and descriptions for response format: {model_class.__name__}"
    for field_name, field in model_class.model_fields.items():
        prompt += f"(field={field_name}, description={field.description})"