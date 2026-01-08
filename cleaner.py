"""Text cleaning using Claude Agent SDK."""

from dataclasses import dataclass
from pathlib import Path

import anyio
from claude_agent_sdk import query, ClaudeAgentOptions


@dataclass
class CleanResult:
    file_path: Path
    was_edited: bool
    changes_made: list[str]


async def clean_file(file_path: Path, model: str = "sonnet") -> CleanResult:
    """
    Clean profanity from a file using Claude Agent SDK.

    Uses Claude Code's normal permission flow - will prompt for Edit tool usage.
    Makes surgical changes to the file in place using the Edit tool.
    """
    abs_path = file_path.resolve()

    prompt = f"""Read the file at {abs_path} and scan it for any profanity or inappropriate language.

For each instance found, use the Edit tool to replace it with a family-friendly alternative that sounds natural when read aloud.

Be extremely conservative - ONLY replace actual profanity/swear words. Keep everything else exactly as written.

After making all edits, output a summary of changes made in this format:
CHANGES_MADE:
- "original word" → "replacement"
- ...

If no profanity was found, output:
CHANGES_MADE: none"""

    options = ClaudeAgentOptions(
        model=model,
        max_turns=50,  # Allow multiple edit operations
    )

    response_parts = []
    async for message in query(prompt=prompt, options=options):
        response_parts.append(str(message))

    response_text = "".join(response_parts).strip()

    # Parse changes from response
    changes_made = []
    was_edited = False

    if "CHANGES_MADE:" in response_text:
        changes_section = response_text.split("CHANGES_MADE:")[-1].strip()
        if changes_section.lower() != "none":
            was_edited = True
            for line in changes_section.split("\n"):
                line = line.strip()
                if line.startswith("-") and "→" in line:
                    changes_made.append(line[1:].strip())

    return CleanResult(
        file_path=abs_path,
        was_edited=was_edited,
        changes_made=changes_made,
    )


def clean_file_sync(file_path: Path, model: str = "sonnet") -> CleanResult:
    """Synchronous wrapper for clean_file."""
    return anyio.run(clean_file, file_path, model)
