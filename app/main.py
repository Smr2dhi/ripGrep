import asyncio

from app.rag_pipeline import RagPipeline
from utils.logging import get_logger


logger = get_logger(__name__)


async def main():
    logger.info("Application started")

    rag = RagPipeline()
    logger.info("RAG pipeline created")

    question = "How is user authentication handled?"

    logger.info("Sending question to RAG pipeline: %s", question)

    response = await rag.ask(question)

    if response:
        logger.info("Answer received successfully")
    else:
        logger.error("No answer received from RAG pipeline")

    print("\nANSWER:")
    print(response)

    logger.info("Application completed")


asyncio.run(main())