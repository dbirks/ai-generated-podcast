"""RSS feed generation from episodes.yaml."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from feedgen.feed import FeedGenerator
from ruamel.yaml import YAML


# Hardcoded config (personal project)
GITHUB_PAGES_URL = "https://dbirks.github.io/ai-generated-podcast"
BLOB_BASE_URL = "https://birkspublic.blob.core.windows.net/aigeneratedpodcast"
PODCAST_TITLE = "AI-generated podcast"
PODCAST_DESCRIPTION = "My personal podcast feed for some topics I want to learn more about."


@dataclass
class Episode:
    title: str
    published_date: datetime
    description: str
    blog_url: str | None = None
    was_edited: bool = False
    author: str | None = None
    article_date: str | None = None
    tech: str | None = None


def load_episodes(path: Path = Path("episodes.yaml")) -> list[Episode]:
    """Load episodes from YAML file."""
    yaml = YAML()
    with open(path) as f:
        data = yaml.load(f)

    episodes = []
    for item in data:
        pub_date = item["published_date"]
        if isinstance(pub_date, str):
            pub_date = datetime.fromisoformat(pub_date)

        episodes.append(Episode(
            title=item["title"],
            published_date=pub_date,
            description=item["description"].strip(),
            blog_url=item.get("blog_url"),
            was_edited=item.get("was_edited", False),
            author=item.get("author"),
            article_date=item.get("article_date"),
            tech=item.get("tech"),
        ))

    return episodes


def save_episodes(episodes: list[Episode], path: Path = Path("episodes.yaml")):
    """Save episodes to YAML file."""
    yaml = YAML()
    yaml.default_flow_style = False

    data = []
    for ep in episodes:
        item = {
            "title": ep.title,
            "published_date": ep.published_date.isoformat(),
            "blog_url": ep.blog_url,
            "was_edited": ep.was_edited,
            "author": ep.author,
            "article_date": ep.article_date,
            "tech": ep.tech,
            "description": ep.description + "\n",  # literal block style
        }
        data.append(item)

    with open(path, "w") as f:
        yaml.dump(data, f)


def add_episode(episode: Episode, path: Path = Path("episodes.yaml")):
    """Add a new episode to the YAML file."""
    episodes = load_episodes(path)
    episodes.append(episode)
    save_episodes(episodes, path)


def format_description(episode: Episode) -> str:
    """Format episode description with metadata."""
    lines = [episode.description]

    has_metadata = episode.author or episode.article_date or episode.blog_url or episode.tech
    if has_metadata:
        lines.append("")  # blank line before metadata

    if episode.author:
        lines.append(f"Author: {episode.author}")
    if episode.article_date:
        lines.append(f"Date: {episode.article_date}")
    if episode.tech:
        lines.append(f"Tech: {episode.tech}")
    if episode.blog_url:
        lines.append(f"Original: {episode.blog_url}")

    return "\n".join(lines)


def generate_feed(episodes: list[Episode] | None = None) -> str:
    """Generate RSS feed XML string."""
    if episodes is None:
        episodes = load_episodes()

    fg = FeedGenerator()
    fg.load_extension("podcast")
    fg.podcast.itunes_category("Technology", "Podcasting")
    fg.link(href=GITHUB_PAGES_URL, rel="alternate")
    fg.title(PODCAST_TITLE)
    fg.description(PODCAST_DESCRIPTION)

    # Podcast artwork
    logo_url = f"{GITHUB_PAGES_URL}/logo.png"
    fg.image(url=logo_url, title=PODCAST_TITLE, link=GITHUB_PAGES_URL)
    fg.podcast.itunes_image(logo_url)

    for episode in episodes:
        url = f"{BLOB_BASE_URL}/{episode.title}.m4a"

        fe = fg.add_entry()
        fe.id(url)
        fe.title(episode.title)
        fe.description(format_description(episode))
        fe.enclosure(url, 0, "audio/mp4")
        fe.published(episode.published_date)

    return fg.rss_str(pretty=True).decode("utf-8")


def write_feed(output_path: Path = Path("rss.xml")):
    """Generate and write RSS feed to file."""
    rss_content = generate_feed()
    output_path.write_text(rss_content)
    return rss_content
