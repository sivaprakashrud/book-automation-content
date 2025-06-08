import os
import json
import requests

DATA_DIR = "data"
BOOK_PATH = os.path.join(DATA_DIR, "books.json")

def fetch_from_openlibrary(query="productivity"):
    url = f"https://openlibrary.org/search.json?q={query}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print("[ERROR] Failed to fetch from OpenLibrary")
            return []
        data = response.json()
        books = []
        for doc in data.get("docs", [])[:5]:  # Limit to 5 books
            books.append({
                "title": doc.get("title"),
                "author": ", ".join(doc.get("author_name", [])),
                "content": f"Summary placeholder for '{doc.get('title')}' by {doc.get('author_name', [''])[0]}"
            })
        return books
    except Exception as e:
        print(f"[ERROR] OpenLibrary error: {e}")
        return []

def fetch_from_google_books(query="productivity"):
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print("[ERROR] Failed to fetch from Google Books")
            return []
        data = response.json()
        books = []
        for item in data.get("items", [])[:5]:  # Limit to 5 books
            volume_info = item.get("volumeInfo", {})
            books.append({
                "title": volume_info.get("title"),
                "author": ", ".join(volume_info.get("authors", [])),
                "content": volume_info.get("description", "No description available.")
            })
        return books
    except Exception as e:
        print(f"[ERROR] Google Books error: {e}")
        return []

def save_books_to_file(book_list):
    os.makedirs(DATA_DIR, exist_ok=True)
    try:
        with open(BOOK_PATH, "w", encoding="utf-8") as f:
            json.dump(book_list, f, indent=4, ensure_ascii=False)
        print(f"[INFO] Saved {len(book_list)} books to {BOOK_PATH}")
    except Exception as e:
        print(f"[ERROR] Failed to save books to file: {e}")

def fetch_books():
    print("[INFO] Fetching books...")
    all_books = []
    all_books.extend(fetch_from_openlibrary())
    all_books.extend(fetch_from_google_books())
    save_books_to_file(all_books)

if __name__ == "__main__":
    fetch_books()
