import asyncio
from app.rag_pipeline import RagPipeline

async def main():
    rag= RagPipeline()

    question = "What is the company's work from home policy?"

    keyword=await rag .extract_keyword(question)
    print("Question:", question)
    print("Keyword:", keyword)


if __name__ == "__main__":
    asyncio.run(main())