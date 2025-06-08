import os
import json
import cohere

# -------- SETTINGS --------
DATA_DIR = "data"
BOOK_PATH = os.path.join(DATA_DIR, "books.json")
SUMMARY_PATH = os.path.join(DATA_DIR, "summaries.json")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")  # You must set this in your GitHub Secrets or local env

# -------- HELPER FUNCTIONS --------
def load_books():
    if not os.path.exists(BOOK_PATH):
        raise FileNotFoundError(f"{BOOK_PATH} does not exist.")
    with open(BOOK_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def summarize_with_cohere(text):
    try:
        co = cohere.Client(COHERE_API_KEY)
        response = co.summarize(
            text=text,
            length="short",     # Ideal for Reels
            format="paragraph",
            model="command-light"
        )
        return response.summary
    except Exception as e:
        print(f"[ERROR] Cohere summarization failed: {e}")
        return "Summary could not be generated."

def generate_summaries(book_list):
    summaries = []
    for idx, book in enumerate(book_list):
        print(f"[INFO] Summarizing book {idx+1}: {book['title']}")
        summary = summarize_with_cohere(book.get("content", ""))
        summaries.append({
            "title": book["title"],
            "author": book.get("author", ""),
            "summary": summary
        })
    return summaries

def save_summaries(summaries):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(summaries, f, indent=4, ensure_ascii=False)
    print(f"[INFO] Saved {len(summaries)} summaries to {SUMMARY_PATH}")

# -------- MAIN --------
if __name__ == "__main__":
    books = load_books()
    summaries = generate_summaries(books)
    save_summaries(summaries)
