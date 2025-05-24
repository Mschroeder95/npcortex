from typing import Any
from . import chroma_client
import json
import re

def get_chroma_document_by_id(id: str, collection_name: str) -> Any:
    coll = chroma_client.get_collection(name=make_chroma_safe_name(collection_name))
    game_data = coll.get(ids=[make_chroma_safe_name(collection_name)])
    return json.loads(game_data["documents"][0])

def make_chroma_safe_name(raw_name: str, max_length: int = 64) -> str:
    name = raw_name.lower()

    name = name.replace("_", "-")

    name = re.sub(r"[^a-z0-9_-]", "-", name)

    name = re.sub(r"_+", "-", name).strip("-")

    return name[:max_length]
