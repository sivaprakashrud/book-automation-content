import os
from fetch_books import fetch_books_to_csv
from summarize_books import summarize_books_from_csv
from text_to_audio import text_to_audio
from create_video import create_video
import csv

# Set up folders
os.makedirs("voices", exist_ok=True)
os.makedirs("videos", exist_ok=True)

# Step 1: Fetch books and save to books.csv
print("📚 Fetching books...")
fetch_books_to_csv()

# Step 2: Summarize using Cohere API
print("🧠 Summarizing books...")
summarize_books_from_csv()

# Step 3–5: Convert to audio + create video
with open("summaries.csv", newline='', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for idx, row in enumerate(reader, 1):
        title = row["title"]
        summary = row["summary"]
        
        print(f"\n🎤 [{idx}] Converting '{title}' to voice...")
        audio_path = f"voices/{title[:50].replace(' ', '_')}.mp3"
        text_to_audio(summary, audio_path)

        print(f"🎞️  Generating video for '{title}'...")
        video_path = f"videos/{title[:50].replace(' ', '_')}.mp4"
        create_video(summary, audio_path, video_path)

print("\n✅ All videos generated in the 'videos/' folder.")
