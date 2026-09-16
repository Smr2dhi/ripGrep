import asyncio
import logging

from app.rag_pipeline import RagPipeline


logging.basicConfig(
    level=logging.INFO
)


async def main():

    rag = RagPipeline()

    response = await rag.ask(
        "How is user authentication handled?"
    )

    print("\nANSWER:")
    print(response)


if __name__ == "__main__":
    asyncio.run(main())