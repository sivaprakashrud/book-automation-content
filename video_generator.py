# video_generator.py
# ────────────────────────────────────────────────────────────────
"""
Generate one Manim video for every summary chunk produced by
summarize.py.  Output MP4s will land in  videos/<Book>_part#.mp4
"""

import os, json, re, sys, subprocess, importlib.util

# ────────────────────────────────────────────────────────────────
# 0.  Ensure MANIM is installed in the *current interpreter*
# ────────────────────────────────────────────────────────────────
def ensure_manim():
    if importlib.util.find_spec("manim") is not None:
        return
    print("[WARN] 'manim' not found. Installing Manim Community Edition…")
    # ‘--quiet’ keeps CI logs clean; remove for verbose output.
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "--quiet", "manim==0.18.*"]
    )
ensure_manim()

from manim import *  # noqa: E402  (import AFTER we know it’s available)

# ────────────────────────────────────────────────────────────────
# 1.  Paths & helpers
# ────────────────────────────────────────────────────────────────
DATA_DIR     = "data"
SUMMARY_FILE = os.path.join(DATA_DIR, "summaries.json")
VIDEO_DIR    = "videos"
BACKGROUND_DIR = "backgrounds"            # optional stills

os.makedirs(VIDEO_DIR, exist_ok=True)

def safe_name(txt: str) -> str:
    """filename-safe slug."""
    return re.sub(r'[\\/*?:"<>|()\']', "", txt.replace(" ", "_"))


# ────────────────────────────────────────────────────────────────
# 2.  Scene template
# ────────────────────────────────────────────────────────────────
class SummaryScene(Scene):
    def __init__(self, title, body, bg_path=None, **kwargs):
        super().__init__(**kwargs)
        self.title_text = title
        self.body_text  = body
        self.bg_path    = bg_path

    def construct(self):
        # optional background
        if self.bg_path and os.path.exists(self.bg_path):
            bg = ImageMobject(self.bg_path).scale_to_fit_height(config.frame_height)
            self.add(bg)

        # Title
        title = Text(self.title_text, font_size=60, color=WHITE).to_edge(UP)

        # Body (wrap ~60 characters/line)
        wrapped = "\n".join(self.body_text.splitlines())
        body = Text(wrapped, font_size=36, color=WHITE)
        body.next_to(title, DOWN).align_on_border(LEFT)

        # animations
        self.play(FadeIn(title), run_time=1)
        self.play(Write(body), run_time=4)
        self.wait(1)
        self.play(FadeOut(title), FadeOut(body), run_time=0.8)


# ────────────────────────────────────────────────────────────────
# 3.  Driver – iterate JSON → render scenes
# ────────────────────────────────────────────────────────────────
def main():
    if not os.path.exists(SUMMARY_FILE):
        print("[ERROR] Run summarize.py first – no summaries.json found.")
        return

    with open(SUMMARY_FILE, encoding="utf-8") as f:
        books = json.load(f)

    if not books:
        print("[WARN] summaries.json is empty – nothing to film.")
        return

    for book in books:
        title  = book.get("title", "Untitled")
        bullets = book.get("summaries", [])
        if not bullets:
            print(f"[WARN] '{title}' has no summaries → skipping.")
            continue

        bg = os.path.join(BACKGROUND_DIR, f"{safe_name(title)}.png")
        for idx, text in enumerate(bullets, 1):
            outfile = f"{safe_name(title)}_part{idx}.mp4"
            out_path = os.path.join(VIDEO_DIR, outfile)

            print(f"[INFO] Rendering → {out_path}")
            # render with temporary config so files land exactly where we want
            with tempconfig({
                "media_dir": VIDEO_DIR,
                "output_file": outfile.replace(".mp4", ""),
                "format": "mp4",
                "quality": "low_quality",  # change to 'medium_quality' for nicer video
                "disable_caching": True
            }):
                scene = SummaryScene(title, text, bg_path=bg)
                scene.render()

    print("[INFO] All videos generated.")

# ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
