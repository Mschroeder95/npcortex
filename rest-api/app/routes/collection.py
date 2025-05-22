from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from clients import chroma_client
from constants import LOW_LEVEL_TAG

router = APIRouter()
router = APIRouter(tags=[LOW_LEVEL_TAG])


class CollectionsResponse(BaseModel):
    collections: list[str] = Field(..., description="List of found collections")


@router.get(
    "/collection",
    response_model=CollectionsResponse,
    summary="Get all collections",
    description="Retrieves a list of all collections.",
)
def get_collection():
    return CollectionsResponse(collections=chroma_client.list_collections())


@router.delete(
    "/collection",
    summary="Delete A collection",
    description="Low level interface for deleting collections. Used to manage the (RAG) Retrieval-Augmented Generation system.",
)
def delete_collection(
    name: str = Query(description="Name of the collection to delete"),
):
    try:
        chroma_client.delete_collection(name=name)
    except Exception as e:
        # You can catch more specific exceptions if you like
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chroma delete_collection failed: {e}",
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"deleted": True, "collection": name}
    )
