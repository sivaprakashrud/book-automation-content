import requests
import time
import random
from typing import List, Dict
from bs4 import BeautifulSoup

import json

BOOK_SOURCES = [
    "https://www.googleapis.com/books/v1/volumes?q=subject:self-help&maxResults=10",
    "https://openlibrary.org/subjects/self-help.json?limit=10",
    "https://gutendex.com/books?topic=self-help",
    "https://api.nytimes.com/svc/books/v3/lists/current/self-help.json?api-key=YOUR_API_KEY"  # Optional
]


MAX_DESCRIPTION_LENGTH = 2000  # Safe description limit

def fetch_books_from_source(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("books", []) if isinstance(data, dict) else data
    except Exception as e:
        print(f"[Error] Failed to fetch from {url}: {e}")
        return []

def clean_book(book):
    try:
        title = book.get("title", "Untitled")
        authors = book.get("authors", ["Unknown"])
        description = book.get("description", "")
        if len(description) > MAX_DESCRIPTION_LENGTH:
            description = description[:MAX_DESCRIPTION_LENGTH] + "..."
        return {"title": title, "authors": authors, "description": description}
    except Exception as e:
        print(f"[Warning] Skipped book due to error: {e}")
        return None

def fetch_all_books():
    all_books = []
    seen_titles = set()

    print("Fetching books from multiple sources...")

    for url in BOOK_SOURCES:
        print(f"🔗 Fetching from: {url}")
        books = fetch_books_from_source(url)
        for book in books:
            cleaned = clean_book(book)
            if cleaned and cleaned["title"] not in seen_titles:
                all_books.append(cleaned)
                seen_titles.add(cleaned["title"])

    print(f"✅ Total books fetched: {len(all_books)}")
    with open("books.json", "w", encoding="utf-8") as f:
        json.dump(all_books, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    fetch_all_books()
