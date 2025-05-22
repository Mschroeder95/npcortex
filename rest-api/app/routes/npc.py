import json
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel
from config import STATIC_DIR
import os
from routes import embed
from constants import HIGH_LEVEL_TAG

router = APIRouter(tags=[HIGH_LEVEL_TAG])

class Npc(BaseModel):
    name: str
    bio: str

@router.post("/npc")
async def create_npc(
    collection_name: str = Form(..., description="The name of the collection to save the NPC"),
    name: str = Form(..., description="NPC’s name"),
    bio: str = Form(..., description="Short bio for the NPC"),
    voiceFile: UploadFile= File(..., description="WAV file for the NPC’s voice"),
):
    # create NPC directory
    os.makedirs(f'{STATIC_DIR}/{name}', exist_ok=True)
    os.makedirs(f'{STATIC_DIR}/{name}/voices', exist_ok=True)

    # save wav
    wav_path = os.path.join(f'{STATIC_DIR}/{name}/voices/', voiceFile.filename)
    try:
        contents = await voiceFile.read()
        with open(wav_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to save voice file: {e}")
    
    npc = Npc(name=name, bio=bio)
    with open(f'{STATIC_DIR}/{name}/{name}.json', "w") as f:
        json.dump(npc.model_dump_json(), f, indent=4)

    # embed name+bio into the "npc-collection"
    full_text = f"{name}: {bio}"
    embed_res: embed.EmbedResponse = await embed.post_embed(collection_name, full_text)

    return {
        "name":        name,
        "bio":         bio,
        "voice_file":  wav_path,
        "embed_ids":   embed_res.ids,
    }