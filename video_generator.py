"""
Karaoke Video Generator
-----------------------
This script generates a 45-second video that includes:
  • An automatically generated, animated abstract background.
  • A subtitle overlay that shows the full voiceover transcript as a single line.
  • A karaoke effect, where the word being spoken is highlighted (in yellow)
    for the duration it is heard (based on a fixed timing algorithm).
  • An optional voiceover audio track is added, if available.

Requirements:
  - Summaries must be available in data/summaries.json.
  - Optionally, a voiceover file exists in voices/ matching the book title & part.
"""
import os, json, re, sys, subprocess, importlib.util, random
from manim import *

# ————————————————
# 0. Ensure MANIM is installed in the correct Python environment
# ————————————————
def ensure_manim():
    if importlib.util.find_spec("manim") is None:
        print("[WARN] 'manim' not found. Installing now...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "manim"])
    
    # Install required system dependencies for Manim
    if sys.platform.startswith("linux"):
        print("[INFO] Installing FFmpeg & Cairo dependencies...")
        subprocess.run([
            "sudo", "apt-get", "install", "-y", "libcairo2-dev", "libpango1.0-dev",
            "libglib2.0-dev", "pkg-config", "ffmpeg"
        ], check=True)
    
    import manim  # Final confirmation of successful install

ensure_manim()

from manim import *

# ————————————————
# 1. Paths and Helper Functions
# ————————————————
DATA_DIR = "data"
SUMMARY_FILE = os.path.join(DATA_DIR, "summaries.json")
VIDEO_DIR = "videos"
VOICE_DIR = "voices"

os.makedirs(VIDEO_DIR, exist_ok=True)

def safe_name(txt: str) -> str:
    return re.sub(r'[\\/*?:"<>|()\']', "", txt.replace(" ", "_"))

def get_voice_file(title: str, part:int=1) -> str:
    """Return the voiceover file path if available."""
    fp = os.path.join(VOICE_DIR, f"{safe_name(title)}_part{part}.mp3")
    return fp if os.path.exists(fp) else ""

# ————————————————
# 2. Animated Abstract Background (45 sec)
# ————————————————
class AbstractBackground(Scene):
    def construct(self):
        # Floating animated circles with shifting colors
        circles = VGroup(*[Circle(radius=random.uniform(0.7, 1.5),
                                  color=random.choice([BLUE, GREEN, RED, PURPLE]),
                                  fill_opacity=0.4)
                          for _ in range(10)])
        circles.arrange_in_grid(rows=3, buff=1.2)
        self.add(circles)
        
        # Animate for full 45 seconds
        self.play(AnimationGroup(*[
            circle.animate.shift(RIGHT * random.uniform(-2,2) + UP * random.uniform(-2,2))
            .set_color(random.choice([WHITE, YELLOW, ORANGE, PINK]))
            for circle in circles
        ], lag_ratio=0.3), run_time=45, rate_func=there_and_back)

# ————————————————
# 3. Karaoke Subtitle Scene
# ————————————————
class KaraokeScene(Scene):
    def __init__(self, title: str, transcript: str, voice_path: str = "", **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.transcript = transcript
        self.voice_path = voice_path

    def construct(self):
        TOTAL_DURATION = 45  # Fixed video duration

        # Add animated abstract background
        self.camera.background_color = DARK_BLUE
        bg_circles = VGroup(*[Circle(radius=random.uniform(0.7, 1.5),
                                      color=random.choice([BLUE, GREEN, RED, PURPLE]),
                                      fill_opacity=0.3)
                              for _ in range(10)])
        bg_circles.arrange_in_grid(rows=3, buff=1.2)
        self.add(bg_circles)
        self.play(AnimationGroup(*[
            circle.animate.shift(RIGHT*random.uniform(-2,2) + UP*random.uniform(-2,2))
            .set_color(random.choice([WHITE, YELLOW, ORANGE, PINK]))
            for circle in bg_circles
        ], lag_ratio=0.3), run_time=TOTAL_DURATION, rate_func=there_and_back)

        # Display Title at the Top
        title_text = Text(self.title, font_size=50, color=WHITE).to_edge(UP)
        self.add(title_text)

        # Create the subtitle (word-by-word karaoke effect)
        words = self.transcript.split()
        word_mobjects = VGroup(*[Text(word, font_size=36, color=WHITE) for word in words])
        word_mobjects.arrange(RIGHT, buff=0.3).to_edge(DOWN)
        self.add(word_mobjects)

        # Attach voiceover if available
        if self.voice_path:
            try:
                self.add_sound(self.voice_path)
                print(f"[INFO] Added voiceover: {self.voice_path}")
            except Exception as e:
                print(f"[WARN] Failed to attach voiceover: {e}")

        # Karaoke-style word highlighting timing
        duration_per_word = TOTAL_DURATION / len(words)
        
        # Highlight words as they are spoken
        for i, word in enumerate(word_mobjects):
            self.play(word.animate.set_color(YELLOW), run_time=duration_per_word * 0.8, rate_func=linear)
            if i > 0:  # Reset previous words to white
                self.play(word_mobjects[i-1].animate.set_color(WHITE), run_time=duration_per_word * 0.2, rate_func=linear)

        # Final cleanup: Reset last word to white
        if word_mobjects:
            self.play(word_mobjects[-1].animate.set_color(WHITE), run_time=0.5)

# ————————————————
# 4. Main Driver: Load transcript and render karaoke video
# ————————————————
def main():
    if not os.path.exists(SUMMARY_FILE):
        print("[ERROR] summaries.json not found. Run summarize.py first.")
        return

    with open(SUMMARY_FILE, encoding="utf-8") as f:
        books = json.load(f)

    if not books:
        print("[WARN] summaries.json is empty.")
        return

    # Select first book & summary bullet
    book = books[0]
    title = book.get("title", "Untitled")
    transcript = book.get("summaries", [""])[0]
    transcript = transcript.strip() or "No transcript available."
    
    # Check for matching voiceover file
    voice_file = get_voice_file(title)

    safe_title = safe_name(title)
    
    # Render Karaoke Scene
    output_filename = f"{safe_title}_karaoke.mp4"
    print(f"[INFO] Rendering karaoke video → {output_filename}")
    with tempconfig({
        "media_dir": VIDEO_DIR,
        "output_file": safe_title + "_karaoke",
        "format": "mp4",
        "quality": "medium_quality",
        "disable_caching": True
    }):
        scene = KaraokeScene(title, transcript, voice_path=voice_file)
        scene.render()

    print("[INFO] Karaoke video generated successfully.")

if __name__ == "__main__":
    main()
