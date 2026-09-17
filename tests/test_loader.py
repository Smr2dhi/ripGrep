from fastapi import FastAPI, UploadFile, File
import os
import shutil

from backend.ingestion.loader import load_document


app = FastAPI()


UPLOAD_DIR = "documents"

os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/test-loader")
async def test_loader(file: UploadFile = File(...)):

    file_path = os.path.join(
        UPLOAD_DIR,
        file.filename
    )

    with open(file_path, "wb") as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    result = load_document(file_path)

    return {
        "document_name": result["document_name"],
        "file_type": result["file_type"],
        "pages": result["pages"],
        "text": result["text"]
    }