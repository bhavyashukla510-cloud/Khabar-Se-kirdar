from moviepy.editor import ImageClip, concatenate_videoclips
from PIL import Image, ImageDraw
import os

OUTPUT_PATH = "backend-python/outputs/video/output.mp4"


def create_frame(text, index, size=(1280, 720)):

    img = Image.new("RGB", size, color=(30, 30, 30))
    draw = ImageDraw.Draw(img)

    draw.text((80, 300), text[:100], fill=(255, 255, 255))

    frame_path = f"temp_frame_{index}.png"
    img.save(frame_path)

    return frame_path


def generate_with_local_ai(prompt: str):

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    scenes = [
        "AI NEWS GENERATOR",
        "Processing Data...",
        prompt
    ]

    clips = []
    temp_files = []

    for i, scene in enumerate(scenes):

        frame_path = create_frame(scene, i)
        temp_files.append(frame_path)

        clip = ImageClip(frame_path).set_duration(2)
        clips.append(clip)

    final = concatenate_videoclips(clips)

    final.write_videofile(
        OUTPUT_PATH,
        fps=24,
        codec="libx264",
        audio=False
    )

    # cleanup temp images
    for f in temp_files:
        if os.path.exists(f):
            os.remove(f)

    return {
        "video_path": OUTPUT_PATH
    }