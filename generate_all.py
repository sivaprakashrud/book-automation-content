from fetch_books import fetch_books
from summarize import generate_summaries
from voice_generator import generate_voices
from video_generator import generate_videos

def main():
    print("[STEP 1] Fetching books...")
    fetch_books()

    print("[STEP 2] Generating summaries...")
    generate_summaries()  # ✅ No arguments required

    print("[STEP 3] Generating voice files...")
    generate_voices()

    print("[STEP 4] Generating videos...")
    generate_videos()

if __name__ == "__main__":
    main()
