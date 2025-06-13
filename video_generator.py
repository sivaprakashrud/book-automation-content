from manim import *
import json, os, re, textwrap

# File Paths
DATA_DIR = "data"
SUMMARY_FILE = os.path.join(DATA_DIR, "summaries.json")
VIDEO_DIR = "videos"
BACKGROUND_DIR = "backgrounds"

class SummaryVideo(Scene):
    def __init__(self, title, summary, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.summary = summary

    def construct(self):
        """Generate an animated video for a single summary."""
        print(f"[INFO] Creating video for: {self.title}")

        # Format text
        wrapped_text = "\n".join(textwrap.wrap(self.summary, width=60))

        # Load background image or video
        bg_path = os.path.join(BACKGROUND_DIR, f"{sanitize_filename(self.title)}.png")
        if os.path.exists(bg_path):
            background = ImageMobject(bg_path).scale(1.5)
        else:
            background = Rectangle(width=16, height=9, color=BLACK)

        # Create title
        title_text = Text(self.title, font_size=60, color=WHITE).to_edge(UP)
        
        # Create summary text with animation
        summary_text = Text(wrapped_text, font_size=40, color=WHITE)
        summary_text.shift(DOWN)

        # Animate the text with fade-in and movement
        self.play(FadeIn(background), run_time=1)
        self.play(Write(title_text), run_time=2)
        self.play(summary_text.animate.shift(RIGHT * 2), run_time=5)
        
        # Add fade-out effect
        self.play(FadeOut(title_text), FadeOut(summary_text), FadeOut(background))

        print(f"[INFO] Video for '{self.title}' generated successfully!")

def sanitize_filename(title):
    """Remove invalid characters for file names."""
    return re.sub(r'[\\/*?:"<>|()\']', "", title.replace(" ", "_"))

def generate_videos():
    """Generate separate videos for each summary."""
    if not os.path.exists(SUMMARY_FILE):
        print("[ERROR] Summary file missing.")
        return
    
    with open(SUMMARY_FILE, "r", encoding="utf-8") as f:
        summaries = json.load(f)

    os.makedirs(VIDEO_DIR, exist_ok=True)

    for item in summaries:
        title = item.get("title", "Untitled")
        summary_list = item.get("summaries", [])

        if not title or not summary_list:
            print(f"[WARN] Missing title or summary in entry: {item}")
            continue

        for i, summary in enumerate(summary_list):
            video_filename = os.path.join(VIDEO_DIR, f"{sanitize_filename(title)}_part{i+1}.mp4")
            scene = SummaryVideo(title, summary)
            scene.render()
            print(f"[INFO] Saved video: {video_filename}")

if __name__ == "__main__":
    generate_videos()
