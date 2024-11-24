import json
import os

from pydub import AudioSegment


def get_audio_duration(file_path):
    audio = AudioSegment.from_file(file_path)
    duration_seconds = audio.duration_seconds

    return duration_seconds


def save_result_to_local_file(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as result_file:
        json.dump(data, result_file, ensure_ascii=False, indent=4)
