# AI-Generated Podcast

Generates podcast audio from blog posts using Claude for text cleanup and ElevenLabs for TTS.

**Listen:** [PocketCasts](https://pca.st/lle4pykv)

## Setup

```bash
uv sync
cp .env.example .env
# Edit .env with your API keys
```

## CLI Usage

```bash
# Full pipeline: clean text, generate audio, upload to Azure, update feed
uv run main.py episode "Episode Title" --text post.txt --url https://blog.com/post

# Individual commands
uv run main.py clean post.txt                    # Clean profanity with Claude
uv run main.py tts cleaned.txt -o episode.m4a   # Generate audio with ElevenLabs
uv run main.py upload episode.m4a               # Upload to Azure Blob Storage
uv run main.py feed                             # Regenerate RSS feed
uv run main.py list                             # List all episodes
```

## Adding Episodes

Edit `episodes.yaml`:

```yaml
- title: Episode Title
  published_date: "2024-10-09T00:41:54-04:00"
  blog_url: https://example.com/post
  was_edited: true
  description: |
    Episode description here.
    Can be multiline.
```

Then run `uv run main.py feed` to regenerate the RSS feed.

## Architecture

- `main.py` - Typer CLI
- `cleaner.py` - Claude Agent SDK text cleaning
- `tts.py` - ElevenLabs audio generation
- `storage.py` - Azure Blob Storage upload
- `feed.py` - RSS feed generation
- `episodes.yaml` - Episode data

## Feed URL

https://dbirks.github.io/ai-generated-podcast/rss.xml
