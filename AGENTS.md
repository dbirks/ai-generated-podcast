# AGENTS.md

Instructions for Claude Code when working with this repository.

## Quick Episode Workflow

When user pastes a blog URL, follow these steps:

```bash
# 1. Scrape article (works for most sites, not Medium)
uv run main.py scrape https://example.com/post

# 2. Check for profanity (f-word, s-word, d-word - NOT fart/ass/crap)
grep -i -E "fuck|shit|damn|bitch|bastard" temp/article.txt

# 3. If profanity found, manually edit with Edit tool:
#    fuck -> freaking, shit -> stuff, damn -> darn, etc.

# 4. Generate TTS (auto-chunks, uses cedar voice by default)
uv run main.py tts temp/article.txt -o "temp/Episode Title.mp3"

# 5. Upload to Azure
uv run main.py upload "temp/Episode Title.mp3" --name "Episode Title.m4a"

# 6. Add to episodes.yaml (scrape command prints metadata)
# 7. Regenerate feed and push
uv run main.py feed && git add -A && git commit -m "Add Episode Title" && git push
```

## Medium Articles (Cloudflare blocked)

Medium blocks curl. Use Wayback Machine:
```bash
curl -sL "https://web.archive.org/web/https://medium.com/..." -o /tmp/article.html
uv run python3 -c "from scraper import ...; # extract with readability"
```

Or ask user to paste text manually.

## TTS Providers

**OpenAI (default):**
- Model: `gpt-4o-mini-tts` (newest, best quality)
- Voice: `cedar` (newest, most natural)
- Other voices: marin, nova, alloy, ash, coral, echo, fable, onyx, sage, shimmer
- Chunks at 4k chars, auto-concatenates with ffmpeg

**ElevenLabs (fallback):**
- Use `-p elevenlabs` flag
- Chunks at 10k chars
- Quota-based, can run out

## Profanity Rules

Light touch - only edit strong profanity:
- fuck/fucking -> freaking
- shit -> stuff
- shitbag -> jerk
- damn/damnedest -> darn/darndest
- bitch/bastard -> jerk

Keep these (mild): fart, ass, crap, hell

## Architecture

```
main.py       - Typer CLI (scrape, tts, upload, feed, list)
scraper.py    - Article extraction with readability-lxml
tts.py        - OpenAI/ElevenLabs TTS with auto-chunking
storage.py    - Azure Blob Storage upload
feed.py       - RSS generation with feedgen (iTunes/Spotify compatible)
episodes.yaml - Episode metadata
```

## Episode Schema

```yaml
- title: Episode Title
  published_date: "2026-01-08T12:00:00-05:00"
  blog_url: https://example.com/post
  was_edited: false  # true if profanity cleaned
  author: Author Name
  article_date: "2026-01-08"
  tech: Claude, OpenAI TTS (cedar)
  description: |
    2-4 line summary of the episode content.
```

## Deployment

GitHub Actions on push to main:
1. `uv run main.py feed` generates rss.xml
2. Uploads only rss.xml, logo.png, index.html to Pages (not temp/)
3. ~30s deploy time

## Batch Processing

When processing multiple articles, use parallel Task agents:
- Scrape all articles in parallel
- Check profanity in parallel
- Run TTS in parallel background agents
- Upload to Azure in parallel
- Add all to episodes.yaml at once

This lets the user queue work while processing continues.

## External URLs

- RSS: https://dbirks.github.io/ai-generated-podcast/rss.xml
- Audio: https://birkspublic.blob.core.windows.net/aigeneratedpodcast/
- Spotify: https://open.spotify.com/show/7ChYkvtx2lftMXIaouaIKN
