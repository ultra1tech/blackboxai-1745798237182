import os
import uuid
from typing import List
from fastapi import UploadFile, HTTPException, status
from PIL import Image
import aiofiles
from app.core.config import settings

UPLOAD_DIR = settings.UPLOAD_DIR
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
MAX_FILE_SIZE = settings.MAX_FILE_SIZE  # 5MB

async def validate_image(file: UploadFile) -> None:
    """Validate image file."""
    # Check file size
    file.file.seek(0, 2)  # Seek to end
    size = file.file.tell()
    file.file.seek(0)  # Reset position
    
    if size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size too large. Maximum size is {MAX_FILE_SIZE/1024/1024}MB"
        )
    
    # Check file extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Verify it's a valid image
    try:
        image = Image.open(file.file)
        image.verify()
        file.file.seek(0)  # Reset position after verification
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image file"
        )

async def save_upload(file: UploadFile, directory: str) -> str:
    """
    Save uploaded file and return the file path.
    
    Args:
        file: The uploaded file
        directory: Subdirectory within UPLOAD_DIR (e.g., 'products', 'stores')
    
    Returns:
        str: URL path to the saved file
    """
    await validate_image(file)
    
    # Create upload directory if it doesn't exist
    upload_path = os.path.join(UPLOAD_DIR, directory)
    os.makedirs(upload_path, exist_ok=True)
    
    # Generate unique filename
    ext = os.path.splitext(file.filename)[1].lower()
    filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(upload_path, filename)
    
    # Save file
    try:
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save file: {str(e)}"
        )
    
    # Return URL path
    return f"/static/uploads/{directory}/{filename}"

async def delete_file(file_path: str) -> None:
    """Delete file from storage."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not delete file: {str(e)}"
        )

async def save_multiple_uploads(files: List[UploadFile], directory: str) -> List[str]:
    """Save multiple uploaded files and return their paths."""
    paths = []
    for file in files:
        path = await save_upload(file, directory)
        paths.append(path)
    return paths

def get_file_url(filename: str, directory: str) -> str:
    """Get full URL for a file."""
    return f"/static/uploads/{directory}/{filename}"

def get_file_path(filename: str, directory: str) -> str:
    """Get full file system path for a file."""
    return os.path.join(UPLOAD_DIR, directory, filename)

async def process_image(
    file: UploadFile,
    directory: str,
    max_size: tuple = (800, 800),
    quality: int = 85,
    create_thumbnail: bool = False,
    thumbnail_size: tuple = (200, 200)
) -> dict:
    """
    Process image upload with resizing and optional thumbnail creation.
    
    Args:
        file: The uploaded file
        directory: Upload subdirectory
        max_size: Maximum dimensions for the main image
        quality: JPEG quality (1-100)
        create_thumbnail: Whether to create a thumbnail
        thumbnail_size: Thumbnail dimensions
    
    Returns:
        dict: Paths to the processed images
    """
    await validate_image(file)
    
    # Create upload directory
    upload_path = os.path.join(UPLOAD_DIR, directory)
    os.makedirs(upload_path, exist_ok=True)
    
    # Generate unique filename
    ext = os.path.splitext(file.filename)[1].lower()
    filename = f"{uuid.uuid4()}"
    
    # Process main image
    image = Image.open(file.file)
    
    # Convert to RGB if necessary
    if image.mode in ('RGBA', 'P'):
        image = image.convert('RGB')
    
    # Resize main image
    image.thumbnail(max_size, Image.LANCZOS)
    
    # Save main image
    main_path = os.path.join(upload_path, f"{filename}{ext}")
    image.save(main_path, quality=quality, optimize=True)
    
    result = {
        "main_image": f"/static/uploads/{directory}/{filename}{ext}"
    }
    
    # Create thumbnail if requested
    if create_thumbnail:
        thumb = image.copy()
        thumb.thumbnail(thumbnail_size, Image.LANCZOS)
        thumb_path = os.path.join(upload_path, f"{filename}_thumb{ext}")
        thumb.save(thumb_path, quality=quality, optimize=True)
        result["thumbnail"] = f"/static/uploads/{directory}/{filename}_thumb{ext}"
    
    return result
