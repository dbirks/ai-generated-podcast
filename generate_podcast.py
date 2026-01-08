#!/usr/bin/env python3
"""
Generate podcast audio from blog posts using ElevenLabs TTS API.
"""

import os
import re
from pathlib import Path
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

# Load environment variables
load_dotenv()


# Simple profanity filter - add words as needed
PROFANITY_MAP = {
    r'\bfuck\b': 'f***',
    r'\bshit\b': 's***',
    r'\bass\b': 'a**',
    r'\bdamn\b': 'd***',
    r'\bhell\b': 'h***',
    r'\bbitch\b': 'b****',
    r'\bbastard\b': 'b******',
}


def clean_text(text: str) -> tuple[str, bool]:
    """
    Clean profanity from text.

    Returns:
        tuple: (cleaned_text, was_edited)
    """
    cleaned = text
    was_edited = False

    for pattern, replacement in PROFANITY_MAP.items():
        new_text = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
        if new_text != cleaned:
            was_edited = True
        cleaned = new_text

    return cleaned, was_edited


def add_metadata_intro(
    text: str,
    blog_url: str = None,
    was_edited: bool = False,
    ai_tools: list[str] = None
) -> str:
    """
    Add intro with metadata about the blog post and generation.

    Args:
        text: The main blog post text
        blog_url: URL of the original blog post
        was_edited: Whether the text was edited for language
        ai_tools: List of AI tools/models used

    Returns:
        Full text with intro
    """
    intro_parts = []

    if blog_url:
        intro_parts.append(f"This episode is based on a blog post available at {blog_url}.")

    if was_edited:
        intro_parts.append("The text has been lightly edited for language.")

    if ai_tools:
        tools_str = ", ".join(ai_tools)
        intro_parts.append(f"This audio was generated using {tools_str}.")

    if intro_parts:
        intro = " ".join(intro_parts) + "\n\n"
        return intro + text

    return text


def generate_podcast_audio(
    text: str,
    output_path: str,
    blog_url: str = None,
    filter_profanity: bool = True,
    voice_id: str = None,
    model_id: str = None,
) -> dict:
    """
    Generate podcast audio from text using ElevenLabs TTS.

    Args:
        text: The blog post text to convert
        output_path: Where to save the audio file (e.g., "episode.mp3")
        blog_url: Optional URL of the original blog post
        filter_profanity: Whether to filter profanity (default: True)
        voice_id: ElevenLabs voice ID (defaults to env var)
        model_id: ElevenLabs model ID (defaults to env var)

    Returns:
        dict with metadata about the generation
    """
    # Clean text if requested
    was_edited = False
    if filter_profanity:
        text, was_edited = clean_text(text)

    # Get AI tools used
    ai_tools = [
        "ElevenLabs text-to-speech",
        model_id or os.getenv('MODEL_ID', 'eleven_multilingual_v2')
    ]

    # Add metadata intro
    full_text = add_metadata_intro(
        text,
        blog_url=blog_url,
        was_edited=was_edited,
        ai_tools=ai_tools
    )

    # Initialize ElevenLabs client
    client = ElevenLabs(api_key=os.getenv('ELEVENLABS_API_KEY'))

    # Get voice and model IDs
    voice = voice_id or os.getenv('VOICE_ID', 'JBFqnCBsd6RMkjVDRZzb')
    model = model_id or os.getenv('MODEL_ID', 'eleven_multilingual_v2')

    print(f"Generating audio with ElevenLabs...")
    print(f"Voice: {voice}")
    print(f"Model: {model}")
    print(f"Text length: {len(full_text)} characters")

    # Generate audio
    audio = client.text_to_speech.convert(
        text=full_text,
        voice_id=voice,
        model_id=model,
        output_format="mp3_44100_128"
    )

    # Save to file
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'wb') as f:
        for chunk in audio:
            f.write(chunk)

    print(f"Audio saved to: {output_file}")

    return {
        'output_path': str(output_file),
        'was_edited': was_edited,
        'blog_url': blog_url,
        'ai_tools': ai_tools,
        'text_length': len(full_text)
    }


def main():
    """Example usage"""

    # Example blog post text
    blog_text = """
    This is an example blog post about programming.
    You can replace this with actual blog content.
    """

    # Generate the podcast
    result = generate_podcast_audio(
        text=blog_text,
        output_path="output.mp3",
        blog_url="https://example.com/my-blog-post",
        filter_profanity=True
    )

    print("\nGeneration complete!")
    print(f"Metadata: {result}")


if __name__ == "__main__":
    main()
