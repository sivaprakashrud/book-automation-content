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

def fetch_books(category):
    print(f"[INFO] Fetching books in category: {category}")
    all_books = []

    for url in BOOK_SOURCES:
        try:
            print(f"[INFO] Fetching from: {url}")
            response = requests.get(url)
            data = response.json()

            # Google Books API
            if "googleapis" in url:
                items = data.get("items", [])
                for item in items:
                    volume = item.get("volumeInfo", {})
                    book = {
                        "title": volume.get("title", "Untitled"),
                        "authors": volume.get("authors", ["Unknown"]),
                        "description": volume.get("description", "No description.")
                    }
                    all_books.append(book)

            # OpenLibrary API
            elif "openlibrary" in url:
                works = data.get("works", [])
                for item in works:
                    book = {
                        "title": item.get("title", "Untitled"),
                        "authors": [a.get("name", "Unknown") for a in item.get("authors", [])],
                        "description": item.get("description", {}).get("value") if isinstance(item.get("description"), dict) else item.get("description", "No description.")
                    }
                    all_books.append(book)

            # Gutendex API
            elif "gutendex" in url:
                results = data.get("results", [])
                for item in results:
                    book = {
                        "title": item.get("title", "Untitled"),
                        "authors": [a.get("name", "Unknown") for a in item.get("authors", [])],
                        "description": "No description."  # Gutendex doesn't provide one
                    }
                    all_books.append(book)

        except Exception as e:
            print(f"[ERROR] Failed to fetch from {url}: {e}")

    print(f"[INFO] Fetched {len(all_books)} books.")
    return all_books

# Create output directory if it doesn't exist
os.makedirs("output", exist_ok=True)

# Save to JSON
with open("output/books.json", "w", encoding="utf-8") as f:
    json.dump(books, f, ensure_ascii=False, indent=4)

# Save to CSV
csv_fields = ["title", "author", "description", "source"]
with open("output/books.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=csv_fields)
    writer.writeheader()
    for book in books:
        writer.writerow(book)

print("[INFO] Book data saved to output/books.json and output/books.csv")
