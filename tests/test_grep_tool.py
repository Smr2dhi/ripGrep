import pytest

from agents import Agent, Runner
from agents.testing import (
    ScriptedModel,
    assistant_message,
    function_call
)

from app.grep_tool import grep_search


@pytest.mark.asyncio
async def test_agent_tool_call():

    model = ScriptedModel(
        [
            [
                function_call(
                    "grep_search",
                    {
                        "keywords": ["authentication"]
                    },
                    call_id="call_1"
                )
            ],
            [
                assistant_message(
                    "User authentication is handled through the login system."
                )
            ]
        ]
    )

    agent = Agent(
        name="GrepRAG Assistant",
        instructions=(
            "Use grep_search to find information "
            "from the knowledge base."
        ),
        model=model,
        tools=[grep_search]
    )

    result = await Runner.run(
        agent,
        "How is user authentication handled?"
    )

    assert (
        "authentication"
        in result.final_output.lower()
    )

    assert len(model.calls) == 2

    model.assert_complete()