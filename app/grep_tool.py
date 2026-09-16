import subprocess
import os
from utils.logging import logging
from agents import function_tool
from app.config import DOCUMENTS_DIR

logger = logging.getLogger(__name__)


@function_tool
def list_files() -> str:
    """List files available in the company knowledge base."""

    try:
        files = [
            file
            for file in os.listdir(DOCUMENTS_DIR)
            if os.path.isfile(os.path.join(DOCUMENTS_DIR, file))
        ]

        logger.info("Files found in knowledge base: %s", len(files))

        return "\n".join(files)

    except OSError as e:
        logger.exception("Could not list knowledge base files")
        return f"File listing error: {e}"

    
@function_tool
def grep_search(keywords: list[str])-> str:


    """
    Search the company knowledge base using keywords.

    Pass individual useful search terms, not the complete user question.
    Use this tool when information is needed from the knowledge base.
    """
    logger.info("SEARCH KEYWORDS: %s", keywords)
    command=[
        "rg",
        "-n",
        "-i",
        "-F"
    ]
    for keyword in keywords:
        command.extend(["-e",keyword])
    command.append(".") #tells rg to search in the current directory.

    try:
        result=subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False ,#"If the command exits with a non-zero status, don't automatically raise a Python exception
            cwd=DOCUMENTS_DIR
        )
        if result.returncode == 0:
            matches = result.stdout.strip().splitlines()

            logger.info(
            "Grep search completed successfully. Matches found: %s",
            len(matches))

            from app.context_retrieval import get_context
            context = get_context(
                result.stdout)
            
            return context
                
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