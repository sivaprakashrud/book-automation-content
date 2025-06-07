import requests
import json
import os

def fetch_from_openlibrary(subject="productivity", limit=5):
    url = f"https://openlibrary.org/subjects/{subject}.json?limit={limit}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        books = []
        for book in data.get("works", []):
            books.append({
                "title": book.get("title", "Untitled"),
                "author": book.get("authors", [{}])[0].get("name", "Unknown Author"),
                "source": "openlibrary"
            })
        return books
    except Exception as e:
        print(f"[ERROR] Failed to fetch from OpenLibrary: {e}")
        return []

def fetch_from_google_books(query="productivity", limit=5):
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults={limit}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        books = []
        for item in data.get("items", []):
            volume = item.get("volumeInfo", {})
            books.append({
                "title": volume.get("title", "Untitled"),
                "author": ", ".join(volume.get("authors", ["Unknown Author"])),
                "source": "google_books"
            })
        return books
    except Exception as e:
        print(f"[ERROR] Failed to fetch from Google Books: {e}")
        return []

import os
import json
from your_module import fetch_from_openlibrary, fetch_from_google_books  # replace with your actual import paths

def save_books_to_file(book_list, filename="data/books.json"):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(book_list, f, indent=4, ensure_ascii=False)
        print(f"[INFO] Saved {len(book_list)} books to {filename}")
    except Exception as e:
        print(f"[ERROR] Failed to save books to file: {e}")

def fetch_books():
    all_books = []
    all_books.extend(fetch_from_openlibrary())
    all_books.extend(fetch_from_google_books())
    save_books_to_file(all_books, filename="data/books.json")

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    fetch_books()
