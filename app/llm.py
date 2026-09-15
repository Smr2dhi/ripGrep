import os
from app.models import SearchKeywords
from utils.prompt import AGENT_INSTRUCTIONS,REFUSAL_ANSWER
from agents.exceptions import ModelBehaviorError
from openai import AsyncOpenAI,OpenAIError
from utils.logging import get_logger

from agents import(
    Agent,
    Runner,
    OpenAIChatCompletionsModel,
    set_tracing_disabled, 
    ModelSettings
    )

from dotenv import load_dotenv

from app.config import (
    GEMINI_API_KEY,
    GEMINI_ENDPOINT,
    GEMINI_MODEL
)

set_tracing_disabled(True)

logger=get_logger(__name__)



class LLMClient:
    def __init__(self):
        self.last_error = None
        load_dotenv()

        set_tracing_disabled(True)

        self.api_key=GEMINI_API_KEY
        self.base_url=GEMINI_ENDPOINT

        self.model_name=GEMINI_MODEL
        self.client=AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=50
        )

        self.model=OpenAIChatCompletionsModel(
            model=self.model_name,
            openai_client=self.client
        )

    async def llm_call(
            self,
            prompt, 
            system_instruction=AGENT_INSTRUCTIONS):

        agent=Agent(
            name="GrepRAG Assistant",
            instructions=system_instruction,
            model=self.model,
            model_settings=ModelSettings(max_tokens=1500),
            output_type=SearchKeywords,

            tools=[]


        )

        try:
            response=await Runner.run(
                agent,
                prompt,
                
            )
            return response.final_output

        except ModelBehaviorError as e:
            self.last_error = str(e)
            logger.error("ModelBehaviour error: %s",e)

        except OpenAIError as e:
            logger.error("Gemini API error: %s", e)
            return None

        except Exception as e:
            self.last_error = str(e)
            logger.error("Unexpected LLM error: %s", e)
            return None
