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

## Lessons Learned

### ElevenLabs Character Limit
ElevenLabs API has a 10,000 character limit per request. `tts.py` automatically chunks long texts at paragraph/sentence boundaries and concatenates with ffmpeg.

### Profanity Cleaning
The `cleaner.py` uses claude-agent-sdk but the spawned agent doesn't reliably make file edits. For now, do profanity edits manually with the Edit tool. Light-touch rules:
- `ass` → `butt`
- `shit` → `stuff` / `squat` / `nada`
- `hell` → `heck`
- `damn` → `darn`
- `F***` → remove/reword
- Keep: `fart`, `crap`, other mild words

### Fetching Blog Content
Medium and similar sites block curl (Cloudflare). Either use browser devtools MCP or manually copy the article text.

### Audio Format
Files are MP3 but uploaded with `.m4a` extension for podcast app compatibility.

### Full Episode Workflow
```bash
# 1. Get article text into temp/article.txt (manual or browser MCP)
# 2. Clean profanity (manual Edit tool for now)
# 3. Generate audio
uv run main.py tts temp/article_clean.txt -o "temp/Episode Title.mp3"
# 4. Test locally
mpv "temp/Episode Title.mp3"
# 5. Upload and add to feed
uv run main.py upload "temp/Episode Title.mp3" --name "Episode Title.m4a"
# 6. Edit episodes.yaml, then regenerate feed
uv run main.py feed
# 7. Push to deploy
git push origin main
```
