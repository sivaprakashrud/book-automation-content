import os
import json
import pyttsx3

SUMMARY_FILE = "data/summaries.json"
VOICE_DIR = "voices"

def generate_voices():
    if not os.path.exists(SUMMARY_FILE):
        print(f"[ERROR] {SUMMARY_FILE} not found. Please run summarize.py first.")
        return

    os.makedirs(VOICE_DIR, exist_ok=True)

    try:
        with open(SUMMARY_FILE, "r", encoding="utf-8") as f:
            summaries = json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load summaries: {e}")
        return

    engine = pyttsx3.init()
    engine.setProperty("rate", 150)
    engine.setProperty("volume", 1.0)

    for i, item in enumerate(summaries):
        title = item.get("title", f"Book {i+1}")
        summary = item.get("summary", "")

        if not summary:
            print(f"[WARNING] Summary missing for '{title}'. Skipping.")
            continue

        filename = os.path.join(VOICE_DIR, f"summary_{i+1}.mp3")

        print(f"[INFO] Generating voice for: {title}")
        try:
            engine.save_to_file(summary, filename)
            engine.runAndWait()
        except Exception as e:
            print(f"[ERROR] Failed to generate voice for '{title}': {e}")

    print(f"[INFO] Voice generation complete. Files saved in '{VOICE_DIR}/'.")

if __name__ == "__main__":
    generate_voices()
