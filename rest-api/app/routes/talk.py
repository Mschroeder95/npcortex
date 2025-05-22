from chromadb import QueryResult
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from config import OLLAMA_MODEL, OLLAMA_EMBED_MODEL
from clients import ollama_client, chroma_client
from constants import HIGH_LEVEL_TAG
router = APIRouter(tags=[HIGH_LEVEL_TAG])

class ResponseFormat(BaseModel):
    player_name: str
    ollama_response: str
class TalkRequest(BaseModel):
    collections: list[str]
    words: str
class TalkResponse(BaseModel):
    words: str
@router.post("/talk", response_model=TalkResponse)
def post_talk(req: TalkRequest):
    
    embedding = ollama_client.embed(
        model=OLLAMA_EMBED_MODEL,
        input=req.words
    )
    
    results: list[QueryResult] = []
    for coll_name in req.collections:
        try:
            coll = chroma_client.get_collection(name=coll_name)
        except ValueError as e:
            return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chroma add failed: {e}"
        )

        query_result = coll.query(
            query_embeddings=embedding['embeddings'],
            n_results=1
        )
        results.append(query_result)

    data = results[0]['documents'][0][0]
    output = ollama_client.generate(
    model=OLLAMA_MODEL,
    prompt=f"Using this data: {data}. Respond to this prompt: {req.words}",
    format= ResponseFormat.model_json_schema(),
    )

    return TalkResponse(
        words=str(output['response'])
    )
