import subprocess

from utils.logging import logging
from agents import function_tool
from app.config import DOCUMENTS_DIR

logger = logging.getLogger(__name__)

@function_tool
def grep_search(keywords: list[str])-> str:


    """
    Search the company knowledge base using keywords.

    Pass individual useful search terms, not the complete user question.
    Use this tool when information is needed from the knowledge base.
    """
    print("SEARCH KEYWORDS:", keywords)
    command=[
        "rg",
        "-n",
        "-i",
        "-F"
    ]
    for keyword in keywords:
        command.extend(["-e",keyword])
    command.append(DOCUMENTS_DIR)

    try:
        result=subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False #"If the command exits with a non-zero status, don't automatically raise a Python exception
        )
        if result.returncode == 0:
            logger.info("Grep search completed successfully")
            return result.stdout
        
        if result.returncode == 1:
            logger.info("Grep search found no matches")
            return "NO matching information found."
        
        logger.error("Grep search failed: %s", result.stderr)
        return f"Search error: {result.stderr}"

    except OSError as e:
        logger.exception("Could not start ripgrep")
        return f"Search tool error: {e}"

    except Exception as e:
        logger.exception("Unexpected error during grep search")
        return f"Unexpected search error: {e}"