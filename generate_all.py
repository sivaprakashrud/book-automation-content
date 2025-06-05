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
titles = fetch_books("self-help")
print(f"Fetched {len(titles)} books")

for i, title in enumerate(titles):
    try:
        print(f"\nProcessing Book {i+1}: {title}")
MAX_DESCRIPTION_LENGTH = 2000  # or any safe limit your model handles well

def truncate_description(description):
    return description[:MAX_DESCRIPTION_LENGTH] + "..." if len(description) > MAX_DESCRIPTION_LENGTH else description
book["description"] = truncate_description(book.get("description", ""))

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
