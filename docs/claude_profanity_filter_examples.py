"""
Claude API Profanity Filter Examples
=====================================

Python examples for using Claude API to detect, censor, and clean profanity
from text. Suitable for blog post cleaning before TTS conversion.

Requirements:
    pip install anthropic python-dotenv

Environment Setup:
    Create a .env file with:
    ANTHROPIC_API_KEY=your_api_key_here
"""

import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the Anthropic client
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


# =============================================================================
# Example 1: Basic Profanity Detection
# =============================================================================

def detect_profanity(text: str) -> dict:
    """
    Detect if text contains profanity or inappropriate language.

    Args:
        text: The text to analyze

    Returns:
        dict with keys: has_profanity (bool), details (str)
    """
    prompt = f"""Analyze the following text for profanity, obscenities, or inappropriate language.

Text to analyze:
<text>{text}</text>

Respond with ONLY a JSON object in this format:
{{
    "has_profanity": <true or false>,
    "profane_words": [<list of profane words found>],
    "severity": "<none/mild/moderate/severe>",
    "explanation": "<brief explanation>"
}}"""

    response = client.messages.create(
        model="claude-3-haiku-20240307",  # Using Haiku for cost-effectiveness
        max_tokens=300,
        temperature=0,  # Use 0 for consistent results
        messages=[{"role": "user", "content": prompt}]
    )

    result = json.loads(response.content[0].text)
    return result


# =============================================================================
# Example 2: Censor Profanity with Asterisks
# =============================================================================

def censor_profanity(text: str, censor_char: str = "*") -> dict:
    """
    Replace profanity with censored versions (e.g., f*** or [censored]).

    Args:
        text: The text to censor
        censor_char: Character to use for censoring (default: "*")

    Returns:
        dict with keys: cleaned_text (str), changes_made (bool), original_words (list)
    """
    prompt = f"""Replace any profanity, obscenities, or inappropriate language in the text below with censored versions.

Rules:
- Keep the first letter of each profane word
- Replace remaining letters with "{censor_char}" characters
- Preserve the original sentence structure and meaning
- Keep all punctuation and formatting

Text to censor:
<text>{text}</text>

Respond with ONLY a JSON object in this format:
{{
    "cleaned_text": "<the censored text>",
    "changes_made": <true or false>,
    "censored_words": [<list of words that were censored>]
}}"""

    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1000,
        temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )

    result = json.loads(response.content[0].text)
    return result


# =============================================================================
# Example 3: Clean Text While Preserving Meaning
# =============================================================================

def clean_text_preserve_meaning(text: str) -> dict:
    """
    Rewrite text to remove profanity while preserving the original meaning and tone.
    Best for blog posts where you want natural-sounding, clean text.

    Args:
        text: The text to clean

    Returns:
        dict with keys: cleaned_text (str), changes_made (bool), summary (str)
    """
    prompt = f"""Rewrite the following text to remove any profanity, obscenities, or inappropriate language while preserving the original meaning, tone, and intent.

Guidelines:
- Replace profane words with appropriate alternatives
- Maintain the author's voice and style
- Keep the same emotional impact without offensive language
- Preserve all factual content and key points
- Make the text suitable for text-to-speech conversion

Text to clean:
<text>{text}</text>

Respond with ONLY a JSON object in this format:
{{
    "cleaned_text": "<the cleaned text>",
    "changes_made": <true or false>,
    "changes_summary": "<brief description of what was changed>"
}}"""

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",  # Using Sonnet for better quality
        max_tokens=2000,
        temperature=0.3,  # Slight creativity for natural rewrites
        messages=[{"role": "user", "content": prompt}]
    )

    result = json.loads(response.content[0].text)
    return result


# =============================================================================
# Example 4: Batch Processing for Multiple Texts
# =============================================================================

def batch_clean_texts(texts: list[str]) -> dict:
    """
    Clean multiple texts in a single API call for cost efficiency.

    Args:
        texts: List of texts to clean

    Returns:
        dict mapping text index to cleaned version
    """
    # Format texts with IDs
    texts_str = '\n'.join([f'<text id="{idx}">{text}</text>'
                           for idx, text in enumerate(texts)])

    prompt = f"""Clean the following texts by removing profanity and inappropriate language while preserving meaning.

Texts to clean:
<texts>
{texts_str}
</texts>

Respond with ONLY a JSON object in this format:
{{
    "cleaned_texts": [
        {{
            "id": <text id>,
            "cleaned_text": "<cleaned version>",
            "changes_made": <true or false>
        }},
        ...
    ]
}}"""

    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=4000,
        temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )

    result = json.loads(response.content[0].text)
    return result


# =============================================================================
# Example 5: Advanced Content Moderation with Custom Categories
# =============================================================================

def moderate_content(text: str, custom_categories: list[str] = None) -> dict:
    """
    Perform comprehensive content moderation including profanity and other issues.

    Args:
        text: The text to moderate
        custom_categories: Optional list of additional categories to check

    Returns:
        dict with moderation results
    """
    default_categories = [
        'Profanity and Obscenities',
        'Sexual Content',
        'Hate Speech',
        'Violence',
        'Discriminatory Language'
    ]

    categories = default_categories + (custom_categories or [])
    categories_str = '\n'.join(f'- {cat}' for cat in categories)

    prompt = f"""Analyze the following text for inappropriate content based on these categories:

Categories:
{categories_str}

Text to analyze:
<text>{text}</text>

Respond with ONLY a JSON object in this format:
{{
    "safe": <true or false>,
    "violations": [<list of violated categories>],
    "severity": "<none/low/medium/high>",
    "cleaned_version": "<version with violations removed>",
    "explanation": "<brief explanation of issues found>"
}}"""

    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1000,
        temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )

    result = json.loads(response.content[0].text)
    return result


# =============================================================================
# Example 6: Async Processing for Large Volumes
# =============================================================================

import asyncio
from anthropic import AsyncAnthropic

async def async_clean_text(text: str) -> dict:
    """
    Asynchronously clean text - useful for processing many texts concurrently.

    Args:
        text: The text to clean

    Returns:
        dict with cleaned text and metadata
    """
    async_client = AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    prompt = f"""Remove profanity and inappropriate language from this text while preserving meaning:

<text>{text}</text>

Respond with ONLY a JSON object:
{{
    "cleaned_text": "<cleaned version>",
    "changes_made": <true or false>
}}"""

    response = await async_client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1000,
        temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )

    return json.loads(response.content[0].text)


async def process_multiple_texts_async(texts: list[str]) -> list[dict]:
    """
    Process multiple texts concurrently for maximum efficiency.

    Args:
        texts: List of texts to process

    Returns:
        List of results in the same order as input
    """
    tasks = [async_clean_text(text) for text in texts]
    results = await asyncio.gather(*tasks)
    return results


# =============================================================================
# Example 7: Smart Text Cleaning with Context Awareness
# =============================================================================

def smart_clean_blog_post(text: str, preserve_quotes: bool = True) -> dict:
    """
    Intelligently clean blog posts with context awareness.
    Useful for TTS conversion where quoted profanity might be acceptable.

    Args:
        text: The blog post text
        preserve_quotes: If True, be more lenient with quoted profanity

    Returns:
        dict with cleaned text optimized for TTS
    """
    context_instruction = ""
    if preserve_quotes:
        context_instruction = """
- If profanity appears in direct quotes, you may keep it if it's essential to the quote's meaning
- Always clean profanity in the author's own voice"""

    prompt = f"""Clean this blog post for text-to-speech conversion. Remove or replace profanity while maintaining the author's voice.

Guidelines:
- Make text sound natural when read aloud
- Replace profanity with appropriate alternatives
- Preserve the blog post's tone and personality
- Keep all factual content intact{context_instruction}

Blog post:
<text>{text}</text>

Respond with ONLY a JSON object:
{{
    "cleaned_text": "<TTS-ready text>",
    "changes_made": <true or false>,
    "tts_notes": "<any notes about how this will sound when spoken>"
}}"""

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",  # Better quality for nuanced cleaning
        max_tokens=3000,
        temperature=0.3,
        messages=[{"role": "user", "content": prompt}]
    )

    result = json.loads(response.content[0].text)
    return result


# =============================================================================
# Usage Examples
# =============================================================================

if __name__ == "__main__":
    # Sample texts for testing
    test_texts = [
        "This is a completely clean text with no issues.",
        "What the hell is going on here? This is absolutely insane!",
        "The damn API keeps timing out and it's driving me crazy.",
    ]

    print("=" * 70)
    print("EXAMPLE 1: Basic Profanity Detection")
    print("=" * 70)
    for text in test_texts[:2]:
        result = detect_profanity(text)
        print(f"\nText: {text}")
        print(f"Result: {json.dumps(result, indent=2)}")

    print("\n" + "=" * 70)
    print("EXAMPLE 2: Censor Profanity")
    print("=" * 70)
    for text in test_texts[1:3]:
        result = censor_profanity(text)
        print(f"\nOriginal: {text}")
        print(f"Censored: {result['cleaned_text']}")
        print(f"Changes made: {result['changes_made']}")

    print("\n" + "=" * 70)
    print("EXAMPLE 3: Clean While Preserving Meaning")
    print("=" * 70)
    result = clean_text_preserve_meaning(test_texts[2])
    print(f"\nOriginal: {test_texts[2]}")
    print(f"Cleaned: {result['cleaned_text']}")
    print(f"Summary: {result['changes_summary']}")

    print("\n" + "=" * 70)
    print("EXAMPLE 4: Batch Processing")
    print("=" * 70)
    batch_result = batch_clean_texts(test_texts)
    for item in batch_result['cleaned_texts']:
        print(f"\nID {item['id']}: {item['cleaned_text']}")
        print(f"Changes: {item['changes_made']}")

    print("\n" + "=" * 70)
    print("EXAMPLE 5: Content Moderation")
    print("=" * 70)
    result = moderate_content(test_texts[1])
    print(f"\nText: {test_texts[1]}")
    print(f"Safe: {result['safe']}")
    print(f"Violations: {result['violations']}")
    print(f"Cleaned: {result['cleaned_version']}")

    print("\n" + "=" * 70)
    print("EXAMPLE 6: Async Processing")
    print("=" * 70)
    async_results = asyncio.run(process_multiple_texts_async(test_texts))
    for idx, result in enumerate(async_results):
        print(f"\nText {idx}: {result['cleaned_text']}")

    print("\n" + "=" * 70)
    print("EXAMPLE 7: Smart Blog Post Cleaning")
    print("=" * 70)
    blog_text = """The conference was a complete disaster. The damn speakers kept
    going over time and the Wi-Fi was shit. However, the keynote speaker said,
    "Sometimes you have to say 'screw it' and just ship the product." That
    really resonated with me."""

    result = smart_clean_blog_post(blog_text, preserve_quotes=True)
    print(f"\nOriginal:\n{blog_text}")
    print(f"\nCleaned:\n{result['cleaned_text']}")
    print(f"\nTTS Notes: {result['tts_notes']}")

    print("\n" + "=" * 70)
    print("All examples completed!")
    print("=" * 70)
