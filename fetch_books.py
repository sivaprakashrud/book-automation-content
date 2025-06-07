import os
import json
import requests

def fetch_from_openlibrary():
    print("[INFO] Fetching books from OpenLibrary...")
    books = []
    try:
        for subject in ["productivity", "self-help", "time management"]:
            url = f"https://openlibrary.org/subjects/{subject}.json?limit=5"
            res = requests.get(url)
            if res.status_code == 200:
                data = res.json()
                for work in data.get("works", []):
                    books.append({
                        "title": work.get("title", "No Title"),
                        "author": ", ".join(a.get("name") for a in work.get("authors", [])),
                        "source": "OpenLibrary"
                    })
            else:
                print(f"[WARN] Failed to fetch {subject} books: {res.status_code}")
    except Exception as e:
        print(f"[ERROR] OpenLibrary fetch failed: {e}")
    return books

def fetch_from_google_books():
    print("[INFO] Fetching books from Google Books...")
    books = []
    try:
        for query in ["productivity", "self improvement", "focus"]:
            url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=5"
            res = requests.get(url)
            if res.status_code == 200:
                data = res.json()
                for item in data.get("items", []):
                    info = item.get("volumeInfo", {})
                    books.append({
                        "title": info.get("title", "No Title"),
                        "author": ", ".join(info.get("authors", ["Unknown"])),
                        "source": "GoogleBooks"
                    })
            else:
                print(f"[WARN] Failed to fetch books from GoogleBooks: {res.status_code}")
    except Exception as e:
        print(f"[ERROR] Google Books fetch failed: {e}")
    return books

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
