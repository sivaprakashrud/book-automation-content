import os
import json
import re
from gtts import gTTS

SUMMARY_FILE = "data/summaries.json"
VOICE_DIR = "voices"

def sanitize_filename(title):
    """Remove invalid characters for file names."""
    return re.sub(r'[\\/*?:"<>|()\']', "", title.replace(" ", "_"))

def generate_voices(summary_file=SUMMARY_FILE, output_folder=VOICE_DIR):
    os.makedirs(output_folder, exist_ok=True)

    with open(summary_file, "r", encoding="utf-8") as f:
        summaries = json.load(f)

    for summary in summaries:
        title = summary.get("title", f"untitled_{summaries.index(summary)}")
        text = summary.get("summary", "")

        if not text:
            print(f"[WARN] No summary for: {title}")
            continue

        try:
            tts = gTTS(text)
            safe_title = sanitize_filename(title)
            voice_path = os.path.join(output_folder, f"{safe_title}.mp3")
            tts.save(voice_path)
            print(f"[INFO] Saved voice file: {voice_path}")
        except Exception as e:
            print(f"[ERROR] Failed to generate voice for {title}: {e}")

if __name__ == "__main__":
    generate_voices()
