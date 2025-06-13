import os
import json
import cohere

# ————————————————
# Configuration
# ————————————————
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
if not COHERE_API_KEY:
    raise RuntimeError("Missing COHERE_API_KEY in env")

co = cohere.Client(COHERE_API_KEY)

DATA_DIR      = "data"
BOOK_PATH     = os.path.join(DATA_DIR, "books.json")
SUMMARY_PATH  = os.path.join(DATA_DIR, "summaries.json")

# ————————————————
# Helpers
# ————————————————
def split_text_into_parts(text, num_parts=5, min_len=250):
    text = text.strip()
    if len(text) < min_len:
        return []
    part_size = max(len(text) // num_parts, min_len)
    parts = [text[i*part_size:(i+1)*part_size] for i in range(num_parts)]
    # Merge leftovers so every chunk ≥ min_len
    merged, buffer = [], ""
    for p in parts:
        buffer += p
        if len(buffer) >= min_len:
            merged.append(buffer)
            buffer = ""
    if buffer:
        merged.append(buffer)
    return merged

def summarize_text(text):
    """Call Cohere.summarize and catch anything that goes wrong."""
    try:
        result = co.summarize(
            text=text,
            model="summarize-xlarge",
            length="medium",
            format="bullet",
            extractiveness="high"
        )
        return result.summary
    except Exception as e:
        print(f"[WARN] Cohere summarization failed: {e}")
        return None

# ————————————————
# Main
# ————————————————
def summarize_books():
    if not os.path.exists(BOOK_PATH):
        print(f"[ERROR] {BOOK_PATH} not found. Run fetch_books.py first.")
        return

    with open(BOOK_PATH, "r", encoding="utf-8") as f:
        books = json.load(f)

    all_summaries = []
    for book in books:
        title     = book.get("title", "Untitled")
        full_text = book.get("full_text", "")
        print(f"[INFO] Summarizing '{title}'")

        parts = split_text_into_parts(full_text)
        if not parts:
            print(f"[WARN] Skipping '{title}'—text too short.")
            continue

        summaries = []
        for idx, chunk in enumerate(parts, 1):
            summary = summarize_text(chunk)
            if summary:
                summaries.append(summary)
        if summaries:
            all_summaries.append({
                "title":     title,
                "authors":   book.get("authors", []),
                "summaries": summaries
            })

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(all_summaries, f, indent=4, ensure_ascii=False)

    print(f"[INFO] Wrote {len(all_summaries)} entries to {SUMMARY_PATH}")

if __name__ == "__main__":
    summarize_books()
