from fastapi import APIRouter, File, UploadFile, Form, HTTPException, status
from pydantic import BaseModel, Field
from clients import minio_client
from constants import LOW_LEVEL_TAG

router = APIRouter(prefix='/file', tags=[LOW_LEVEL_TAG])


@router.post(
    path='/',
    summary="Upload a file to the system",
    description="Low level interface for saving files",
)
async def save_file(
    bucket_name: str = Form(..., description="Name of the bucket"),
    path: str = Form(..., description="Object key (path) in the bucket"),
    file: UploadFile = File(..., description="The file to save"),
):
    create_bucket_if_does_not_exist(bucket_name)

    try:
        minio_client.put_object(
            bucket_name,
            f'{path}/{file.filename}',
            file.file,
            file.size,
            content_type=file.content_type,
        )
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload {file.filename} to `{bucket_name}/{path}/`: {e}",
        )

    return {"uploaded": True, "bucket": bucket_name, "path": path}

# @router.get()
# async def get_file(
#     bucket_name: str,
#     object_name: str
# ):
#     create_bucket_if_does_not_exist(bucket_name)
    
#     response = minio_client.get_object(bucket_name=bucket_name, object_name=object_name)
#     if response.status == status.HTTP_404_NOT_FOUND:
#         response.

def create_bucket_if_does_not_exist(bucket_name: str):
    try:
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not create/access bucket `{bucket_name}`: {e}",
        )