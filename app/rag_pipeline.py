from app.llm import LLMClient

class RagPipeline:
    def __init__(self):
        self.llm=LLMClient()

    async def extract_keyword(self,question):
        keyword=await self.llm.llm_call(
            question,
            system_instruction=
   """You are a search keyword extraction assistant.

Extract important individual keywords from the user's question.

These keywords will be searched using ripgrep.

Rules:
- Return individual words whenever possible.
- Do not return the complete question.
- Do not return explanations.
- Do not return duplicate keywords.
- Return only useful search terms.
- Return the keywords in the keywords field.

Example:

Question:
What is the company's work from home policy?

Keywords:
["work", "home", "remote", "policy"]

Question:
Where is user authentication handled and what method is used?

Keywords:
["user", "authentication", "login", "method"]
"""
        )
        return keyword