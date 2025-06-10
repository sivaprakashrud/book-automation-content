from fetch_books import fetch_books
from summarize import summarize_books
from voice_generator import generate_voices
from video_generator import generate_videos

def main():
    print("[STEP 1] Fetching books...")
    books = fetch_books()

    print("[STEP 2] Generating summaries...")
    summaries = summarize_books()

    print("[STEP 3] Generating voice files...")
    generate_voices(summaries)

    print("[STEP 4] Generating videos...")
    generate_videos(summaries)

if __name__ == "__main__":
    main()
