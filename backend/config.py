import os
from dotenv import load_dotenv
from utils.logging import get_logger
logger=get_logger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ENV_FILE = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_FILE)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_ENDPOINT = os.getenv(
    "GEMINI_ENDPOINT",
    "https://generativelanguage.googleapis.com/v1beta/openai/"
)

GEMINI_MODEL = os.getenv("GEMINI_MODEL")

DOCUMENTS_DIR = os.path.join(BASE_DIR, "documents")


logger.info("BASE_DIR: %s", BASE_DIR)
logger.info("ENV_FILE: %s", ENV_FILE)
logger.info("ENV file exists: %s", os.path.exists(ENV_FILE))

logger.info("GEMINI_API_KEY configured: %s", bool(GEMINI_API_KEY))
logger.info("GEMINI_ENDPOINT: %s", GEMINI_ENDPOINT)
logger.info("GEMINI_MODEL: %s", GEMINI_MODEL)

logger.info("DOCUMENTS_DIR: %s", DOCUMENTS_DIR)
logger.info("Documents directory exists: %s", os.path.exists(DOCUMENTS_DIR))