import cohere
import csv
import os
import time

# Set your Cohere API key here or in your environment
COHERE_API_KEY = os.getenv("COHERE_API_KEY", "your-cohere-api-key")
co = cohere.Client(COHERE_API_KEY)

INPUT_FILE = "books.csv"
OUTPUT_FILE = "summaries.csv"

def summarize_book(title):
    prompt = f"Summarize the book titled '{title}' in 200 words. Focus on the key ideas, lessons, and insights that are practically useful."

    try:
        response = co.generate(
            model='command-nightly',  # Best for summarization
            prompt=prompt,
            max_tokens=500,
            temperature=0.7,
        )
        return response.generations[0].text.strip()
    except Exception as e:
        print(f"[ERROR] Failed to summarize {title}: {e}")
        return None

def summarize_books_from_csv():
    if not os.path.exists(INPUT_FILE):
        print(f"[ERROR] Input file '{INPUT_FILE}' not found.")
        return

    with open(INPUT_FILE, newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        books = [row["title"] for row in reader if "title" in row]

    with open(OUTPUT_FILE, "w", newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(["title", "summary"])

        for i, title in enumerate(books, 1):
            print(f"[{i}] Summarizing: {title}")
            summary = summarize_book(title)
            if summary:
                writer.writerow([title, summary])
            time.sleep(1)  # To avoid API rate limits

    print(f"\n✅ Summaries saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    summarize_books_from_csv()
