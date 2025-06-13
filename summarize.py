import os
import json
import cohere
import subprocess
import sys

try:
    import cohere
except ModuleNotFoundError:
    print("[WARN] 'cohere' module not found. Installing...")
    subprocess.run([sys.executable, "-m", "pip", "install", "cohere"], check=True)
    import cohere  # ✅ Retry import after installation
    
# File Paths
BOOK_PATH = "data/books.json"
SUMMARY_PATH = "data/summaries.json"

# ✅ Cohere API Key (Replace with actual key or set env var)
COHERE_API_KEY = os.getenv("COHERE_API_KEY", "your_actual_cohere_api_key")

def summarize_books():
    """Summarize book descriptions using Cohere API."""
    if not os.path.exists(BOOK_PATH):
        print(f"[ERROR] Book file not found at: {BOOK_PATH}")
        return []

    with open(BOOK_PATH, "r", encoding="utf-8") as f:
        books = json.load(f)

    co = cohere.Client(COHERE_API_KEY)
    summaries = []

    for book in books:
        title = book.get("title", "Untitled")
        text = book.get("description") or book.get("text") or ""

        if not text:
            print(f"[WARN] No content to summarize for: {title}")
            continue

        try:
            response = co.summarize(text=text, length="short", format="paragraph")
            summary_text = response.summary if response.summary else "No summary available."

            summaries.append({
                "title": title,
                "summary": summary_text
            })
            print(f"[INFO] Summary generated for: {title}")
        except Exception as e:
            print(f"[ERROR] Summarization failed for {title}: {e}")

    os.makedirs("data", exist_ok=True)
    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(summaries, f, indent=4, ensure_ascii=False)
    
    print(f"[INFO] Saved {len(summaries)} summaries to {SUMMARY_PATH}")
    return summaries

if __name__ == "__main__":
    summarize_books()
