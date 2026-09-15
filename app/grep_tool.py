import subprocess
from agents import function_tool

from app.config import DOCUMENTS_DIR

@function_tool
def grep_search(keywords:list[str])-> str:
    command=[
         "rg",
        "-n",
        "-i",
        "-F"
    ]

    for keyword in keywords:
        command.extend(["-e", keyword])

    command.append(DOCUMENTS_DIR)

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False
    )

    if result.returncode == 1:
        return "No matching results found."

    if result.returncode == 2:
        return f"ripgrep error: {result.stderr}"

    return result.stdout