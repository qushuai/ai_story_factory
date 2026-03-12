import os
from db.audio_repository import get_sfx_map
from core.config_loader import config


TTS_DIR = config["paths"]["tts_placeholder_dir"]
TTS_DURATION = config["audio"]["tts_placeholder_duration"]


def build_audio_plan(story_json):

    os.makedirs(TTS_DIR, exist_ok=True)

    sfx_map = get_sfx_map()

    audio_plan = []

    index = 0

    for seg in story_json["segments"]:

        entry = {
            "index": index,
            "type": seg.type
        }

        # -------------------------
        # dialogue
        # -------------------------
        if seg.type == "dialogue":

            speaker = seg.speaker
            text = seg.text

            filename = f"{index}_{speaker}.wav"

            file_path = os.path.join(TTS_DIR, filename)

            entry.update({
                "speaker": speaker,
                "text": text,
                "file": file_path,
                "duration": TTS_DURATION
            })

        # -------------------------
        # sfx
        # -------------------------
        elif seg.type == "sfx":

            name = seg.name

            if name not in sfx_map:

                print(f"⚠ 未找到 SFX: {name}")

                continue

            entry.update({
                "sfx_name": name,
                "file": sfx_map[name]
            })

        # -------------------------
        # pause
        # -------------------------
        elif seg.type == "pause":

            duration = seg.duration or 600

            entry.update({
                "duration": duration
            })

        audio_plan.append(entry)

        index += 1

    return audio_plan