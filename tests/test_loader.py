from ingestion.loader import load_document


def test_load_txt():

    document = load_document(
        "documents/auth.txt"
    )

    assert document["document_name"] == "auth.txt"
    assert document["file_type"] == "txt"
    assert "authentication" in document["text"].lower()