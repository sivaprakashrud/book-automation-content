import requests
import time
import random
import json
from typing import List, Dict
from bs4 import BeautifulSoup

BOOK_SOURCES = [
    "https://www.googleapis.com/books/v1/volumes?q=subject:self-help&maxResults=5",
    "https://openlibrary.org/subjects/self-help.json?limit=5",
    "https://gutendex.com/books?topic=self-help"
]

def clean_google_book(item):
    volume = item.get("volumeInfo", {})
    return {
        "title": volume.get("title", "No Title"),
        "authors": volume.get("authors", ["Unknown Author"]),
        "description": volume.get("description", "No description available.")
    }

def clean_openlibrary_book(item):
    return {
        "title": item.get("title", "No Title"),
        "authors": [author.get("name") for author in item.get("authors", []) if author.get("name")],
        "description": "No description available."  # OpenLibrary subject API doesn't include full desc
    }

def clean_gutendex_book(item):
    return {
        "title": item.get("title", "No Title"),
        "authors": [author.get("name") for author in item.get("authors", []) if author.get("name")],
        "description": "No description available."  # Gutendex doesn't provide desc in this endpoint
    }

def fetch_books(category):
    print(f"[INFO] Fetching books in category: {category}")
    all_books = []

    for url in BOOK_SOURCES:
        try:
            print(f"[INFO] Fetching from: {url}")
            response = requests.get(url)
            data = response.json()
            books = data.get("books", []) if "books" in data else data  # support different formats
            all_books.extend(books)
        except Exception as e:
            print(f"[ERROR] Could not fetch from {url}: {e}")

    return all_books

if __name__ == "__main__":
    books = fetch_books()
    print(f"\n✅ Total books fetched: {len(books)}\n")
    for idx, book in enumerate(all_books):
        try:
            title = book.get("title", "Untitled")
            authors = ", ".join(book.get("authors", [])) if isinstance(book.get("authors"), list) else str(book.get("authors", "Unknown"))
            desc_raw = book.get("description", "")
            if isinstance(desc_raw, dict):
                description = desc_raw.get("value", "")
            elif isinstance(desc_raw, str):
                description = desc_raw
            else:
                description = ""

    
            # Sanitize overly long descriptions
            if len(description) > 1000:
                description = description[:1000] + "..."
    
            print(f"[INFO] Processing Book {idx + 1}: {title}")
            print(f"   Authors: {authors}")
            print(f"   Description: {description}\n")
    
            # Add your own processing here (summarize, voiceover, etc.)
    
        except Exception as e:
            print(f"[ERROR] Failed to process book {idx + 1}: {book}")
            print(f"Reason: {e}")

 
