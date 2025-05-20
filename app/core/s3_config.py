import uuid
from typing import Optional

import boto3
from fastapi import UploadFile

# Настройки AWS S3
AWS_ACCESS_KEY_ID = "secret"
AWS_SECRET_ACCESS_KEY = "secret"
S3_ENDPOINT = "storage.yandexcloud.net"
S3_BUCKET_NAME = "secret"
S3_REGION = "secret"

s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    endpoint_url=f"https://{S3_ENDPOINT}",
    region_name=S3_REGION
)

async def upload_profile_photo(file: UploadFile) -> Optional[str]:
    """
    Upload a profile photo to Yandex Object Storage and return the URL
    """
    if not file:
        return None

    try:
        file_extension = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"

        file_content = await file.read()

        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=unique_filename,
            Body=file_content,
            ContentType=file.content_type
        )

        file_url = f"https://{S3_ENDPOINT}/{S3_BUCKET_NAME}/{unique_filename}"
        return file_url
    except Exception as e:
        print(f"Error uploading file: {e}")
        return None 