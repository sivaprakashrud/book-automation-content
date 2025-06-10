import os
import json
import cohere

BOOK_PATH = "data/books.json"
SUMMARY_PATH = "data/summaries.json"
COHERE_API_KEY = os.getenv("COHERE_API_KEY", "your_actual_cohere_api_key")  # Replace with valid key or set env var

def summarize_books(books):
    if not os.path.exists(BOOK_PATH):
        print(f"[ERROR] Book file not found at: {BOOK_PATH}")
        return []

    with open(BOOK_PATH, "r", encoding="utf-8") as f:
        books = json.load(f)

    co = cohere.Client(COHERE_API_KEY)
    summaries = []

    for book in books:
        text = book.get("description") or book.get("text") or ""
        if not text:
            print(f"[WARN] No content to summarize for: {book.get('title', 'Unknown')}")
            continue

        try:
            response = co.summarize(text=text, length='short', format='paragraph')
            summary_text = response.summary
            summaries.append({
                "title": book.get("title", "Untitled"),
                "summary": summary_text
            })
            print(f"[INFO] Summary generated for: {book.get('title')}")
        except Exception as e:
            print(f"[ERROR] Summarization failed for {book.get('title', 'Unknown')}: {e}")

    os.makedirs("data", exist_ok=True)
    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(summaries, f, indent=4, ensure_ascii=False)
    print(f"[INFO] Saved {len(summaries)} summaries to {SUMMARY_PATH}")
    
    return summaries
