from pathlib import Path
import os
from docx import Document
from pypdf import PdfReader


def load_txt(path):
    path = Path(path)

    text= path.read_text(
        encoding="utf-8"
    )
    return {
        "text": text,
        "document_name": path.name,
        "file_type": "txt",
        "pages": None
    }

def load_md(path):
    path = Path(path)

    text= path.read_text(
        encoding="utf-8"
    )
    return {
        "text": text,
        "document_name": path.name,
        "file_type": "md",
        "pages": None
    }



def load_docx(path):
    path = Path(path)

    document = Document(path)

    text = []

    for item in document.iter_inner_content():

        if hasattr(item, "text"):
            if item.text.strip():
                text.append(item.text)

        elif hasattr(item, "rows"):

            text.append("TABLE:")

            for row in item.rows:

                row_data = []

                for cell in row.cells:
                    row_data.append(
                        cell.text.strip()
                    )

                text.append(
                    " | ".join(row_data)
                )

    return {
        "text": "\n".join(text),
        "document_name": path.name,
        "file_type": "docx",
        "pages": None
    }

def load_pdf(path):
    path = Path(path)

    reader = PdfReader(path)

    pages = []
    text = []

    for page_number, page in enumerate(
        reader.pages,
        start=1
    ):

        page_text = page.extract_text(
            extraction_mode="layout"
        )

        if page_text:
            page_text = page_text.strip()

        pages.append({
            "page": page_number,
            "text": page_text
        })

        if page_text:
            text.append(
                f"[Page {page_number}]\n"
                f"{page_text}"
            )

    return {
        "text": "\n\n".join(text),
        "document_name": path.name,
        "file_type": "pdf",
        "pages": pages
    }

def load_document(path):

    extension = os.path.splitext(path)[1].lower()

    if extension == ".txt":
        return load_txt(path)

    elif extension == ".md":
        return load_md(path)

    elif extension == ".docx":
        return load_docx(path)

    elif extension == ".pdf":
        return load_pdf(path)

    else:
        raise ValueError(
            f"Unsupported file type: {extension}"
        )