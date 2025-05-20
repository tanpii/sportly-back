import os
import uuid
from fastapi import UploadFile
from datetime import datetime
from app.core.s3_config import upload_profile_photo
from botocore.exceptions import ClientError

async def upload_profile_photo(file: UploadFile) -> str:
    """Загрузка фотографии профиля в S3"""
    try:
        # Генерируем уникальное имя файла
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"profile_photos/{uuid.uuid4()}{file_extension}"
        
        # Читаем содержимое файла
        content = await file.read()
        
        # Загружаем файл в S3
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=unique_filename,
            Body=content,
            ContentType=file.content_type
        )
        
        # Генерируем URL для доступа к файлу
        url = f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{unique_filename}"
        return url
        
    except ClientError as e:
        print(f"Ошибка при загрузке файла в S3: {str(e)}")
        return None
    except Exception as e:
        print(f"Неожиданная ошибка: {str(e)}")
        return None

__all__ = ['upload_profile_photo'] 