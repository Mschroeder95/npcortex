from fastapi import APIRouter, File, UploadFile, Form, HTTPException, status
from pydantic import BaseModel, Field
from clients import minio_client
from constants import LOW_LEVEL_TAG

router = APIRouter(tags=[LOW_LEVEL_TAG])


@router.post(
    "/file",
    summary="Upload a file to the system",
    description="Low level interface for saving files",
)
async def store_file(
    bucket_name: str = Form(..., description="Name of the bucket"),
    path: str = Form(..., description="Object key (path) in the bucket"),
    file: UploadFile = File(..., description="The file to save"),
):
    try:
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not create/access bucket `{bucket_name}`: {e}",
        )
    
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
