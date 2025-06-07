import os
import json
import requests
import os
import json

# Sample data to simulate successful book fetching
sample_books = [
    {
        "title": "Atomic Habits",
        "author": "James Clear",
        "content": "Atomic Habits is a guide on how to build good habits and break bad ones...",
    },
    {
        "title": "Deep Work",
        "author": "Cal Newport",
        "content": "Deep Work teaches you how to focus without distraction on cognitively demanding tasks...",
    },
]

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

# Save the sample data to books.json
books_file_path = "data/books.json"
with open(books_file_path, "w", encoding="utf-8") as f:
    json.dump(sample_books, f, indent=4, ensure_ascii=False)

books_file_path  # Return path for confirmation

# Save the fetched books to local file
def save_books_to_file(book_list, filename="data/books.json"):
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(book_list, f, indent=4, ensure_ascii=False)
        print(f"[INFO] Saved {len(book_list)} books to {filename}")
    except Exception as e:
        print(f"[ERROR] Failed to save books to file: {e}")

# Fetch from OpenLibrary
def fetch_from_openlibrary():
    print("[INFO] Fetching from OpenLibrary...")
    books = []
    try:
        for subject in ["productivity", "self-help"]:
            response = requests.get(f"https://openlibrary.org/subjects/{subject}.json?limit=10")
            data = response.json()
            for item in data.get("works", []):
                books.append({
                    "title": item.get("title"),
                    "author": item.get("authors", [{}])[0].get("name", "Unknown"),
                    "source": "OpenLibrary"
                })
    except Exception as e:
        print(f"[ERROR] Failed fetching from OpenLibrary: {e}")
    return books

# Fetch from Google Books (no API key required)
def fetch_from_google_books():
    print("[INFO] Fetching from Google Books...")
    books = []
    try:
        for keyword in ["productivity", "self-help"]:
            response = requests.get(f"https://www.googleapis.com/books/v1/volumes?q={keyword}&maxResults=10")
            data = response.json()
            for item in data.get("items", []):
                volume_info = item.get("volumeInfo", {})
                books.append({
                    "title": volume_info.get("title"),
                    "author": ", ".join(volume_info.get("authors", ["Unknown"])),
                    "source": "GoogleBooks"
                })
    except Exception as e:
        print(f"[ERROR] Failed fetching from Google Books: {e}")
    return books

# Master function to fetch all books
def fetch_books():
    all_books = []
    all_books.extend(fetch_from_openlibrary())
    all_books.extend(fetch_from_google_books())
    save_books_to_file(all_books)

# Run the script
if __name__ == "__main__":
    fetch_books()
