import os
from pydub import AudioSegment

def generate_youtube_description_with_timestamps(track_paths, mixtape_name="Mixtape", genre="Mix", start_time_sec=0):
    """
    track_paths: list of audio file paths in playback order
    """
    if not track_paths:
        raise ValueError("No tracks provided")
    description = f"🔥 {mixtape_name} 🔥\nGenre: {genre}\n\n🎵 Tracklist:\n"
    current_time = start_time_sec
    for path in track_paths:
        audio = AudioSegment.from_file(path)
        duration_sec = len(audio) // 1000
        minutes = current_time // 60
        seconds = current_time % 60
        timestamp = f"{minutes:02d}:{seconds:02d}"
        name = os.path.splitext(os.path.basename(path))[0]
        description += f"{timestamp} - {name}\n"
        current_time += duration_sec
    description += "\n💽 Download/Listen links:\nYou can find these tracks online.\n\n🎧 Follow for more mixes!\n\n"
    hashtags = ["#Mixtape", "#DJMix", "#HouseMusic", "#MusicMix"]
    description += " ".join(hashtags)
    return description
