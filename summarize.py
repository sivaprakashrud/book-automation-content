import os
import json
import requests
import cohere
import cohere
from cohere.error import CohereAPIError  # ✅ Correct import
        
# Ensure API key is set
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
if not COHERE_API_KEY:
    raise ValueError("[ERROR] Cohere API key is missing! Set COHERE_API_KEY as an environment variable.")

co = cohere.Client(COHERE_API_KEY)

DATA_DIR = "data"
BOOK_PATH = os.path.join(DATA_DIR, "books.json")
SUMMARY_PATH = os.path.join(DATA_DIR, "summaries.json")

def split_text_into_parts(text, num_parts=5):
    """Splits a book's full text into equal parts for better summarization."""
    text = text.strip()
    if len(text) < 250:
        return []  # Skip books with insufficient content

    part_size = len(text) // num_parts
    return [text[i * part_size : (i + 1) * part_size] for i in range(num_parts)]

def summarize_text(text):
    """Summarizes a given text using Cohere API."""
    try:
        response = co.summarize(
            text=text,
            model="summarize-xlarge",
            length="medium",
            format="bullet",
            extractiveness="high"
        )
        return response.summary
    except CohereAPIError as e:  # ✅ Use the correct exception
        print(f"[ERROR] Cohere API error: {e}")
        return None

def summarize_books():
    """Reads books.json, splits each book into 5 parts, and summarizes key points."""
    if not os.path.exists(BOOK_PATH):
        print("[ERROR] books.json not found! Run fetch_books.py first.")
        return

    with open(BOOK_PATH, "r", encoding="utf-8") as f:
        books = json.load(f)

    summaries = []
    for book in books:
        title = book.get("title", "Untitled")
        full_text = book.get("full_text", "").strip()

        if not full_text or len(full_text) < 250:
            print(f"[WARN] Skipping '{title}' – text too short ({len(full_text)} chars)")
            continue

        print(f"[INFO] Summarizing '{title}'...")
        parts = split_text_into_parts(full_text, num_parts=5)
        book_summaries = [summarize_text(part) for part in parts if part]

        summaries.append({
            "title": title,
            "authors": book.get("authors", ["Unknown"]),
            "summaries": book_summaries
        })

    # Save summaries to file
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(summaries, f, indent=4, ensure_ascii=False)

    print(f"[INFO] Saved {len(summaries)} summarized books to {SUMMARY_PATH}")

if __name__ == "__main__":
    summarize_books()
