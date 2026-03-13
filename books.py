import os
import requests

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "YOUR_API")

def search_books_google_smart(query_list, max_results=5, lang="ru"):
    books = []

    if not query_list:
        return []

    base_url = "https://www.googleapis.com/books/v1/volumes"

    for query in query_list:
        if not query or not query.strip():
            continue

        params = {
            "q": query,
            "maxResults": max_results,
            "printType": "books",
            "langRestrict": lang,
        }

        if GOOGLE_API_KEY and GOOGLE_API_KEY != "ээ":
            params["key"] = GOOGLE_API_KEY

        try:
            response = requests.get(base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException:
            continue
        except ValueError:
            continue

        items = data.get("items", [])
        if not items:
            continue

        for item in items:
            info = item.get("volumeInfo", {}) or {}
            title = info.get("title")
            if not title:
                continue

            books.append({
                "title": title,
                "authors": info.get("authors", []) or [],
                "description": info.get("description", "") or "",
                "thumbnail": (info.get("imageLinks") or {}).get("thumbnail"),
                "preview": info.get("previewLink"),
                "source": "Google Books",
            })

    unique = {b["title"]: b for b in books}
    return list(unique.values())

def shorten_link(url, max_len=60):
    if not url or not isinstance(url, str):
        return ""
    url = url.strip()
    return url if len(url) <= max_len else url[:max_len] + "..."

def get_books_for_profession_smart(profession, profession_to_topics, topic_to_queries):
    prof_key = profession.lower().strip()
    topics = profession_to_topics.get(prof_key, [])
    all_books = {}

    if not topics:
        return {}

    for topic in topics:
        queries = topic_to_queries.get(topic, [topic])
        books = search_books_google_smart(queries, max_results=5)
        all_books[topic] = books

    return all_books

