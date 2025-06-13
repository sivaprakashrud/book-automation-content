# voice_generator.py  – self-installing gTTS + random voices
import os, json, re, random, subprocess, sys

# ------------------------------------------------------------------
# Make sure gTTS is available
# ------------------------------------------------------------------
try:
    from gtts import gTTS
except ModuleNotFoundError:
    print("[WARN] gTTS not found. Installing…")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "gTTS"])
    from gtts import gTTS

# ------------------------------------------------------------------
DATA_DIR   = "data"
SUMMARY_FP = os.path.join(DATA_DIR, "summaries.json")
VOICE_DIR  = "voices"
VOICES     = ["en", "en-au", "en-uk", "en-us", "en-in"]  # random accents
# ------------------------------------------------------------------

def sanitize(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|()\']', "", name.replace(" ", "_"))

def generate_voices(summary_file: str = SUMMARY_FP, out_dir: str = VOICE_DIR):
    if not os.path.exists(summary_file):
        print(f"[ERROR] Missing {summary_file}. Run summarize.py first.")
        return

    os.makedirs(out_dir, exist_ok=True)

    with open(summary_file, encoding="utf-8") as f:
        data = json.load(f)

    if not data:
        print("[WARN] summaries.json is empty.")
        return

    for book in data:
        title = book.get("title", "Untitled")
        for idx, text in enumerate(book.get("summaries", []), start=1):
            if not text.strip():
                continue
            try:
                voice = random.choice(VOICES)
                tts   = gTTS(text=text, lang=voice.split("-")[0])
                fp    = os.path.join(out_dir, f"{sanitize(title)}_part{idx}.mp3")
                tts.save(fp)
                print(f"[INFO] Saved: {fp}  (voice={voice})")
            except Exception as e:
                print(f"[WARN] Couldn’t voice '{title}' part {idx}: {e}")

if __name__ == "__main__":
    generate_voices()
