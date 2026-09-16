import os
import shutil

from fastapi import FastAPI, UploadFile, File, HTTPException

from app.config import DOCUMENTS_DIR
from app.models import AskRequest, AskResponse
from app.rag_pipeline import RagPipeline
from ingestion.loader import load_document
from utils.logging import get_logger


logger = get_logger(__name__)


app = FastAPI(
    title="GrepRAG - AI Knowledge Assistant",
    version="1.0"
)


ALLOWED_EXTENSIONS = {
    ".txt",
    ".md",
    ".pdf",
    ".docx"
}


rag = RagPipeline()


@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...)
):

    logger.info(
        "Document upload started: %s",
        file.filename
    )

    if not file.filename:

        logger.warning(
            "Upload rejected: filename missing"
        )

        raise HTTPException(
            status_code=400,
            detail="Filename is required."
        )

    extension = os.path.splitext(
        file.filename
    )[1].lower()

    if extension not in ALLOWED_EXTENSIONS:

        logger.warning(
            "Upload rejected: unsupported file type: %s",
            extension
        )

        raise HTTPException(
            status_code=400,
            detail="Only .txt, .md, .pdf and .docx files are allowed."
        )

    filename = os.path.basename(
        file.filename
    )

    file_path = os.path.join(
        DOCUMENTS_DIR,
        filename
    )

    try:

        os.makedirs(
            DOCUMENTS_DIR,
            exist_ok=True
        )

        with open(
            file_path,
            "wb"
        ) as saved_file:

            shutil.copyfileobj(
                file.file,
                saved_file
            )

        logger.info(
            "Document saved: %s",
            file_path
        )

        document = load_document(
            file_path
        )

        logger.info(
            "Document loaded successfully: %s",
            filename
        )

        return {
            "message": "Document uploaded successfully",
            "filename": filename,
            "file_type": extension,
            "document": document
        }

    except Exception as e:

        logger.exception(
            "Document upload failed: %s",
            e
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to upload and process document."
        )

    finally:

        await file.close()

        logger.info(
            "Upload request completed: %s",
            file.filename
        )


@app.post(
    "/ask",
    response_model=AskResponse
)
async def ask_question(
    request: AskRequest
):

    logger.info(
        "Question received: %s",
        request.question
    )

    try:

        answer = await rag.ask(
            request.question
        )

        if answer is None:

            logger.error(
                "No answer returned from RAG pipeline"
            )

            raise HTTPException(
                status_code=500,
                detail="Unable to generate an answer."
            )

        logger.info(
            "Question answered successfully"
        )

        return AskResponse(
            question=request.question,
            answer=answer,
            sources=[],
            mode="live"
        )

    except HTTPException:

        raise

    except Exception as e:

        logger.exception(
            "Question processing failed: %s",
            e
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to process question."
        )