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

from cleaner import clean_text_sync, CleanResult
from feed import Episode, add_episode, load_episodes, write_feed, BLOB_BASE_URL
from storage import upload_blob
from tts import generate_audio

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
    rprint(f"[bold]Creating episode:[/bold] {title}")

    # Read text
    text = text_file.read_text()
    rprint(f"  Read {len(text)} characters from {text_file}")

    # Clean text
    was_edited = False
    if not skip_clean:
        rprint("\n[bold]Cleaning text with Claude...[/bold]")
        result: CleanResult = clean_text_sync(text, model=model)
        text = result.cleaned_text
        was_edited = result.was_edited
        if was_edited:
            rprint(f"  Edited: {result.changes_made}")
        else:
            rprint("  No changes needed")

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
    output: Path | None = typer.Option(None, "--output", "-o", help="Output file (default: stdout)"),
    model: str = typer.Option("sonnet", "--model", "-m", help="Claude model to use"),
):
    """Clean profanity from text using Claude."""
    text = text_file.read_text()
    rprint(f"Cleaning {len(text)} characters with Claude ({model})...")

    result = clean_text_sync(text, model=model)

    if result.was_edited:
        rprint(f"[yellow]Edited:[/yellow] {result.changes_made}")
    else:
        rprint("[green]No changes needed[/green]")

    if output:
        output.write_text(result.cleaned_text)
        rprint(f"Saved to: {output}")
    else:
        print(result.cleaned_text)


@app.command()
def tts(
    text_file: Path = typer.Argument(..., help="Path to text file"),
    output: Path = typer.Option(..., "--output", "-o", help="Output audio file path"),
):
    """Generate audio from text using ElevenLabs."""
    text = text_file.read_text()
    rprint(f"Generating audio from {len(text)} characters...")

    generate_audio(text, output)
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


if __name__ == "__main__":
    app()
