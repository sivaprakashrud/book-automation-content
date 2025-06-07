from gtts import gTTS
import os

def generate_voice(text, filename):
    try:
        tts = gTTS(text)
        path = f"voices/{filename}.mp3"
        os.makedirs("voices", exist_ok=True)
        tts.save(path)
        return path
    except Exception as e:
        print(f"[ERROR] Voice generation failed: {e}")
        return None


def generate_text_script(book):
    return f"📚 Title: {book['title']}\n👤 Author(s): {', '.join(book['authors'])}\n\n✨ Summary:\n{book['summary']}"
