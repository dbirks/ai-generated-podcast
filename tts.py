"""Text-to-speech generation using ElevenLabs."""

import os
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

load_dotenv()

# Defaults
DEFAULT_VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"
DEFAULT_MODEL_ID = "eleven_multilingual_v2"
MAX_CHARS = 9000  # ElevenLabs limit is 10000, leave margin


def chunk_text(text: str, max_chars: int = MAX_CHARS) -> list[str]:
    """Split text into chunks at paragraph boundaries."""
    paragraphs = text.split("\n\n")
    chunks = []
    current = ""

    for para in paragraphs:
        # If single paragraph exceeds limit, split at sentences
        if len(para) > max_chars:
            sentences = para.replace(". ", ".\n").split("\n")
            for sent in sentences:
                if len(current) + len(sent) + 2 > max_chars:
                    if current:
                        chunks.append(current.strip())
                    current = sent
                else:
                    current = current + " " + sent if current else sent
        elif len(current) + len(para) + 2 > max_chars:
            chunks.append(current.strip())
            current = para
        else:
            current = current + "\n\n" + para if current else para

    if current:
        chunks.append(current.strip())

    return chunks


def generate_audio(
    text: str,
    output_path: Path,
    voice_id: str | None = None,
    model_id: str | None = None,
) -> Path:
    """
    Generate audio from text using ElevenLabs TTS.

    Automatically chunks long text and concatenates audio.
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

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Check if we need to chunk
    if len(text) <= MAX_CHARS:
        # Simple case - single request
        audio = client.text_to_speech.convert(
            text=text,
            voice_id=voice,
            model_id=model,
            output_format="mp3_44100_128",
        )
        with open(output_path, "wb") as f:
            for chunk in audio:
                f.write(chunk)
    else:
        # Chunk and concatenate
        chunks = chunk_text(text)
        print(f"  Splitting into {len(chunks)} chunks...")

        # Generate audio for each chunk
        audio_files = []
        with tempfile.TemporaryDirectory() as tmpdir:
            for i, chunk in enumerate(chunks):
                print(f"  Generating chunk {i+1}/{len(chunks)} ({len(chunk)} chars)...")
                audio = client.text_to_speech.convert(
                    text=chunk,
                    voice_id=voice,
                    model_id=model,
                    output_format="mp3_44100_128",
                )
                chunk_path = Path(tmpdir) / f"chunk_{i:03d}.mp3"
                with open(chunk_path, "wb") as f:
                    for data in audio:
                        f.write(data)
                audio_files.append(chunk_path)

            # Concatenate with ffmpeg
            print(f"  Concatenating {len(audio_files)} audio files...")
            list_file = Path(tmpdir) / "files.txt"
            with open(list_file, "w") as f:
                for af in audio_files:
                    f.write(f"file '{af}'\n")

            import subprocess
            subprocess.run([
                "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                "-i", str(list_file), "-c", "copy", str(output_path)
            ], check=True, capture_output=True)

    print(f"  Saved to: {output_path}")
    return output_path
