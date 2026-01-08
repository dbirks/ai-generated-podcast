# AI-Generated Podcast

A Python script that generates an RSS podcast feed for AI-generated audio content.

## How it works

1. `main.py` generates an RSS feed from a hardcoded list of episodes
2. Audio files (.m4a) are hosted on Azure Blob Storage
3. GitHub Actions automatically deploys the feed to GitHub Pages on every push to main

## Setup

```bash
uv sync
source .venv/bin/activate
```

Create a `.env` file with your ElevenLabs API key:
```bash
cp .env.example .env
# Edit .env and add your ELEVENLABS_API_KEY
```

## Generate podcast audio from blog posts

```bash
python generate_podcast.py
```

Edit `generate_podcast.py` to customize:
- Blog post text and URL
- Profanity filtering (on by default)
- Voice and model settings

## Generate the RSS feed

```bash
python main.py
```

This creates `rss.xml` in the current directory.

## Adding episodes

Edit the `episodes` list in `main.py`:

```python
{
    "title": "Episode Title",
    "description": "Episode description",
    "published_date": "2024-10-09T00:41:54-04:00",  # Eastern Time, ISO 8601 format
}
```

The audio file must exist at:
`https://birkspublic.blob.core.windows.net/aigeneratedpodcast/{title}.m4a`

## Podcast format

Each episode includes:
- Link to the original blog post (when applicable)
- Note about any editing for language
- Information about AI models and tools used in generation

## Feed URL

https://dbirks.github.io/ai-generated-podcast/rss.xml
