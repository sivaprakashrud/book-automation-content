import requests
import time
import random
import json
from typing import List, Dict
from bs4 import BeautifulSoup
import requests
import csv
import os

BOOK_SOURCES = [
    "https://www.googleapis.com/books/v1/volumes?q=subject:self-help&maxResults=5",
    "https://openlibrary.org/subjects/self-help.json?limit=5",
    "https://gutendex.com/books?topic=self-help"
]

def fetch_books(category="self-help"):
    print(f"[INFO] Fetching books in category: {category}")
    all_books = []

    for url in BOOK_SOURCES:
        try:
            print(f"[INFO] Fetching from: {url}")
            response = requests.get(url)
            data = response.json()

            if "items" in data:  # Google Books
                for item in data["items"]:
                    book = {
                        "title": item["volumeInfo"].get("title", "Untitled"),
                        "authors": item["volumeInfo"].get("authors", []),
                        "description": item["volumeInfo"].get("description", "No description available")
                    }
                    all_books.append(book)

            elif "works" in data:  # OpenLibrary
                for work in data["works"]:
                    book = {
                        "title": work.get("title", "Untitled"),
                        "authors": [a["name"] for a in work.get("authors", []) if "name" in a],
                        "description": work.get("description", {}).get("value", "No description available") if isinstance(work.get("description"), dict) else work.get("description", "No description available")
                    }
                    all_books.append(book)

            elif "results" in data:  # Gutendex
                for result in data["results"]:
                    book = {
                        "title": result.get("title", "Untitled"),
                        "authors": [a["name"] for a in result.get("authors", [])],
                        "description": "No description available"
                    }
                    all_books.append(book)

        except Exception as e:
            print(f"[ERROR] Failed to process source {url}: {e}")

    print(f"[INFO] Fetched {len(all_books)} books")
    return all_books


