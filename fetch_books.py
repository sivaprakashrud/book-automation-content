import os
import subprocess
import json

# ————————————————
# Ensure `requests` is installed before import
# ————————————————
try:
    import requests
except ImportError:
    print("[WARN] `requests` not found. Installing now…")
    subprocess.run(["pip", "install", "requests"], check=True)
    import requests

# ————————————————
# Paths
# ————————————————
DATA_DIR  = "data"
BOOK_PATH = os.path.join(DATA_DIR, "books.json")


def fetch_from_openlibrary(niche="productivity", max_results=5):
    """Fetch full-text books from OpenLibrary by niche."""
    print(f"[INFO] OpenLibrary: Searching for '{niche}' (max {max_results})")
    books = []
    url = f"https://openlibrary.org/search.json?q={niche}&limit={max_results}"
    try:
        r = requests.get(url)
        r.raise_for_status()
        hits = r.json().get("docs", [])
        for doc in hits:
            work_key = doc.get("key", "")
            if not work_key.startswith("/works/"):
                continue
            work_id = work_key.split("/works/")[-1]
            detail_url = f"https://openlibrary.org/works/{work_id}.json"

            dr = requests.get(detail_url)
            dr.raise_for_status()
            data = dr.json()

            desc = data.get("description", "No full text available.")
            if isinstance(desc, dict):
                desc = desc.get("value", "No full text available.")

            books.append({
                "title":     doc.get("title", "Unknown Title"),
                "authors":   doc.get("author_name", ["Unknown"]),
                "full_text": desc,
                "source":    "OpenLibrary"
            })
    except requests.RequestException as e:
        print(f"[ERROR] OpenLibrary fetch failed: {e}")
    return books


def fetch_from_gutenberg(niche="productivity", max_results=5):
    """Fetch full-text books from Gutendex (Project Gutenberg) by niche."""
    print(f"[INFO] Gutenberg: Searching for '{niche}' (max {max_results})")
    books = []
    url = f"https://gutendex.com/books/?search={niche}&limit={max_results}"
    try:
        r = requests.get(url)
        r.raise_for_status()
        for item in r.json().get("results", []):
            book_id = item.get("id")
            title   = item.get("title", "Unknown Title")
            authors = [a.get("name", "Unknown") for a in item.get("authors", [])]

            txt_url = f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt"
            tr = requests.get(txt_url)
            full_text = tr.text if tr.status_code == 200 else "No full text available."

            books.append({
                "title":     title,
                "authors":   authors,
                "full_text": full_text,
                "source":    "Project Gutenberg"
            })
    except requests.RequestException as e:
        print(f"[ERROR] Gutenberg fetch failed: {e}")
    return books


def save_books_to_file(book_list):
    """Save the combined list of books to JSON."""
    os.makedirs(DATA_DIR, exist_ok=True)
    try:
        with open(BOOK_PATH, "w", encoding="utf-8") as f:
            json.dump(book_list, f, indent=2, ensure_ascii=False)
        print(f"[INFO] {len(book_list)} books saved to {BOOK_PATH}")
    except Exception as e:
        print(f"[ERROR] Could not write to {BOOK_PATH}: {e}")


def fetch_books(niche="productivity"):
    """Fetch from both sources and save to disk."""
    print(f"[INFO] Starting fetch for niche: '{niche}'")
    all_books = []
    all_books.extend(fetch_from_openlibrary(niche))
    all_books.extend(fetch_from_gutenberg(niche))
    save_books_to_file(all_books)


if __name__ == "__main__":
    # Quick sanity check: run with default niche
    fetch_books(niche="productivity")
