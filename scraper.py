"""Blog article scraper for podcast generation."""

import re
import sys
from html import unescape
from urllib.request import urlopen, Request

from lxml import html
from readability import Document


def fetch_url(url: str) -> str:
    """Fetch URL content with a browser-like user agent."""
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8")


def html_to_text(html_content: str) -> str:
    """Convert HTML to plain text, preserving paragraph breaks."""
    # Parse HTML
    tree = html.fromstring(html_content)

    # Remove script and style elements
    for elem in tree.xpath("//script | //style"):
        elem.getparent().remove(elem)

    # Get text with paragraph breaks
    lines = []
    for elem in tree.iter():
        if elem.tag in ("p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "blockquote"):
            text = elem.text_content().strip()
            if text:
                lines.append(text)
                lines.append("")  # blank line after paragraphs

    text = "\n".join(lines)

    # Clean up whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = unescape(text)

    return text.strip()


def extract_metadata(raw_html: str) -> dict:
    """Extract title, author, date from HTML meta tags."""
    tree = html.fromstring(raw_html)

    metadata = {}

    # Title
    og_title = tree.xpath('//meta[@property="og:title"]/@content')
    if og_title:
        metadata["title"] = og_title[0]
    else:
        title = tree.xpath("//title/text()")
        if title:
            metadata["title"] = title[0].strip()

    # Author
    author = tree.xpath('//meta[@name="author"]/@content')
    if author:
        metadata["author"] = author[0]

    # Date (try various common patterns)
    for attr in ["article:published_time", "og:updated_time", "datePublished"]:
        date = tree.xpath(f'//meta[@property="{attr}"]/@content')
        if date:
            # Extract just the date part (YYYY-MM-DD)
            match = re.search(r"(\d{4}-\d{2}-\d{2})", date[0])
            if match:
                metadata["date"] = match.group(1)
                break

    return metadata


def scrape_article(url: str) -> tuple[str, dict]:
    """Scrape article text and metadata from URL.

    Returns (article_text, metadata_dict)
    """
    raw_html = fetch_url(url)

    # Extract main content with readability
    doc = Document(raw_html)
    content_html = doc.summary()

    # Convert to plain text
    text = html_to_text(content_html)

    # Get metadata
    metadata = extract_metadata(raw_html)
    if "title" not in metadata:
        metadata["title"] = doc.title()

    return text, metadata


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run scraper.py <url> [output.txt]")
        sys.exit(1)

    url = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"Fetching: {url}")
    text, metadata = scrape_article(url)

    print(f"\nMetadata:")
    for key, value in metadata.items():
        print(f"  {key}: {value}")

    print(f"\nArticle length: {len(text)} characters")

    if output_file:
        # Prepend title to text
        title = metadata.get("title", "Untitled")
        full_text = f"{title}\n\n{text}"

        with open(output_file, "w") as f:
            f.write(full_text)
        print(f"Saved to: {output_file}")
    else:
        print(f"\nPreview (first 500 chars):\n{text[:500]}...")
