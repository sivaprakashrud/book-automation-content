# generate_all.py
import json
from fetch_books import fetch_books
from summarize import summarize_text
from text_voice_generator import generate_text_script, generate_voice

print("[INFO] Starting script...")
books = fetch_books("self-help")

for i, book in enumerate(books):
    print(f"[INFO] Processing Book {i+1}: {book['title']}")
    book['summary'] = summarize_text(book['description'])
    script = generate_text_script(book)
    filename = f"book_{i+1}"
    voice_path = generate_voice(script, filename)
    book['voice_path'] = voice_path

# Save to JSON
os.makedirs("output", exist_ok=True)
with open("output/books.json", "w", encoding="utf-8") as f:
    json.dump(books, f, ensure_ascii=False, indent=4)

print("[INFO] All done. Output saved to output/books.json")
