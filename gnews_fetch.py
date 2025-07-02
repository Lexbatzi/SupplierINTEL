def gnews_articles(name: str, days: int = 90):
    """
    Return a Feedparser 'entries' list of headlines that mention `name`
    within the last `days` days, nudged to packaging/can industry.
    """
    query = f'"{name}" packaging OR cans when:{days}d'
    url   = (
        "https://news.google.com/rss/search?"
        f"q={requests.utils.quote(query)}&hl=en-US&gl=US&ceid=US:en"
    )
    return feedparser.parse(url)["entries"]
