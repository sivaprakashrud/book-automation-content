pip install moviepy

from moviepy.editor import TextClip, AudioFileClip, CompositeVideoClip

def generate_video(summary_text, audio_path, output_path="final_video.mp4"):
    clip = TextClip(summary_text, fontsize=24, color='white', bg_color='black', size=(720, 1280), method='caption')
    clip = clip.set_duration(AudioFileClip(audio_path).duration)
    audio = AudioFileClip(audio_path)
    video = clip.set_audio(audio)
    video.write_videofile(output_path, fps=24)
    return output_path
