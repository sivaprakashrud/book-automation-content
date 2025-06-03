# generate_all.py
from scraper import get_books_from_goodreads
from summarizer import summarize_book
from tts import text_to_audio
from video_maker import create_video

def main():
    books = get_books_from_goodreads()
    for title in books:
        summary = summarize_book(title)
        filename = title.replace(" ", "_")
        text_to_audio(summary, filename)
        create_video(summary, f"voices/{filename}.mp3", f"videos/{filename}.mp4")

if __name__ == "__main__":
    main()
