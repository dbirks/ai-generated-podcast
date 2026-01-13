"""Text-to-speech generation using ElevenLabs or OpenAI."""

import os
import subprocess
import tempfile
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ElevenLabs defaults
ELEVENLABS_DEFAULT_VOICE = "JBFqnCBsd6RMkjVDRZzb"
ELEVENLABS_DEFAULT_MODEL = "eleven_multilingual_v2"
ELEVENLABS_MAX_CHARS = 9000

# OpenAI defaults
OPENAI_DEFAULT_VOICE = "cedar"
OPENAI_DEFAULT_MODEL = "gpt-4o-mini-tts"
OPENAI_MAX_CHARS = 4000  # Limit is 4096, leave margin


def chunk_text(text: str, max_chars: int) -> list[str]:
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


def _generate_elevenlabs(
    text: str,
    output_path: Path,
    voice: str,
    model: str,
) -> Path:
    """Generate audio using ElevenLabs."""
    from elevenlabs.client import ElevenLabs

    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise ValueError("ELEVENLABS_API_KEY not set in environment")

    client = ElevenLabs(api_key=api_key)

    print(f"Generating audio with ElevenLabs...")
    print(f"  Voice: {voice}")
    print(f"  Model: {model}")
    print(f"  Text length: {len(text)} characters")

    if len(text) <= ELEVENLABS_MAX_CHARS:
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
        chunks = chunk_text(text, ELEVENLABS_MAX_CHARS)
        print(f"  Splitting into {len(chunks)} chunks...")
        _generate_chunked(client, chunks, output_path, voice, model, "elevenlabs")

    return output_path


def _generate_openai(
    text: str,
    output_path: Path,
    voice: str,
    model: str,
) -> Path:
    """Generate audio using OpenAI TTS."""
    from openai import OpenAI

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set in environment")

    client = OpenAI(api_key=api_key)

    print(f"Generating audio with OpenAI...")
    print(f"  Voice: {voice}")
    print(f"  Model: {model}")
    print(f"  Text length: {len(text)} characters")

    if len(text) <= OPENAI_MAX_CHARS:
        with client.audio.speech.with_streaming_response.create(
            model=model,
            voice=voice,
            input=text,
            response_format="mp3",
        ) as response:
            response.stream_to_file(output_path)
    else:
        chunks = chunk_text(text, OPENAI_MAX_CHARS)
        print(f"  Splitting into {len(chunks)} chunks...")
        _generate_chunked_openai(client, chunks, output_path, voice, model)

    return output_path


def _generate_chunked(client, chunks, output_path, voice, model, provider):
    """Generate and concatenate chunked audio for ElevenLabs."""
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

        _concatenate_audio(audio_files, output_path, tmpdir)


def _generate_chunked_openai(client, chunks, output_path, voice, model):
    """Generate and concatenate chunked audio for OpenAI."""
    audio_files = []
    with tempfile.TemporaryDirectory() as tmpdir:
        for i, chunk in enumerate(chunks):
            print(f"  Generating chunk {i+1}/{len(chunks)} ({len(chunk)} chars)...")
            chunk_path = Path(tmpdir) / f"chunk_{i:03d}.mp3"
            with client.audio.speech.with_streaming_response.create(
                model=model,
                voice=voice,
                input=chunk,
                response_format="mp3",
            ) as response:
                response.stream_to_file(chunk_path)
            audio_files.append(chunk_path)

        _concatenate_audio(audio_files, output_path, tmpdir)


def _concatenate_audio(audio_files, output_path, tmpdir):
    """Concatenate audio files using ffmpeg."""
    print(f"  Concatenating {len(audio_files)} audio files...")
    list_file = Path(tmpdir) / "files.txt"
    with open(list_file, "w") as f:
        for af in audio_files:
            f.write(f"file '{af}'\n")

    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(list_file), "-c", "copy", str(output_path)
    ], check=True, capture_output=True)


def generate_audio(
    text: str,
    output_path: Path,
    provider: str = "elevenlabs",
    voice: str | None = None,
    model: str | None = None,
) -> Path:
    """
    Generate audio from text using TTS.

    Args:
        text: Text to convert to speech
        output_path: Path to save audio file
        provider: "elevenlabs" or "openai"
        voice: Voice ID (provider-specific)
        model: Model ID (provider-specific)

    Returns the output path.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if provider == "openai":
        voice = voice or os.getenv("OPENAI_VOICE", OPENAI_DEFAULT_VOICE)
        model = model or os.getenv("OPENAI_MODEL", OPENAI_DEFAULT_MODEL)
        _generate_openai(text, output_path, voice, model)
    else:
        voice = voice or os.getenv("VOICE_ID", ELEVENLABS_DEFAULT_VOICE)
        model = model or os.getenv("MODEL_ID", ELEVENLABS_DEFAULT_MODEL)
        _generate_elevenlabs(text, output_path, voice, model)

    print(f"  Saved to: {output_path}")
    return output_path


def _generate_silence(duration_seconds: float, output_path: Path) -> Path:
    """Generate silence using ffmpeg."""
    print(f"  Generating {duration_seconds}s silence...")
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", "-i",
        f"anullsrc=r=44100:cl=stereo:d={duration_seconds}",
        "-c:a", "libmp3lame", "-b:a", "128k", str(output_path)
    ], check=True, capture_output=True)
    return output_path


def generate_audio_with_intro(
    intro_text: str,
    main_text: str,
    output_path: Path,
    provider: str = "openai",
    intro_voice: str = "marin",
    main_voice: str = "cedar",
    model: str | None = None,
    pause_duration: float = 2.0,
) -> Path:
    """
    Generate audio with intro (different voice) + pause + main content.

    Args:
        intro_text: Text for intro (spoken in intro_voice)
        main_text: Main content text (spoken in main_voice)
        output_path: Path to save final audio file
        provider: "openai" or "elevenlabs"
        intro_voice: Voice for intro (default: "marin")
        main_voice: Voice for main content (default: "cedar")
        model: Model ID (provider-specific)
        pause_duration: Seconds of silence between intro and main (default: 2.0)

    Returns the output path.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Generating audio with intro...")
    print(f"  Intro voice: {intro_voice}")
    print(f"  Main voice: {main_voice}")
    print(f"  Pause: {pause_duration}s")
    print(f"  Intro length: {len(intro_text)} characters")
    print(f"  Main length: {len(main_text)} characters")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # 1. Generate intro with intro_voice
        intro_path = tmpdir_path / "intro.mp3"
        if provider == "openai":
            from openai import OpenAI
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not set in environment")
            client = OpenAI(api_key=api_key)
            model = model or os.getenv("OPENAI_MODEL", OPENAI_DEFAULT_MODEL)

            print(f"  Generating intro ({len(intro_text)} chars)...")
            with client.audio.speech.with_streaming_response.create(
                model=model,
                voice=intro_voice,
                input=intro_text,
                response_format="mp3",
            ) as response:
                response.stream_to_file(intro_path)
        else:
            from elevenlabs.client import ElevenLabs
            api_key = os.getenv("ELEVENLABS_API_KEY")
            if not api_key:
                raise ValueError("ELEVENLABS_API_KEY not set in environment")
            client = ElevenLabs(api_key=api_key)
            model = model or os.getenv("MODEL_ID", ELEVENLABS_DEFAULT_MODEL)

            print(f"  Generating intro ({len(intro_text)} chars)...")
            audio = client.text_to_speech.convert(
                text=intro_text,
                voice_id=intro_voice,
                model_id=model,
                output_format="mp3_44100_128",
            )
            with open(intro_path, "wb") as f:
                for chunk in audio:
                    f.write(chunk)

        # 2. Generate silence
        silence_path = tmpdir_path / "silence.mp3"
        _generate_silence(pause_duration, silence_path)

        # 3. Generate main content with main_voice (with chunking if needed)
        main_path = tmpdir_path / "main.mp3"
        if provider == "openai":
            from openai import OpenAI
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not set in environment")
            client = OpenAI(api_key=api_key)
            model = model or os.getenv("OPENAI_MODEL", OPENAI_DEFAULT_MODEL)

            if len(main_text) <= OPENAI_MAX_CHARS:
                print(f"  Generating main content ({len(main_text)} chars)...")
                with client.audio.speech.with_streaming_response.create(
                    model=model,
                    voice=main_voice,
                    input=main_text,
                    response_format="mp3",
                ) as response:
                    response.stream_to_file(main_path)
            else:
                chunks = chunk_text(main_text, OPENAI_MAX_CHARS)
                print(f"  Generating main content in {len(chunks)} chunks...")
                _generate_chunked_openai(client, chunks, main_path, main_voice, model)
        else:
            from elevenlabs.client import ElevenLabs
            api_key = os.getenv("ELEVENLABS_API_KEY")
            if not api_key:
                raise ValueError("ELEVENLABS_API_KEY not set in environment")
            client = ElevenLabs(api_key=api_key)
            model = model or os.getenv("MODEL_ID", ELEVENLABS_DEFAULT_MODEL)

            if len(main_text) <= ELEVENLABS_MAX_CHARS:
                print(f"  Generating main content ({len(main_text)} chars)...")
                audio = client.text_to_speech.convert(
                    text=main_text,
                    voice_id=main_voice,
                    model_id=model,
                    output_format="mp3_44100_128",
                )
                with open(main_path, "wb") as f:
                    for chunk in audio:
                        f.write(chunk)
            else:
                chunks = chunk_text(main_text, ELEVENLABS_MAX_CHARS)
                print(f"  Generating main content in {len(chunks)} chunks...")
                _generate_chunked(client, chunks, main_path, main_voice, model, "elevenlabs")

        # 4. Concatenate all three parts
        audio_files = [intro_path, silence_path, main_path]
        _concatenate_audio(audio_files, output_path, tmpdir)

    print(f"  Saved to: {output_path}")
    return output_path
