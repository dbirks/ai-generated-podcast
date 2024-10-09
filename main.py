from feedgen.feed import FeedGenerator


def main():

    fg = FeedGenerator()

    fg.load_extension('podcast')
    fg.podcast.itunes_category('Technology', 'Podcasting')
    fg.link(href='http://example.com', rel='alternate')
    fg.title("AI-generated podcast")
    fg.description("My personal podcast feed for some topics I want to learn more about.")
    fg.rss_str(pretty=True)




    fe = fg.add_entry()
    fe.id('http://lernfunk.de/media/654321/1/file.mp3')
    fe.title('The First Episode')
    fe.description('Enjoy our first episode.')
    fe.enclosure('http://lernfunk.de/media/654321/1/file.mp3', 0, 'audio/mpeg')
    fg.rss_file('rss.xml')


if __name__ == "__main__":
    main()
