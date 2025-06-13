import os
import json
import time
import cohere

# ————————————————
# Configuration
# ————————————————
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
if not COHERE_API_KEY:
    raise RuntimeError("[ERROR] Missing COHERE_API_KEY environment variable!")
co = cohere.Client(COHERE_API_KEY)

DATA_DIR     = "data"
BOOK_PATH    = os.path.join(DATA_DIR, "books.json")
SUMMARY_PATH = os.path.join(DATA_DIR, "summaries.json")

# ————————————————
# Helpers
# ————————————————
def split_text_into_parts(text, num_parts=5, min_len=250):
    """Return a list of ≥min_len chunks, up to num_parts, merging small remainders."""
    text = text.strip()
    if len(text) < min_len:
        return []
    part_size = max(len(text)//num_parts, min_len)
    raw = [text[i*part_size:(i+1)*part_size] for i in range(num_parts)]
    merged, buff = [], ""
    for chunk in raw:
        buff += chunk
        if len(buff) >= min_len:
            merged.append(buff)
            buff = ""
    if buff:
        merged.append(buff)
    return merged

def summarize_chunk(chunk, max_retries=3):
    """Call Cohere.summarize(), retry on 429, catch everything."""
    for attempt in range(1, max_retries+1):
        try:
            r = co.summarize(
                text=chunk,
                model="summarize-xlarge",
                length="medium",
                format="bullets",       # must be "paragraph" or "bullets"
                extractiveness="high"
            )
            return r.summary
        except Exception as e:
            msg = str(e)
            if "429" in msg and attempt < max_retries:
                wait = 5 * attempt
                print(f"[WARN] Rate-limit hit. Sleeping {wait}s (retry {attempt})")
                time.sleep(wait)
                continue
            print(f"[WARN] Summarization failed: {msg}")
            return None
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

    results = []
    for book in books:
        title = book.get("title", "Untitled")
        text  = book.get("full_text", "").strip()
        print(f"[INFO] Summarizing '{title}' ({len(text)} chars)")

        parts = split_text_into_parts(text)
        if not parts:
            print(f"[WARN] Skipping '{title}'—text too short.")
            continue

        bullets = []
        for idx, chunk in enumerate(parts, 1):
            summary = summarize_chunk(chunk)
            if summary:
                bullets.append(summary)
            else:
                print(f"[WARN] Chunk {idx} for '{title}' failed.")

        if bullets:
            results.append({
                "title":     title,
                "authors":   book.get("authors", []),
                "summaries": bullets
            })

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"[INFO] Wrote {len(results)} summarized books to {SUMMARY_PATH}")

if __name__ == "__main__":
    summarize_books()
