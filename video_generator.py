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

# ────────────────────────────────────────────────────────────────
# 0. Ensure Manim is installed (if not, auto-install; see previous instructions)
def ensure_manim():
    if importlib.util.find_spec("manim") is not None:
        return
    print("[WARN] 'manim' not found. Installing Manim Community Edition…")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "manim==0.18.*"])
ensure_manim()

from manim import *

# ────────────────────────────────────────────────────────────────
# 1. Global paths and helper functions
# ────────────────────────────────────────────────────────────────
DATA_DIR      = "data"
SUMMARY_FILE  = os.path.join(DATA_DIR, "summaries.json")
VIDEO_DIR     = "videos"
VOICE_DIR     = "voices"

os.makedirs(VIDEO_DIR, exist_ok=True)

def safe_name(txt: str) -> str:
    return re.sub(r'[\\/*?:"<>|()\']', "", txt.replace(" ", "_"))

def get_voice_file(title: str, part:int=1) -> str:
    """Return the voiceover file path if it exists."""
    fp = os.path.join(VOICE_DIR, f"{safe_name(title)}_part{part}.mp3")
    return fp if os.path.exists(fp) else ""

# ────────────────────────────────────────────────────────────────
# 2. Animated Abstract Background Scene (45 seconds)
# ────────────────────────────────────────────────────────────────
class AbstractBackground(Scene):
    """
    An abstract animated background that runs for exactly 45 seconds.
    In this example, we animate a group of circles that slowly drift and shift color.
    """
    def construct(self):
        circles = VGroup(*[Circle(radius=random.uniform(0.7, 1.2),
                                    color=random.choice([BLUE, GREEN, RED, PURPLE]),
                                    fill_opacity=0.5)
                           for _ in range(8)])
        circles.arrange_in_grid(rows=2, buff=1)
        self.add(circles)
        # Animate over full 45 seconds.
        self.play(AnimationGroup(*[circle.animate.shift(RIGHT * random.uniform(-2,2) + UP * random.uniform(-2,2))
                                    for circle in circles], lag_ratio=0.5),
                  run_time=45, rate_func=there_and_back)

# ────────────────────────────────────────────────────────────────
# 3. Karaoke Subtitle Scene
# ────────────────────────────────────────────────────────────────
class KaraokeScene(Scene):
    """
    This scene combines the abstract background with a karaoke-style subtitle overlay.
    The complete voiceover transcript is displayed as a single line at the bottom of the screen.
    As the 45-second video plays (optionally with a voiceover sound), the words are highlighted one-by-one.
    """
    def __init__(self, title: str, transcript: str, voice_path: str = "", **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.transcript = transcript
        self.voice_path = voice_path

    def construct(self):
        # Set overall video duration as 45 seconds.
        TOTAL_DURATION = 45
        
        # Set background color and add abstract background animation (can blend with subtitles).
        self.camera.background_color = DARK_BLUE
        # Create a simplified abstract background: slowly moving circles.
        bg_circles = VGroup(*[Circle(radius=random.uniform(0.7, 1.2),
                                       color=random.choice([BLUE, GREEN, RED, PURPLE]),
                                       fill_opacity=0.3)
                              for _ in range(8)])
        bg_circles.arrange_in_grid(rows=2, buff=1)
        self.add(bg_circles)
        self.play(AnimationGroup(*[circle.animate.shift(RIGHT*random.uniform(-2,2) + UP*random.uniform(-2,2))
                                    for circle in bg_circles], lag_ratio=0.5),
                  run_time=TOTAL_DURATION, rate_func=there_and_back)
        
        # Add a static title at the top.
        title_text = Text(self.title, font_size=50, color=WHITE).to_edge(UP)
        self.add(title_text)
        
        # Create the subtitle line as individual words (Karaoke effect).
        words = self.transcript.split()
        word_mobjects = VGroup(*[Text(word, font_size=36, color=WHITE) for word in words])
        word_mobjects.arrange(RIGHT, buff=0.3)
        word_mobjects.to_edge(DOWN)
        self.add(word_mobjects)
        
        # If a voiceover file exists, add it as the audio track.
        if self.voice_path:
            try:
                self.add_sound(self.voice_path)
                print(f"[INFO] Added voiceover: {self.voice_path}")
            except Exception as e:
                print(f"[WARN] Voiceover addition failed: {e}")
        
        # Calculate timing: each word gets its share of the TOTAL_DURATION.
        duration_per_word = TOTAL_DURATION / len(words)
        
        # Karaoke loop: sequentially highlight each word.
        # The current word is set to yellow, while the previous word reverts to white.
        for i, word in enumerate(word_mobjects):
            # Highlight the current word.
            self.play(word.animate.set_color(YELLOW), run_time=duration_per_word * 0.8, rate_func=linear)
            # Immediately after, revert the previous word (if any) to white.
            if i > 0:
                self.play(word_mobjects[i-1].animate.set_color(WHITE), run_time=duration_per_word * 0.2, rate_func=linear)
        # End: ensure the last word is reset to white.
        if len(word_mobjects) > 0:
            self.play(word_mobjects[-1].animate.set_color(WHITE), run_time=0.5)

# ────────────────────────────────────────────────────────────────
# 4. Main Driver: Load transcript and Render Karaoke Video
# ────────────────────────────────────────────────────────────────
def main():
    if not os.path.exists(SUMMARY_FILE):
        print("[ERROR] summaries.json not found. Run summarize.py first.")
        return

    with open(SUMMARY_FILE, encoding="utf-8") as f:
        books = json.load(f)

    if not books:
        print("[WARN] summaries.json is empty.")
        return

    # For demonstration, choose the first book & its first summary.
    book = books[0]
    title = book.get("title", "Untitled")
    # Assume the full transcript is the complete summary text.
    transcript = book.get("summaries", [""])[0]
    if not transcript.strip():
        transcript = "No transcript available."

    # Optionally, check for matching voice file.
    voice_file = get_voice_file(title, part=1)

    safe_title = safe_name(title)
    
    # Render the karaoke scene.
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
