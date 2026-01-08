"""Text-to-speech generation using ElevenLabs."""

import os
from pathlib import Path

from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

load_dotenv()

# Defaults
DEFAULT_VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"
DEFAULT_MODEL_ID = "eleven_multilingual_v2"


def generate_audio(
    text: str,
    output_path: Path,
    voice_id: str | None = None,
    model_id: str | None = None,
) -> Path:
    """
    Generate audio from text using ElevenLabs TTS.

    Returns the output path.
    """
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise ValueError("ELEVENLABS_API_KEY not set in environment")

    voice = voice_id or os.getenv("VOICE_ID", DEFAULT_VOICE_ID)
    model = model_id or os.getenv("MODEL_ID", DEFAULT_MODEL_ID)

    client = ElevenLabs(api_key=api_key)

    print(f"Generating audio with ElevenLabs...")
    print(f"  Voice: {voice}")
    print(f"  Model: {model}")
    print(f"  Text length: {len(text)} characters")

    audio = client.text_to_speech.convert(
        text=text,
        voice_id=voice,
        model_id=model,
        output_format="mp3_44100_128",
    )

    # Ensure output directory exists
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write audio to file
    with open(output_path, "wb") as f:
        for chunk in audio:
            f.write(chunk)

    print(f"  Saved to: {output_path}")
    return output_path
