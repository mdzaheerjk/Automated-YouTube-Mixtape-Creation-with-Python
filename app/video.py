import subprocess, os
from PIL import Image
from .config import OUTPUT_DIR

def make_video_from_audio(image_path, audio_path, output_filename="mixtape_vid.mp4",
                          video_resolution=(1280, 720), fps=1, preset="ultrafast"):
    # validations
    if not os.path.exists(image_path):
        raise FileNotFoundError("Image not found: " + image_path)
    if not os.path.exists(audio_path):
        raise FileNotFoundError("Audio not found: " + audio_path)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    temp_img = os.path.join(OUTPUT_DIR, "temp_resized_image.jpg")
    img = Image.open(image_path)
    img = img.resize(video_resolution)
    img.save(temp_img)

    out_path = os.path.join(OUTPUT_DIR, output_filename)
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", temp_img,
        "-i", audio_path,
        "-c:v", "libx264",
        "-preset", preset,
        "-tune", "stillimage",
        "-r", str(fps),
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        out_path
    ]
    subprocess.run(cmd, check=True)
    os.remove(temp_img)
    return out_path
