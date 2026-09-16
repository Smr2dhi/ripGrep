from app.llm import LLMClient
from utils.logging import get_logger


logger = get_logger(__name__)


class RagPipeline:
    def __init__(self):
        logger.info("Initializing RAG pipeline")

        self.llm = LLMClient()

        logger.info("RAG pipeline initialized successfully")

    async def ask(self, question):
        logger.info("Received question: %s", question)

        logger.info("Sending question to LLM")
        response = await self.llm.llm_call(question)

        if response:
            logger.info("RAG pipeline completed successfully")
        else:
            logger.error("RAG pipeline failed: LLM returned no response")

        return response