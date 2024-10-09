from feedgen.feed import FeedGenerator


def main():
    github_pages_base_url = "https://dbirks.github.io/ai-generated-podcast"
    episode_base_url = "https://birkspublic.blob.core.windows.net/aigeneratedpodcast"

    fg = FeedGenerator()

    fg.load_extension("podcast")
    fg.podcast.itunes_category("Technology", "Podcasting")
    fg.link(href=github_pages_base_url, rel="alternate")
    fg.title("AI-generated podcast")
    fg.description(
        "My personal podcast feed for some topics I want to learn more about."
    )
    fg.rss_str(pretty=True)

    episodes = [
        {
            "title": "TLS 1.3 Perfect Forward Secrecy",
            "description": "Using RFC 8446 and various blog articles to describe the concept of Perfect Forward Secrecy in TLS 1.3",
        },
    ]

    for episode in episodes:
        url = f"{episode_base_url}/{episode['title']}.m4a"
        title = episode["title"]
        description = episode["description"]

        fe = fg.add_entry()
        fe.id(url)
        fe.title(title)
        fe.description(description)
        fe.enclosure(url, 0, "audio/mp4")

    fg.rss_file("rss.xml")


if __name__ == "__main__":
    main()
