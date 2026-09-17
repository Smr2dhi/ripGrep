import os
from docx import Document
from pypdf import PdfReader
from utils.logging import get_logger

logger = get_logger(__name__)


def load_document(path):
    try:

        extension = os.path.splitext(path)[1].lower()
        filename=os.path.basename(path)

        if extension in [".txt",".md"]:
            with open(path,"r",encoding="utf-8")as file:
                text=file.read()
            logger.info(f"File loaded: {filename}")

            return{
                "text": text,
                "document_name": filename,
                "file_type": extension[1:],
                "pages": None
            }

        elif extension ==".docx":
            document=Document(path)
            text=[]

            for item in document.iter_inner_content():
                if hasattr(item,"text"):

                    if item.text.strip():
                        text.append(item.text)

                elif hasattr(item,"rows"):
                    text.append("TABLE: ")

                    for row in item.rows:
                        row_data=[]

                        for cell in row.cells:
                            row_data.append(cell.text.strip())

                            text.append(" | ".join(row_data))

            logger.info(f"File loaded: {filename}")
            return {
                "text": "\n".join(text),
                "document_name": filename,
                "file_type": "docx",
                "pages": None
            }

        elif extension == ".pdf":
            reader =PdfReader(path)
            pages=[]
            text=[]

            for page_number ,page in enumerate(
                reader.pages,start=1):

                page_text=page.extract_text(
                    extraction_mode="layout"
                )
                if page_text:
                    page_text =page_text.strip()

                pages.append({
                    "page":page_number,
                    "text":page_text
                })

                if page_text:
                    text.append(
                        f"[Page {page_number}]\n"
                        f"{page_text}"
                    )
            logger.info(f"File loaded: {filename}")
            return {
                "text": "\n\n".join(text),
                "document_name": filename,
                "file_type": "pdf",
                "pages": pages
            }
        else:
            logger.error(f"Unsupported file type: {extension}")
            raise ValueError(f"Unsupported file type: {extension}")

    except FileNotFoundError as e:
        logger.error(f"File not found: {filename} - {e}")
        raise

    except Exception as e:
        logger.error( f"Error loading file: {filename} - {e}")
        raise
