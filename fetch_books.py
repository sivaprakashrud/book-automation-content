import requests
import os
import json 

DATA_DIR = "data"
BOOK_PATH = os.path.join(DATA_DIR, "books.json")

def fetch_from_openlibrary(query="productivity", max_results=10):
    print("[INFO] Fetching from Google Books...")
    books = []
    url = f"https://openlibrary.org/search.json?q={query}&maxResults={max_results}"
    try:
        response = requests.get(url)
        data = response.json()
        for item in data.get("items", []):
            volume_info = item.get("volumeInfo", {})
            books.append({
                "title": volume_info.get("title"),
                "authors": volume_info.get("authors"),
                "description": volume_info.get("description", ""),  # ✅ Needed for summarization
                "text": volume_info.get("description", ""),         # ✅ Backup for summarizer
                "source": "openlibrary"
            })
        return books
    except Exception as e:
        print(f"[ERROR] OpenLibrary error: {e}")
        return []

def fetch_from_google_books(query="productivity", max_results=10):
    print("[INFO] Fetching from Google Books...")
    books = []
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults={max_results}"
    try:
        response = requests.get(url)
        data = response.json()
        for item in data.get("items", []):
            volume_info = item.get("volumeInfo", {})
            books.append({
                "title": volume_info.get("title"),
                "authors": volume_info.get("authors"),
                "description": volume_info.get("description", ""),  # ✅ Needed for summarization
                "text": volume_info.get("description", ""),         # ✅ Backup for summarizer
                "source": "Google Books"
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

