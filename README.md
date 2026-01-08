<p align="center">
  <img src="logo.png" alt="AI-Generated Podcast" width="200">
</p>

## AI-Generated Podcast

Generates podcast audio from blog posts using Claude Code for orchestration and text cleanup, with OpenAI/ElevenLabs for TTS.

**RSS feed:** https://dbirks.github.io/ai-generated-podcast/rss.xml

**Pocket Casts:** https://pocketcasts.com/podcast/ai-generated-podcast/c01659c0-6821-013d-bd77-02e325935ba3

## How It Works

1. Paste a blog URL into Claude Code and ask for a new episode
2. Claude Code scrapes the article, cleans up language if needed, generates TTS audio
3. Audio uploads to Azure Blob Storage, episode metadata goes into `episodes.yaml`
4. `feedgen` generates `rss.xml` from `episodes.yaml`
5. GitHub Actions deploys to GitHub Pages on push

The whole flow runs locally via Claude Code - just paste a link and ask for an episode.

## Setup

```bash
uv sync
cp .env.example .env
# Edit .env with your API keys
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes* | OpenAI API key for TTS |
| `ELEVENLABS_API_KEY` | Yes* | ElevenLabs API key for TTS |
| `AZURE_STORAGE_CONNECTION_STRING` | Yes | Azure Blob Storage connection |
| `OPENAI_VOICE` | No | OpenAI voice (default: `cedar`) |
| `OPENAI_MODEL` | No | OpenAI model (default: `gpt-4o-mini-tts`) |
| `VOICE_ID` | No | ElevenLabs voice ID |
| `MODEL_ID` | No | ElevenLabs model ID |

*At least one TTS provider key required

## OpenAI TTS Models

| Model | Voices | Notes |
|-------|--------|-------|
| `tts-1` | alloy, ash, coral, echo, fable, nova, onyx, sage, shimmer | Older, basic TTS. $15/1M chars |
| `tts-1-hd` | same as tts-1 | Higher quality. $30/1M chars |
| `gpt-4o-mini-tts` | all above + **cedar**, **marin** | Newer (March 2025), supports tone instructions, best quality |

Cedar and marin are the newest, most natural-sounding voices - only available on `gpt-4o-mini-tts`.

## CLI Usage

```bash
# Scrape article text from URL (works for most blogs, not Medium)
uv run main.py scrape https://example.com/post

# Generate audio (OpenAI TTS by default)
uv run main.py tts temp/article.txt -o temp/episode.mp3
uv run main.py tts temp/article.txt -o temp/episode.mp3 -p elevenlabs  # Use ElevenLabs
uv run main.py tts temp/article.txt -o temp/episode.mp3 -v alloy       # Different voice

# Upload to Azure
uv run main.py upload temp/episode.mp3 --name "Episode Title.m4a"

# Manage feed
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
  author: Author Name
  article_date: "2024-10-08"
  tech: Claude, OpenAI TTS (cedar)
  description: |
    Episode description here.
    Can be multiline.
```

Then run `uv run main.py feed` to regenerate the RSS feed.

## Architecture

- `main.py` - Typer CLI
- `scraper.py` - Article extraction from URLs (uses readability)
- `cleaner.py` - Claude Agent SDK text cleaning
- `tts.py` - OpenAI/ElevenLabs TTS (auto-chunks long text)
- `storage.py` - Azure Blob Storage upload
- `feed.py` - RSS feed generation (feedgen library)
- `episodes.yaml` - Episode data

## Notes

- Medium and similar sites block curl (Cloudflare); use Wayback Machine or manually copy article text
- OpenAI TTS chunks at 4k chars, ElevenLabs at 10k chars - handled automatically
- Files are MP3 but uploaded with `.m4a` extension for podcast app compatibility
- For Medium articles, try: `https://web.archive.org/web/<url>`
