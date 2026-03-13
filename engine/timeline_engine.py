import json
import os
from pydub import AudioSegment


def get_audio_duration(file_path, default=2000):
    """安全获取音频时长"""
    try:
        if file_path and os.path.exists(file_path):
            audio = AudioSegment.from_file(file_path)
            return len(audio)
    except Exception as e:
        print(f"⚠ 读取音频失败: {file_path} {e}")

    return default


def build_timeline(story_json_path, audio_plan_path):
    """
    根据 audio_plan 生成 timeline
    timeline 是最终统一时间轴
    """

    # story_json 其实已经不需要，但先保留接口
    with open(story_json_path, "r", encoding="utf-8") as f:
        story = json.load(f)

    with open(audio_plan_path, "r", encoding="utf-8") as f:
        audio_plan = json.load(f)

    timeline = []
    current_time = 0

    for segment in audio_plan:

        seg_type = segment["type"]

        event = {
            "index": segment.get("index"),
            "type": seg_type,
            "start": current_time
        }

        # ---------------- dialogue ----------------
        if seg_type == "dialogue":

            duration = segment.get("duration")

            if duration is None:
                duration = get_audio_duration(segment.get("file"))

            event.update({
                "speaker": segment.get("speaker"),
                "text": segment.get("text"),
                "file": segment.get("file"),
                "duration": duration
            })

            current_time += duration

        # ---------------- sfx ----------------
        elif seg_type == "sfx":

            duration = get_audio_duration(segment.get("file"))

            event.update({
                "sfx_name": segment.get("sfx_name"),
                "file": segment.get("file"),
                "duration": duration
            })

            current_time += duration

        # ---------------- pause ----------------
        elif seg_type == "pause":

            duration = segment.get("duration", 500)

            event.update({
                "duration": duration
            })

            current_time += duration

        # ---------------- bgm ----------------
        elif seg_type == "bgm":

            event.update({
                "file": segment.get("file")
            })

            # BGM 不推进时间

        timeline.append(event)

    return timeline