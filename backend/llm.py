import os
from backend.prompt import AGENT_INSTRUCTIONS,REFUSAL_ANSWER
from agents.exceptions import ModelBehaviorError

from backend.conversation import ConversationMemory
from openai import AsyncOpenAI,OpenAIError
from utils.logging import get_logger

from backend.grep_tool import grep_search,list_files

from agents import(
    Agent,
    Runner,
    set_tracing_disabled,
    set_default_openai_client,
    set_default_openai_api,
    ModelSettings
    )


from backend.config import(
    GEMINI_API_KEY,
    GEMINI_ENDPOINT,
    GEMINI_MODEL
)


set_tracing_disabled(True)
set_default_openai_api("chat_completions")

logger=get_logger(__name__)



class LLMClient:
    def __init__(self):
        self.last_error=None
        self.memory=ConversationMemory(max_history=2)

        logger.info("Initializing LLM client")

        self.api_key=GEMINI_API_KEY
        self.base_url=GEMINI_ENDPOINT
        self.model_name=GEMINI_MODEL

        logger.info("Gemini model configured: %s",self.model_name)
        logger.info("Gemini endpoint configured: %s",self.base_url)
        logger.info("Gemini API key configured: %s",bool(self.api_key))

        self.client=AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )
        logger.info("AsyncOpenAI client created")

        set_default_openai_client(
            self.client,
            use_for_tracing=False
        )

        logger.info("Default OpenAI-compatible client configured")


    async def llm_call(
            self,
            question,
            system_instruction=AGENT_INSTRUCTIONS):

        logger.info("Starting LLM call")


        logger.info(
            "Conversation context prepared - summary: %s "
            "chars, recent conversations: %s",
            len(self.memory.summary),len(self.memory.history)) 

        logger.info("Creating GrepRAG agent")
        
        agent=Agent(
            name="GrepRAG Assistant",
            instructions=system_instruction,
            model=self.model_name,
            # model_settings=ModelSettings(max_tokens=1500),
            tools=[grep_search,list_files]
        )
        logger.info("Agent created successfully")
        logger.debug("System instaruction: "+str(system_instruction))
        logger.info("Tools available to agent: grep_search, list_files")
        logger.info("Starting agent execution")

        try:

            memory=self.memory.get_memory()
            logger.info("Conversation memory retrieved")

            full_prompt=f"""
{memory}

Current user question :
{question}

"""
            logger.info("Sending question and conversation context to agent")

            response=await Runner.run(
                agent,
                full_prompt, 
            )

            logger.info("Agent execution completed successfully")

            if response.context_wrapper.usage:
                logger.info(
                    "Token usage - input: %s, output: %s, total: %s",
                    response.context_wrapper.usage.input_tokens,
                    response.context_wrapper.usage.output_tokens,
                    response.context_wrapper.usage.total_tokens
                )

            answer=response.final_output

            logger.info("LLM response generated successfully")

            self.memory.add_conversation(question,answer)  

            logger.info("Conversation added to memory")

            return answer 


        except ModelBehaviorError as e:
            self.last_error=str(e)
            logger.error("ModelBehaviour error: %s",e)
            return None  
        except OpenAIError as e:
            self.last_error=str(e)  
            logger.error("Gemini API error: %s",e)
            return None  

        except Exception as e:
            self.last_error=str(e)
            logger.exception("Unexpected LLM error: %s",e)  
            return None