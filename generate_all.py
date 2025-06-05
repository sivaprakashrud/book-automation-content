# generate_all.py
import os
from fetch_books import fetch_books
from summarize import summarize_text
from text_to_speech import generate_voiceover
from video_generator import generate_video
from moviepy.video.VideoClip import TextClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip

for folder in ['voices', 'videos', 'assets']:
    os.makedirs(folder, exist_ok=True)


# Ensure output folders exist
os.makedirs("summaries", exist_ok=True)
os.makedirs("voices", exist_ok=True)
os.makedirs("videos", exist_ok=True)

# 1. Fetch Books
titles = fetch_books("productivity")
print(f"Fetched {len(titles)} books")
print("[INFO] Starting script...")

try:
    titles = fetch_books("self-help")
    print("[INFO] Fetched titles:", titles)
except Exception as e:
    print("[ERROR] Failed to fetch books:", e)
    raise

for idx, book in enumerate(all_books):
    try:
        # Safely extract title
        title = book.get("title", "Untitled")

        # Safely extract authors (handle list or string)
        authors_raw = book.get("authors", [])
        if isinstance(authors_raw, list):
            authors = ", ".join(authors_raw)
        elif isinstance(authors_raw, str):
            authors = authors_raw
        else:
            authors = "Unknown"

        # Safely extract description (handle string or dict)
        desc_raw = book.get("description", "")
        if isinstance(desc_raw, dict):
            description = desc_raw.get("value", "")
        elif isinstance(desc_raw, str):
            description = desc_raw
        else:
            description = ""

        # Trim overly long descriptions
        if len(description) > 1000:
            description = description[:1000] + "..."

        print(f"[INFO] Processing Book {idx + 1}: {title}")
        print(f"   Authors: {authors}")
        print(f"   Description: {description}\n")

        # === INSERT your book processing logic here ===
        # e.g., create script, summary, voiceover, etc.
        # process_book(title, authors, description)

    except Exception as e:
        print(f"[ERROR] Failed to process book {idx + 1}: {book}")
        print(f"Reason: {e}")

        # 2. Summarize
        summary = summarize_text(title)
        with open(f"summaries/{i+1}_{title[:30]}.txt", "w", encoding="utf-8") as f:
            f.write(summary)

        # 3. Text to Speech
        audio_path = f"voices/{i+1}_{title[:30]}.mp3"
        generate_voiceover(summary, audio_path)

        # 4. Create Video
        video_path = f"videos/{i+1}_{title[:30]}.mp4"
        generate_video(summary, audio_path, video_path)

        print(f"Done with {title}")

    except Exception as e:
        print(f"Error with {title}: {e}")
        continue 
