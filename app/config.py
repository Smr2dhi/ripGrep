import os
from dotenv import load_dotenv

BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR,".env"))

GEMINI_API_KEY=os.getenv("GEMINI_API_KEY=os.getenv")
GEMINI_ENDPOINT = os.getenv(
    "GEMINI_ENDPOINT",
    "https://generativelanguage.googleapis.com/v1beta/openai/"
)

GEMINI_MODEL = os.getenv("GEMINI_MODEL")
DOCUMENTS_DIR = os.path.join(BASE_DIR, "documents")