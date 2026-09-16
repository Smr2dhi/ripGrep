import os

from app.config import DOCUMENTS_DIR
from utils.logging import get_logger

logger = get_logger(__name__)


def get_context(
    grep_result,
    context_lines=5,
    max_chars=12000
):
    if not grep_result:
        logger.info("No grep results to expand")
        return "NO matching information found."

    matches = {}

    for line in grep_result.splitlines():

        parts = line.split(":", 2)

        if len(parts) < 3:
            continue

        file_path = parts[0]
        line_number = parts[1]

        try:
            line_number = int(line_number)
        except ValueError:
            continue

        if file_path not in matches:
            matches[file_path] = []

        matches[file_path].append(line_number)

    logger.info(
        "Parsed grep results - files: %s, matches: %s",
        len(matches),
        sum(len(lines) for lines in matches.values())
    )

    final_context = []
    total_chars = 0

    for file_path, line_numbers in matches.items():

        full_path = os.path.join(
            DOCUMENTS_DIR,
            file_path
        )

        try:
            with open(
                full_path,
                "r",
                encoding="utf-8"
            ) as file:

                lines = file.readlines()

        except FileNotFoundError:

            logger.error(
                "File not found while retrieving context: %s",
                full_path
            )

            continue

        except Exception as e:

            logger.exception(
                "Could not read file: %s",
                full_path
            )

            continue

        line_numbers = sorted(
            set(line_numbers)
        )

        ranges = []

        start = line_numbers[0]
        end = line_numbers[0]

        for line_number in line_numbers[1:]:

            if line_number <= end + context_lines * 2 + 1:
                end = line_number
            else:
                ranges.append(
                    (start, end)
                )

                start = line_number
                end = line_number

        ranges.append(
            (start, end)
        )

        logger.info(
            "Created %s context groups for %s",
            len(ranges),
            file_path
        )

        file_context = []

        for start, end in ranges:

            context_start = max(
                1,
                start - context_lines
            )

            context_end = min(
                len(lines),
                end + context_lines
            )

            for line_number in range(
                context_start,
                context_end + 1
            ):

                text = lines[line_number - 1].rstrip()

                item = (
                    f"{file_path}:{line_number}:{text}"
                )

                if item not in file_context:
                    file_context.append(item)

        for item in file_context:

            if total_chars + len(item) > max_chars:

                logger.warning(
                    "Maximum context size reached: %s characters",
                    max_chars
                )

                return "\n".join(final_context)

            final_context.append(item)

            total_chars += len(item)

    logger.info(
        "Context retrieval completed - %s characters returned",
        total_chars
    )

    if not final_context:
        return "NO matching information found."

    return "\n".join(final_context)