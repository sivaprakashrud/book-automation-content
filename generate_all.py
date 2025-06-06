import requests
import json

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
                    description = item.get("description", {})
                    if isinstance(description, dict):
                        description = description.get("value", "No description.")
                    elif not isinstance(description, str):
                        description = "No description."

                    book = {
                        "title": item.get("title", "Untitled"),
                        "authors": [a.get("name", "Unknown") for a in item.get("authors", [])],
                        "description": description
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


if __name__ == "__main__":
    print("[INFO] Starting script...")
    books = fetch_books("self-help")

    for idx, book in enumerate(books):
        try:
            print(f"[INFO] Processing Book {idx+1}: {book['title']}")
            print(f"  Title: {book['title']}")
            print(f"  Author(s): {', '.join(book['authors'])}")
            print(f"  Description: {book['description'][:150]}...\n")
        except Exception as e:
            print(f"[ERROR] Failed to process book {idx+1}: {e}")
