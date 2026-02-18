from pydub import AudioSegment
import os, random
from .config import OUTPUT_DIR, ALLOWED_AUDIO_EXT

def smooth_fade_mixtape_from_files(file_paths, output_filename="mixtape.mp3", transition_ms=6000):
    """
    file_paths: list of local file paths to audio files (ordered or randomized externally)
    """
    mixtape = None
    random.shuffle(file_paths)  # optional: randomize
    for i, filepath in enumerate(file_paths):
        song = AudioSegment.from_file(filepath)
        song = song.set_channels(2).set_frame_rate(44100)  # normalize
        if mixtape is None:
            mixtape = song
        else:
            overlap = min(transition_ms, len(song), len(mixtape))
            outgoing = mixtape[-overlap:].fade_out(overlap).low_pass_filter(4000)
            incoming = song[:overlap].fade_in(overlap).low_pass_filter(4000)
            transition = outgoing.overlay(incoming)
            mixtape = mixtape[:-overlap] + transition + song[overlap:]
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, output_filename)
    mixtape.export(out_path, format="mp3")
    return out_path
