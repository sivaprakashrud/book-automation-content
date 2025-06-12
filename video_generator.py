from manim import *

class ProductivityVideo(Scene):
    def construct(self):
        # Load content from JSON
        import json, os, re, textwrap
        SUMMARY_FILE = "data/summaries.json"
        if not os.path.exists(SUMMARY_FILE):
            print("[ERROR] Summary file missing.")
            return
        
        with open(SUMMARY_FILE, "r", encoding="utf-8") as f:
            summaries = json.load(f)

        for item in summaries:
            title = item.get("title", "Untitled")
            summary = item.get("summary", "")
            if not title or not summary:
                print(f"[WARN] Missing title or summary in entry: {item}")
                continue

            print(f"[INFO] Creating video for: {title}")

            # Format text
            wrapped_text = "\n".join(textwrap.wrap(summary, width=60))

            # Create title
            title_text = Text(title, font_size=60, color=WHITE).to_edge(UP)
            
            # Create summary text with animation
            summary_text = Text(wrapped_text, font_size=40, color=WHITE)
            summary_text.shift(DOWN)
            
            # Animate the text moving across the screen
            self.play(Write(title_text), run_time=2)
            self.play(summary_text.animate.shift(RIGHT * 2), run_time=5)
            
            # Add fade-out effect
            self.play(FadeOut(title_text), FadeOut(summary_text))
        
        print("[INFO] All videos processed successfully!")
