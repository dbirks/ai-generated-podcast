#!/usr/bin/env python3
"""
Helper script to add a new episode to episodes.yaml
Used by GitHub Actions automation.
"""

import yaml
import sys
from datetime import datetime, timezone
from pathlib import Path


def add_episode(
    title: str,
    blog_url: str,
    author: str,
    article_date: str,
    description: str,
    was_edited: bool = False,
    tech: str = "Claude, OpenAI TTS (cedar)",
):
    """Add a new episode to episodes.yaml"""

    episodes_file = Path("episodes.yaml")

    # Load existing episodes
    if episodes_file.exists():
        with open(episodes_file, 'r') as f:
            episodes = yaml.safe_load(f) or []
    else:
        episodes = []

    # Create new episode entry
    # Use EST timezone (America/New_York)
    published_date = datetime.now(timezone.utc).astimezone()

    new_episode = {
        'title': title,
        'published_date': published_date.isoformat(),
        'blog_url': blog_url,
        'was_edited': was_edited,
        'author': author,
        'article_date': article_date,
        'tech': tech,
        'description': description.strip(),
    }

    # Add to beginning of list (newest first)
    episodes.insert(0, new_episode)

    # Write back to file
    with open(episodes_file, 'w') as f:
        yaml.dump(episodes, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    print(f"✓ Added episode: {title}")
    print(f"  Published: {published_date.isoformat()}")
    print(f"  Blog URL: {blog_url}")
    return True


def main():
    if len(sys.argv) < 6:
        print("Usage: add_episode.py <title> <blog_url> <author> <article_date> <description> [was_edited] [tech]")
        print("\nExample:")
        print('  add_episode.py "My Episode" "https://blog.com/post" "John Doe" "2026-01-13" "Description here"')
        sys.exit(1)

    title = sys.argv[1]
    blog_url = sys.argv[2]
    author = sys.argv[3]
    article_date = sys.argv[4]
    description = sys.argv[5]
    was_edited = sys.argv[6].lower() == 'true' if len(sys.argv) > 6 else False
    tech = sys.argv[7] if len(sys.argv) > 7 else "Claude, OpenAI TTS (cedar)"

    add_episode(
        title=title,
        blog_url=blog_url,
        author=author,
        article_date=article_date,
        description=description,
        was_edited=was_edited,
        tech=tech,
    )


if __name__ == "__main__":
    main()
