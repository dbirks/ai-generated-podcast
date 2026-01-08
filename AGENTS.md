# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI-generated podcast feed generator. Converts blog posts to audio using Claude (text cleanup) and ElevenLabs (TTS), uploads to Azure Blob Storage, and generates an RSS feed for GitHub Pages.

## Architecture

```
main.py       - Typer CLI entry point
cleaner.py    - Claude Agent SDK text cleaning
tts.py        - ElevenLabs audio generation
storage.py    - Azure Blob Storage upload
feed.py       - RSS feed generation from episodes.yaml
episodes.yaml - Episode data (YAML with literal blocks)
```

## Development Commands

```bash
uv sync                                          # Install dependencies
uv run main.py --help                            # Show CLI help
uv run main.py feed                              # Generate RSS feed
uv run main.py list                              # List episodes
uv run main.py episode "Title" -t post.txt       # Full pipeline
```

## Adding Episodes

1. Add entry to `episodes.yaml`
2. Run `uv run main.py feed` to regenerate RSS

## Deployment

GitHub Actions runs `uv run main.py feed` on push to main, then deploys to GitHub Pages.

## External URLs

- Feed: https://dbirks.github.io/ai-generated-podcast/rss.xml
- Audio: https://birkspublic.blob.core.windows.net/aigeneratedpodcast/
