import os
import json
import re
from gtts import gTTS

# File Paths
DATA_DIR = "data"
SUMMARY_FILE = os.path.join(DATA_DIR, "summaries.json")
VOICE_DIR = "voices"

def sanitize_filename(title):
    """Remove invalid characters for file names."""
    return re.sub(r'[\\/*?:"<>|()\']', "", title.replace(" ", "_"))

def generate_voices(summary_file=SUMMARY_FILE, output_folder=VOICE_DIR):
    """Generate voice files from book summaries using gTTS."""
    if not os.path.exists(summary_file):
        print(f"[ERROR] Summary file not found at: {summary_file}")
        return

    os.makedirs(output_folder, exist_ok=True)

    with open(summary_file, "r", encoding="utf-8") as f:
        try:
            summaries = json.load(f)
        except json.JSONDecodeError as e:
            print(f"[ERROR] Failed to load summaries file: {e}")
            return

    if not summaries:
        print("[WARN] No summaries found in file.")
        return

    for i, summary in enumerate(summaries):
        title = summary.get("title", f"untitled_{i}")
        text = summary.get("summary", "").strip()

        if not text:
            print(f"[WARN] No content to generate voice for: {title}")
            continue

        try:
            tts = gTTS(text, lang="en")  # ✅ Explicitly set language to English
            safe_title = sanitize_filename(title)
            voice_path = os.path.join(output_folder, f"{safe_title}.mp3")
            tts.save(voice_path)
            print(f"[INFO] Saved voice file: {voice_path}")
        except Exception as e:
            print(f"[ERROR] Failed to generate voice for {title}: {e}")

if __name__ == "__main__":
    generate_voices()
