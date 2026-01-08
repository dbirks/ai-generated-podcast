"""Text cleaning using Claude Agent SDK."""

import json
from dataclasses import dataclass

import anyio
from claude_agent_sdk import query, ClaudeAgentOptions


@dataclass
class CleanResult:
    cleaned_text: str
    was_edited: bool
    changes_made: list[str]


async def clean_text(text: str, model: str = "sonnet") -> CleanResult:
    """
    Clean profanity from text using Claude Agent SDK.

    Uses your existing Claude Code subscription - no separate API key needed.
    """
    prompt = f"""Clean any profanity or inappropriate language from this text while preserving its meaning and tone.
Replace profane words with family-friendly alternatives that sound natural when read aloud.

Return your response as JSON with this exact format:
{{
    "cleaned_text": "the cleaned version of the text",
    "was_edited": true or false,
    "changes_made": ["list of changes if any"]
}}

Text to clean:
{text}"""

    options = ClaudeAgentOptions(
        model=model,
        output_format="text",
        session_persistence=False,
    )

    response_parts = []
    async for message in query(prompt=prompt, options=options):
        response_parts.append(str(message))

    response_text = "".join(response_parts).strip()

    # Extract JSON from response (may be wrapped in code blocks)
    json_str = response_text
    if "```json" in response_text:
        start = response_text.find("```json") + 7
        end = response_text.find("```", start)
        json_str = response_text[start:end].strip()
    elif "```" in response_text:
        start = response_text.find("```") + 3
        end = response_text.find("```", start)
        json_str = response_text[start:end].strip()

    try:
        data = json.loads(json_str)
        return CleanResult(
            cleaned_text=data.get("cleaned_text", text),
            was_edited=data.get("was_edited", False),
            changes_made=data.get("changes_made", []),
        )
    except json.JSONDecodeError:
        print(f"Warning: Could not parse JSON. Raw output:\n{response_text}")
        return CleanResult(
            cleaned_text=response_text,
            was_edited=False,
            changes_made=[],
        )


def clean_text_sync(text: str, model: str = "sonnet") -> CleanResult:
    """Synchronous wrapper for clean_text."""
    return anyio.run(clean_text, text, model)
