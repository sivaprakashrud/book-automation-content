import cohere
import os
import json

COHERE_API_KEY = os.getenv("COHERE_API_KEY") or "your-valid-cohere-api-key"
SUMMARY_PATH = "data/summaries.json"

def summarize_books(book_list):
    co = cohere.Client(COHERE_API_KEY)
    summaries = []

    for book in book_list:
        title = book.get("title", "Untitled")
        description = book.get("description", "")
        if not description:
            print(f"[WARN] No content to summarize for: {title}")
            continue

        try:
            response = co.summarize(text=description, format="paragraph", length="medium")
            summary_text = response.summary

            summaries.append({
                "title": title,
                "summary": summary_text
            })

        except Exception as e:
            print(f"Error summarizing '{title}': {e}")

    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(summaries, f, indent=2, ensure_ascii=False)

    print(f"[INFO] Saved {len(summaries)} summaries to {SUMMARY_PATH}")
    return summaries
