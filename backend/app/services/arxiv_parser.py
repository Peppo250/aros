import feedparser
from typing import cast

def parse_arxiv(xml_text: str):

    feed = feedparser.parse(xml_text)

    papers = []

    for entry in feed.entries:

        authors = ", ".join(
            cast(str, author.name)
            for author in entry.authors
        )


        pdf_url = ""

        for link in entry.links:
            if link.type == "application/pdf":
                pdf_url = link.href
                break

        papers.append({
            "title": entry.title,
            "authors": authors,
            "abstract": entry.summary,
            "pdf_url": pdf_url,
            "source": "arxiv"
        })

    return papers