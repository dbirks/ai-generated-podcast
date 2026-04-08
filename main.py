#!/usr/bin/env python3
"""
AI-Generated Podcast CLI

Usage:
    uv run main.py episode "Title" --url https://... --text post.txt
    uv run main.py clean post.txt
    uv run main.py tts cleaned.txt -o episode.m4a
    uv run main.py upload episode.m4a
    uv run main.py feed
"""

from datetime import datetime
from pathlib import Path

import typer
from rich import print as rprint

from cleaner import clean_file_sync, CleanResult
from feed import Episode, add_episode, load_episodes, write_feed, BLOB_BASE_URL
from storage import upload_blob
from tts import generate_audio, generate_audio_with_intro

app = typer.Typer(help="AI-Generated Podcast CLI")


def build_intro(blog_url: str | None, was_edited: bool) -> str:
    """Build the intro text for the podcast episode."""
    parts = []

    if blog_url:
        parts.append(f"This episode is based on a blog post available at {blog_url}.")

    if was_edited:
        parts.append("The text has been lightly edited for language.")

    parts.append("This audio was generated using ElevenLabs text-to-speech and Claude AI for content preparation.")

    return " ".join(parts) + "\n\n"


@app.command()
def episode(
    title: str = typer.Argument(..., help="Episode title"),
    text_file: Path = typer.Option(..., "--text", "-t", help="Path to blog post text file"),
    url: str | None = typer.Option(None, "--url", "-u", help="URL of original blog post"),
    model: str = typer.Option("sonnet", "--model", "-m", help="Claude model for cleaning"),
    skip_clean: bool = typer.Option(False, "--skip-clean", help="Skip profanity cleaning"),
    skip_upload: bool = typer.Option(False, "--skip-upload", help="Skip Azure upload"),
):
    """Full pipeline: clean text, generate audio, upload, add to feed."""
    import shutil
    import tempfile

    rprint(f"[bold]Creating episode:[/bold] {title}")

    # Read text
    text = text_file.read_text()
    rprint(f"  Read {len(text)} characters from {text_file}")

    # Clean text
    was_edited = False
    if not skip_clean:
        rprint("\n[bold]Cleaning text with Claude...[/bold]")
        # Copy to temp file for cleaning
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
            tmp.write(text)
            tmp_path = Path(tmp.name)

        result: CleanResult = clean_file_sync(tmp_path, model=model)
        text = tmp_path.read_text()  # Read the cleaned version
        was_edited = result.was_edited
        if was_edited:
            rprint(f"  Edited: {result.changes_made}")
        else:
            rprint("  No changes needed")
        tmp_path.unlink()  # Clean up temp file

    # Add intro
    intro = build_intro(url, was_edited)
    full_text = intro + text

    # Generate audio
    rprint("\n[bold]Generating audio with ElevenLabs...[/bold]")
    audio_path = Path(f"{title}.m4a")
    generate_audio(full_text, audio_path)

    # Upload to Azure
    if not skip_upload:
        rprint("\n[bold]Uploading to Azure...[/bold]")
        blob_url = upload_blob(audio_path, f"{title}.m4a")
    else:
        blob_url = f"{BLOB_BASE_URL}/{title}.m4a"
        rprint(f"\n[yellow]Skipped upload. Expected URL: {blob_url}[/yellow]")

    # Add to episodes.yaml
    rprint("\n[bold]Adding episode to feed...[/bold]")
    ep = Episode(
        title=title,
        published_date=datetime.now().astimezone(),
        description=f"Based on a blog post. {'Lightly edited for language. ' if was_edited else ''}Generated with ElevenLabs and Claude AI.",
        blog_url=url,
        was_edited=was_edited,
    )
    add_episode(ep)

    # Regenerate feed
    rprint("\n[bold]Regenerating RSS feed...[/bold]")
    write_feed()

    rprint(f"\n[green bold]Done![/green bold] Episode '{title}' created.")
    rprint(f"  Audio: {blob_url}")
    rprint(f"  Feed updated: rss.xml")


@app.command()
def clean(
    text_file: Path = typer.Argument(..., help="Path to text file to clean"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Output file (default: edit in place)"),
    model: str = typer.Option("sonnet", "--model", "-m", help="Claude model to use"),
):
    """Clean profanity from text using Claude (edits file in place)."""
    import shutil

    # Determine target file
    if output:
        shutil.copy(text_file, output)
        target = output
        rprint(f"Copied {text_file} → {output}")
    else:
        target = text_file

    text = target.read_text()
    rprint(f"Cleaning {len(text)} characters with Claude ({model})...")
    rprint("[dim]Claude will use Edit tool for surgical changes...[/dim]")

    result = clean_file_sync(target, model=model)

    if result.was_edited:
        rprint(f"[yellow]Edited:[/yellow]")
        for change in result.changes_made:
            rprint(f"  - {change}")
    else:
        rprint("[green]No changes needed[/green]")

    rprint(f"[green]File updated: {target}[/green]")


@app.command()
def tts(
    text_file: Path = typer.Argument(..., help="Path to text file"),
    output: Path = typer.Option(..., "--output", "-o", help="Output audio file path"),
    provider: str = typer.Option("openai", "--provider", "-p", help="TTS provider: openai or elevenlabs"),
    voice: str | None = typer.Option(None, "--voice", "-v", help="Voice ID (provider-specific)"),
    intro: str | None = typer.Option(None, "--intro", help="Intro text (uses Marin voice + pause before main content)"),
    pause: float = typer.Option(2.0, "--pause", help="Seconds of silence after intro (default: 2.0)"),
    intro_voice: str = typer.Option("marin", "--intro-voice", help="Voice for intro (default: marin)"),
    main_voice: str = typer.Option("cedar", "--main-voice", help="Voice for main content when using --intro (default: cedar)"),
):
    """Generate audio from text using OpenAI or ElevenLabs TTS."""
    text = text_file.read_text()
    rprint(f"Generating audio from {len(text)} characters with {provider}...")

    if intro:
        # Use multi-voice workflow with intro
        rprint(f"[bold]Using intro mode:[/bold] {intro_voice} (intro) + {pause}s pause + {main_voice} (main)")
        generate_audio_with_intro(
            intro_text=intro,
            main_text=text,
            output_path=output,
            provider=provider,
            intro_voice=intro_voice,
            main_voice=main_voice,
            pause_duration=pause,
        )
    else:
        # Standard single-voice workflow
        generate_audio(text, output, provider=provider, voice=voice)

    rprint(f"[green]Saved to: {output}[/green]")


@app.command()
def upload(
    file: Path = typer.Argument(..., help="File to upload"),
    blob_name: str | None = typer.Option(None, "--name", "-n", help="Blob name (default: filename)"),
):
    """Upload a file to Azure Blob Storage."""
    url = upload_blob(file, blob_name)
    rprint(f"[green]Uploaded:[/green] {url}")


@app.command()
def feed():
    """Generate RSS feed from episodes.yaml."""
    episodes = load_episodes()
    rprint(f"Generating feed with {len(episodes)} episodes...")

    content = write_feed()
    rprint("[green]Saved: rss.xml[/green]")

    # Print first few lines
    lines = content.split("\n")[:10]
    for line in lines:
        print(line)
    print("...")


@app.command("list")
def list_episodes():
    """List all episodes in the feed."""
    episodes = load_episodes()

    rprint(f"[bold]{len(episodes)} episodes:[/bold]\n")
    for i, ep in enumerate(episodes, 1):
        rprint(f"  {i}. [bold]{ep.title}[/bold]")
        rprint(f"     {ep.published_date.strftime('%Y-%m-%d %H:%M')}")
        if ep.blog_url:
            rprint(f"     {ep.blog_url}")
        rprint()


@app.command()
def scrape(
    url: str = typer.Argument(..., help="URL to scrape"),
    output: Path = typer.Option(None, "--output", "-o", help="Output file (default: temp/<slug>.txt)"),
):
    """Scrape article text from a URL (works for most blogs, not Medium)."""
    from scraper import scrape_article
    import re

    rprint(f"Fetching: {url}")
    text, metadata = scrape_article(url)

    rprint(f"\n[bold]Metadata:[/bold]")
    for key, value in metadata.items():
        rprint(f"  {key}: {value}")

    rprint(f"\nArticle length: {len(text)} characters")

    # Determine output path
    if not output:
        # Create slug from title or URL
        title = metadata.get("title", url.split("/")[-1])
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:50]
        output = Path(f"temp/{slug}.txt")
        output.parent.mkdir(exist_ok=True)

    # Prepend title
    title = metadata.get("title", "Untitled")
    full_text = f"{title}\n\n{text}"

    output.write_text(full_text)
    rprint(f"\n[green]Saved to: {output}[/green]")

    # Print metadata for easy copy to episodes.yaml
    rprint(f"\n[bold]For episodes.yaml:[/bold]")
    rprint(f"  blog_url: {url}")
    if "author" in metadata:
        rprint(f"  author: {metadata['author']}")
    if "date" in metadata:
        rprint(f"  article_date: \"{metadata['date']}\"")


@app.command()
def verify():
    """Verify all episode audio URLs are reachable (HTTP 200)."""
    import urllib.request
    from urllib.parse import quote

    episodes = load_episodes()
    rprint(f"Verifying audio URLs for {len(episodes)} episodes...\n")

    errors = []
    for ep in episodes:
        # Reproduce the same URL logic as feed.py
        if ep.audio_file:
            encoded_filename = quote(ep.audio_file)
        else:
            blob_filename = ep.title
            for prefix in ["[Blog] ", "[NotebookLM] ", "[Document] ", "[Tidbit] ", "[Short] ", "[Thread] "]:
                if blob_filename.startswith(prefix):
                    blob_filename = blob_filename[len(prefix):]
                    break
            encoded_filename = quote(f"{blob_filename}.m4a")

        url = f"{BLOB_BASE_URL}/{encoded_filename}"

        try:
            req = urllib.request.Request(url, method="HEAD")
            resp = urllib.request.urlopen(req, timeout=10)
            status = resp.status
        except Exception as e:
            status = getattr(e, "code", str(e))

        if status == 200:
            rprint(f"  [green]OK[/green]  {ep.title}")
        else:
            rprint(f"  [red]FAIL ({status})[/red]  {ep.title}")
            rprint(f"       URL: {url}")
            errors.append((ep.title, url, status))

    rprint()
    if errors:
        rprint(f"[red bold]{len(errors)} broken URL(s)![/red bold]")
        for title, url, status in errors:
            rprint(f"  - {title}: {status}")
        raise typer.Exit(code=1)
    else:
        rprint(f"[green bold]All {len(episodes)} URLs OK[/green bold]")


@app.command("fix-content-types")
def fix_content_types():
    """Detect actual audio codec of each blob and set correct content-type."""
    import os
    import subprocess
    import tempfile
    from urllib.parse import quote
    from azure.storage.blob import BlobServiceClient, ContentSettings
    from dotenv import load_dotenv

    load_dotenv()
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not connection_string:
        raise typer.Exit("AZURE_STORAGE_CONNECTION_STRING not set")

    blob_service = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service.get_container_client("aigeneratedpodcast")

    episodes = load_episodes()
    rprint(f"Detecting codec and fixing content-type for {len(episodes)} blobs...\n")

    fixed = 0
    for ep in episodes:
        if ep.audio_file:
            blob_name = ep.audio_file
        else:
            blob_name = ep.title
            for prefix in ["[Blog] ", "[NotebookLM] ", "[Document] ", "[Tidbit] ", "[Short] ", "[Thread] ", "[PDF] "]:
                if blob_name.startswith(prefix):
                    blob_name = blob_name[len(prefix):]
                    break
            blob_name = f"{blob_name}.m4a"

        blob_client = container_client.get_blob_client(blob_name)
        try:
            # Download first 64KB to detect codec
            stream = blob_client.download_blob(offset=0, length=65536)
            header_bytes = stream.readall()

            # Probe with ffprobe
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "stream=codec_name",
                 "-of", "csv=p=0", "-"],
                input=header_bytes, capture_output=True, timeout=10,
            )
            codec = result.stdout.decode().strip().split("\n")[0]

            if codec == "mp3":
                correct_type = "audio/mpeg"
            elif codec in ("aac", "alac"):
                correct_type = "audio/x-m4a"
            else:
                correct_type = "audio/mpeg"  # default to mpeg for safety

            props = blob_client.get_blob_properties()
            current = props.content_settings.content_type
            if current != correct_type:
                blob_client.set_http_headers(ContentSettings(content_type=correct_type))
                rprint(f"  [yellow]Fixed[/yellow] {blob_name}: codec={codec}, {current} → {correct_type}")
                fixed += 1
            else:
                rprint(f"  [green]OK[/green]    {blob_name} (codec={codec}, {current})")
        except Exception as e:
            rprint(f"  [red]ERROR[/red] {blob_name}: {e}")

    rprint(f"\n[green bold]Done! Fixed {fixed} blob(s)[/green bold]")


if __name__ == "__main__":
    app()
