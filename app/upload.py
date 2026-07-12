from fastapi import APIRouter, UploadFile, File
import os
import shutil
import hashlib

from app.database import SessionLocal, Image
from app.embeddings import (
    image_embedding,
    categorize_image
)
from app.search import (
    add_embedding,
    check_near_duplicate
)

router = APIRouter()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def calculate_hash(file_path):
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as f:
        while True:
            data = f.read(4096)

            if not data:
                break

            sha256.update(data)

    return sha256.hexdigest()


@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    db = SessionLocal()

    # ------------------------
    # Exact Duplicate Detection
    # ------------------------

    filehash = calculate_hash(filepath)

    duplicate = db.query(Image).filter(
        Image.filehash == filehash
    ).first()

    if duplicate:

        db.close()

        return {
            "status": "duplicate",
            "message": "Exact duplicate detected",
            "existing_file": duplicate.filename
        }

    # ------------------------
    # CLIP Embedding
    # ------------------------

    embedding = image_embedding(filepath)

    # ------------------------
    # Near Duplicate Detection
    # ------------------------

    near_duplicate = check_near_duplicate(
        embedding,
        threshold=0.85
    )

    if near_duplicate:

        db.close()

        return {
            "status": "near_duplicate",
            "message": "Similar image detected",
            "similar_to": near_duplicate["path"],
            "similarity": near_duplicate["score"]
        }

    # ------------------------
    # Store Embedding
    # ------------------------

    add_embedding(filepath, embedding)

    # ------------------------
    # AI Categorization
    # ------------------------

    category = categorize_image(filepath)

    image = Image(
        filename=file.filename,
        filepath=filepath,
        filehash=filehash,
        category=category
    )

    db.add(image)
    db.commit()
    db.refresh(image)

    db.close()

    return {
        "status": "success",
        "message": "Image uploaded successfully",
        "filename": file.filename,
        "category": category
    }