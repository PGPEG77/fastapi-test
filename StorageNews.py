import os
import requests

NEWS_API_KEY = os.getenv("NEWS_API_KEY")


def get_news():
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": "energy storage",
        "sortBy": "publishedAt",
        "language": "en",
        "pageSize": 10,
        "apiKey": NEWS_API_KEY,
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data.get("status") != "ok":
        return []

    articles = []
    for a in data.get("articles", []):
        articles.append({
            "title": a.get("title"),
            "source": a.get("source", {}).get("name"),
            "description": a.get("description") or "Ingen beskrivning tillgänglig.",
            "url": a.get("url"),
            "published": a.get("publishedAt", "")[:10],
        })

    return articles