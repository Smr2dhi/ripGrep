import asyncio

from app.rag_pipeline import RagPipeline


async def main():

    rag=RagPipeline()

    while True:

        question=input("\nYou: ")

        if question.lower()=="exit":
            break

        answer=await rag.ask(question)

        print("\nAssistant:",answer)


if __name__=="__main__":
    asyncio.run(main())