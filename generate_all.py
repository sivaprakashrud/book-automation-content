# generate_all.py
import os
from fetch_books import fetch_books_from_gutenberg
from summarize import summarize_book
from text_to_speech import text_to_audio
from video_generator import create_video

for folder in ['voices', 'videos', 'assets']:
    os.makedirs(folder, exist_ok=True)


# Ensure output folders exist
os.makedirs("summaries", exist_ok=True)
os.makedirs("voices", exist_ok=True)
os.makedirs("videos", exist_ok=True)

# 1. Fetch Books
titles = get_books_from_goodreads("self-help")
print(f"Fetched {len(titles)} books")

for i, title in enumerate(titles):
    try:
        print(f"\nProcessing Book {i+1}: {title}")

        # 2. Summarize
        summary = summarize_book(title)
        with open(f"summaries/{i+1}_{title[:30]}.txt", "w", encoding="utf-8") as f:
            f.write(summary)

        # 3. Text to Speech
        audio_path = f"voices/{i+1}_{title[:30]}.mp3"
        text_to_audio(summary, audio_path)

        # 4. Create Video
        video_path = f"videos/{i+1}_{title[:30]}.mp4"
        create_video(summary, audio_path, video_path)

        print(f"Done with {title}")

    except Exception as e:
        print(f"Error with {title}: {e}")
        continue
