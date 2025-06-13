import os
import subprocess
import json
import requests

# Ensure `requests` is installed before proceeding
try:
    import requests
except ModuleNotFoundError:
    print("[WARN] `requests` module not found. Installing now...")
    subprocess.run(["pip", "install", "requests"], check=True)
    import requests  # ✅ Retry import after installation

DATA_DIR = "data"
BOOK_PATH = os.path.join(DATA_DIR, "books.json")

def fetch_from_openlibrary(query="productivity", max_results=5):
    """Fetch books from OpenLibrary API (Free, No API Key)."""
    print("[INFO] Fetching from OpenLibrary...")
    books = []
    url = f"https://openlibrary.org/search.json?q={query}&limit={max_results}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        for item in data.get("docs", []):
            books.append({
                "title": item.get("title"),
                "authors": item.get("author_name", []),
                "description": item.get("first_sentence", ""),
                "text": item.get("first_sentence", ""),
                "source": "OpenLibrary"
            })
        return books
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] OpenLibrary error: {e}")
        return []

def fetch_from_gutenberg():
    """Fetch books from Project Gutenberg (Free, No API Key)."""
    print("[INFO] Fetching from Project Gutenberg...")
    books = []
    url = "https://www.gutenberg.org/cache/epub/feeds/rdf-files.tar.bz2"  # Public book list
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.text.split("\n")[:5]  # Simulated parsing (Gutenberg doesn't have JSON API)
        for line in data:
            books.append({
                "title": line.strip(),
                "authors": ["Unknown"],
                "description": "Classic book from Project Gutenberg.",
                "text": "Classic book from Project Gutenberg.",
                "source": "Project Gutenberg"
            })
        return books
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Project Gutenberg error: {e}")
        return []

def save_books_to_file(book_list):
    """Save fetched books to a JSON file."""
    os.makedirs(DATA_DIR, exist_ok=True)
    try:
        with open(BOOK_PATH, "w", encoding="utf-8") as f:
            json.dump(book_list, f, indent=4, ensure_ascii=False)
        print(f"[INFO] Saved {len(book_list)} books to {BOOK_PATH}")
    except Exception as e:
        print(f"[ERROR] Failed to save books to file: {e}")

def fetch_books():
    """Fetch books from multiple free sources and save them."""
    print("[INFO] Fetching books...")
    all_books = []
    all_books.extend(fetch_from_openlibrary())
    all_books.extend(fetch_from_gutenberg())
    all_books.extend(fetch_from_librarything())
    save_books_to_file(all_books)

if __name__ == "__main__":
    fetch_books()
