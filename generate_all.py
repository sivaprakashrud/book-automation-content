import os
from fetch_books import fetch_books
from summarize import generate_summaries
from voice_generator import generate_voices
from video_generator import generate_videos

def ensure_folders():
    os.makedirs("data", exist_ok=True)
    os.makedirs("voices", exist_ok=True)
    os.makedirs("videos", exist_ok=True)

def main():
    print("\n[STEP 1] Ensuring folders exist...")
    ensure_folders()

    print("\n[STEP 2] Fetching books...")
    fetch_books()

    print("\n[STEP 3] Generating summaries...")
    generate_summaries()

    print("\n[STEP 4] Generating voiceovers...")
    generate_voices()

    print("\n[STEP 5] Creating videos...")
    generate_videos()

    print("\n✅ All tasks completed. Videos are ready in the 'videos/' folder.")

if __name__ == "__main__":
    main()

