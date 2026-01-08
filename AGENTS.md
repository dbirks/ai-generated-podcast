# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI-generated podcast RSS feed generator. The repository generates an RSS/podcast feed from a Python script and hosts it via GitHub Pages. Audio files are stored in Azure Blob Storage, and the feed is deployed automatically on every push to main.

## Architecture

- **main.py**: Core feed generation script using `feedgen` library. Contains hardcoded episode list with titles, descriptions, and publication dates. Outputs `rss.xml`.
- **index.html**: Simple static page served via GitHub Pages.
- **GitHub Actions**: Automated deployment pipeline (`.github/workflows/static.yml`) that runs `main.py` to generate the RSS feed and deploys everything to GitHub Pages.
- **Episode storage**: Audio files (`.m4a` format) are stored in Azure Blob Storage at `https://birkspublic.blob.core.windows.net/aigeneratedpodcast/`

## Development Commands

### Setup
```bash
uv sync  # Install dependencies using uv package manager
```

### Running the Generator
```bash
source .venv/bin/activate
python main.py
```
This generates `rss.xml` and prints the feed content to stdout.

### Python Version
The project requires Python 3.12+ (specified in `pyproject.toml` and `.python-version`).

## Adding New Episodes

1. Add a new episode dictionary to the `episodes` list in `main.py`:
   ```python
   {
       "title": "Episode Title",
       "description": "Episode description",
       "published_date": "2024-10-09T00:41:54-04:00",  # Eastern Time format
   }
   ```
2. The episode filename is derived from the title with `.m4a` extension
3. Ensure the corresponding `.m4a` file exists in Azure Blob Storage at: `{episode_base_url}/{title}.m4a`
4. Publish dates use Eastern Time (UTC-4/UTC-5) in ISO 8601 format

## Deployment

The GitHub Actions workflow automatically:
1. Checks out the code
2. Installs `uv` and dependencies
3. Runs `main.py` to generate `rss.xml`
4. Deploys all files to GitHub Pages

No manual deployment is needed - just push to `main`.

## External URLs

- GitHub Pages base: `https://dbirks.github.io/ai-generated-podcast`
- Azure Blob Storage: `https://birkspublic.blob.core.windows.net/aigeneratedpodcast`
