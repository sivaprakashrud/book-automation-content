import os
import json
from transformers import pipeline

# Load summarizer
summarizer = pipeline("summarization", model="t5-small", tokenizer="t5-small")

# Paths
BOOK_PATH = "data/books.json"
SUMMARY_DIR = "summaries"
os.makedirs(SUMMARY_DIR, exist_ok=True)

# Load books
with open(BOOK_PATH, "r", encoding="utf-8") as f:
    books = json.load(f)

# Summarize function
def summarize_text(text):
    trimmed = " ".join(text.split()[:500])
    result = summarizer(trimmed, max_length=200, min_length=50, do_sample=False)
    return result[0]['summary_text'].strip()

# Process books
for i, book in enumerate(books):
    try:
        title = book.get("title", f"Book_{i+1}")
        desc = book.get("description") or book.get("summary") or "No description"
        summary = summarize_text(desc)
        
        # Save summary
        filename = os.path.join(SUMMARY_DIR, f"{title[:50].replace('/', '-')}.txt")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(summary)
            
        print(f"[✔] Summary saved: {filename}")
    except Exception as e:
        print(f"[✘] Failed to process book {i+1}: {e}")
