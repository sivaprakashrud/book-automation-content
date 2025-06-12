from fetch_books import fetch_books
from summarize import summarize_books
from voice_generator import generate_voices
from video_generator import generate_videos
import os

# File Paths
SUMMARY_FILE = "data/summaries.json"

def main():
    print("[STEP 1] Fetching books...")
    books = fetch_books()

    if not books:
        print("[ERROR] No books fetched. Exiting process.")
        return

    print("[STEP 2] Generating summaries...")
    summaries = summarize_books()

    if not os.path.exists(SUMMARY_FILE) or not summaries:
        print("[ERROR] No summaries found. Skipping voice and video generation.")
        return

    print("[STEP 3] Generating voice files...")
    generate_voices(SUMMARY_FILE)

    print("[STEP 4] Generating videos...")
    generate_videos(SUMMARY_FILE)

    print("[INFO] Process completed successfully!")

if __name__ == "__main__":
    main()
