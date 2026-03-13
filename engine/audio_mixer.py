import json
import os
from pydub import AudioSegment
from pydub.generators import Sine


def generate_tts_placeholder(duration):
    """生成占位 TTS 音频（简单蜂鸣）"""
    tone = Sine(440)
    audio = tone.to_audio_segment(duration=duration)
    return (audio - 10)[:duration]


def load_or_create_tts(file_path, duration):
    """如果 TTS 文件不存在，就创建占位音频"""
    if os.path.exists(file_path):
        return AudioSegment.from_file(file_path)

    audio = generate_tts_placeholder(duration)

    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    audio.export(file_path, format="wav")

    return audio


def ms_to_srt_time(ms):
    """毫秒转 SRT 时间格式"""

    hours = ms // 3600000
    minutes = (ms % 3600000) // 60000
    seconds = (ms % 60000) // 1000
    milliseconds = ms % 1000

    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


def mix_audio(story_json_path, audio_plan_path, task_dir):
    """生成最终音频并输出标准 SRT 字幕"""

    audio_dir = os.path.join(task_dir, "audio")
    subtitle_dir = os.path.join(task_dir, "subtitle")

    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(subtitle_dir, exist_ok=True)

    # ----------------------
    # 读取数据
    # ----------------------

    with open(audio_plan_path, "r", encoding="utf-8") as f:
        audio_plan = json.load(f)

    with open(story_json_path, "r", encoding="utf-8") as f:
        story_data = json.load(f)

    final_audio = AudioSegment.silent(duration=0)

    bgm_audio = None

    subtitles = []

    current_time = 0
    story_index = 0

    # ----------------------
    # 处理音频计划
    # ----------------------

    for segment in audio_plan:

        seg_type = segment["type"]

        # ---------------- dialogue ----------------
        if seg_type == "dialogue":

            dialogue_text = ""

            while story_index < len(story_data["segments"]):

                s = story_data["segments"][story_index]

                story_index += 1

                if s.get("type") == "dialogue" and s.get("text"):

                    dialogue_text = s["text"]

                    break

            duration = segment.get("duration") or 2000

            tts_audio = load_or_create_tts(segment["file"], duration)

            final_audio += tts_audio

            if dialogue_text.strip() and dialogue_text != "None":

                subtitles.append({
                    "index": len(subtitles) + 1,
                    "start": ms_to_srt_time(current_time),
                    "end": ms_to_srt_time(current_time + len(tts_audio)),
                    "text": dialogue_text
                })

            current_time += len(tts_audio)

        # ---------------- sfx ----------------
        elif seg_type == "sfx":

            path = segment.get("file")

            if path and os.path.exists(path):

                sfx = AudioSegment.from_file(path)

            else:

                print(f"⚠ SFX 文件不存在 {path}")

                sfx = AudioSegment.silent(duration=500)

            final_audio += sfx

            current_time += len(sfx)

        # ---------------- bgm ----------------
        elif seg_type == "bgm":

            path = segment.get("file")

            if path and os.path.exists(path):

                bgm_audio = AudioSegment.from_file(path) - 10

            else:

                print(f"⚠ BGM 文件不存在 {path}")

                bgm_audio = None

        # ---------------- pause ----------------
        elif seg_type == "pause":

            duration = segment.get("duration") or 500

            silence = AudioSegment.silent(duration=duration)

            final_audio += silence

            current_time += duration

    # ----------------------
    # 叠加 BGM
    # ----------------------

    if bgm_audio:

        loop_count = (len(final_audio) // len(bgm_audio)) + 1

        bgm_loop = bgm_audio * loop_count

        final_audio = final_audio.overlay(bgm_loop[:len(final_audio)])

    # ----------------------
    # 输出音频
    # ----------------------

    output_file = os.path.join(audio_dir, "final_audio.wav")

    final_audio.export(output_file, format="wav")

    print("Final audio generated:", output_file)

    # ----------------------
    # 输出字幕
    # ----------------------

    srt_file = os.path.join(subtitle_dir, "subtitle.srt")

    with open(srt_file, "w", encoding="utf-8") as f:

        for sub in subtitles:

            f.write(f"{sub['index']}\n")

            f.write(f"{sub['start']} --> {sub['end']}\n")

            f.write(f"{sub['text']}\n\n")

    print("Subtitle file generated:", srt_file)

    return output_file, srt_file