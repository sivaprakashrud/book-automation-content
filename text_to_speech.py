from gtts import gTTS
import os

def generate_voiceover(text, output_path="output.mp3"):
    tts = gTTS(text)
    tts.save(output_path)
    return output_path