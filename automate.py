import requests
from fetch_books import fetch_books_from_gutenberg
from summarize import summarize_text
from text_to_speech import generate_voiceover
from video_generator import generate_video

def automate(query="productivity", max_books=1):
    book_urls = fetch_books_from_gutenberg(query, max_books)
    for url in book_urls:
        try:
            book_text = requests.get(url).text[:3000]
            summary = summarize_text(book_text)
            audio_path = generate_voiceover(summary)
            video_path = generate_video(summary, audio_path)
            print(f"Generated video: {video_path}")
        except Exception as e:
            print(f"Failed to process book from {url}: {e}")

if __name__ == "__main__":
    automate()