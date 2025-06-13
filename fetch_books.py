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

def fetch_from_openlibrary(niche="productivity", max_results=5):
    """Fetch full books from OpenLibrary based on user-defined niche."""
    print(f"[INFO] Fetching books related to '{niche}' from OpenLibrary...")
    books = []
    search_url = f"https://openlibrary.org/search.json?q={niche}&limit={max_results}"
    
    try:
        response = requests.get(search_url)
        response.raise_for_status()
        data = response.json()

        for item in data.get("docs", []):
            work_id = item.get("key", "").replace("/works/", "")
            if not work_id:
                continue

            # Fetch full book details
            book_url = f"https://openlibrary.org/works/{work_id}.json"
            book_response = requests.get(book_url)
            book_response.raise_for_status()
            book_data = book_response.json()

            # Handle description format (string vs dictionary)
            full_text_data = book_data.get("description", "No full text available.")
            full_text = full_text_data.get("value", "No full text available.") if isinstance(full_text_data, dict) else full_text_data

            books.append({
                "title": item.get("title", "Unknown Title"),
                "authors": item.get("author_name", ["Unknown"]),
                "full_text": full_text,
                "source": "OpenLibrary"
            })
        return books
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] OpenLibrary error: {e}")
        return []

def fetch_from_gutenberg(niche="productivity", max_results=5):
    """Fetch full books from Project Gutenberg based on user-defined niche."""
    print(f"[INFO] Fetching books related to '{niche}' from Project Gutenberg...")
    books = []
    search_url = f"https://gutendex.com/books/?search={niche}&limit={max_results}"

    try:
        response = requests.get(search_url)
        response.raise_for_status()
        data = response.json()

        for item in data.get("results", []):
            book_id = item.get("id")
            title = item.get("title", "Unknown Title")
            authors = [author["name"] for author in item.get("authors", [])]

            # Fetch full book text
            book_url = f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt"
            book_response = requests.get(book_url)
            if book_response.status_code == 200:
                full_text = book_response.text
            else:
                full_text = "No full text available."

            books.append({
                "title": title,
                "authors": authors,
                "full_text": full_text,
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

def fetch_books(niche="productivity"):
    """Fetch books from multiple sources based on the selected niche."""
    print(f"[INFO] Fetching books for niche: '{niche}'...")
    all_books = []
    all_books.extend(fetch_from_openlibrary(niche))
    all_books.extend(fetch_from_gutenberg(niche))
    save_books_to_file(all_books)

if __name__ == "__main__":
    # Change the niche here (e.g., "science", "fiction", "psychology", etc.)
    fetch_books(niche="productivity")
