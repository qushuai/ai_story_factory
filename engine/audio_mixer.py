import json
import os
from pydub import AudioSegment
from pydub.generators import Sine
from core.config_loader import config

OUTPUT_DIR = "output/audio"
SUBTITLE_FILE = "final_audio.srt"  # 字幕文件

def generate_tts_placeholder(duration):
    """生成占位 TTS 音频（简单蜂鸣）"""
    tone = Sine(440)
    audio = tone.to_audio_segment(duration=duration)
    return audio - 10  # 音量降低

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

def mix_audio(story_json_path, audio_plan_path):
    """根据 audio_plan 生成最终音频，支持 TTS、SFX、BGM、PAUSE，并生成字幕"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 读取音频计划（audio plan）
    with open(audio_plan_path, "r", encoding="utf-8") as f:
        audio_plan = json.load(f)

    # 读取故事 JSON，获取对白内容
    with open(story_json_path, "r", encoding="utf-8") as f:
        story_data = json.load(f)

    final_audio = AudioSegment.silent(duration=0)
    bgm_audio = None
    subtitles = []  # 存储字幕段
    current_time = 0  # 毫秒

    story_index = 0  # 当前对白内容索引

    for segment in audio_plan:
        seg_type = segment["type"]

        # ----------------------
        # 对话
        # ----------------------
        if seg_type == "dialogue":
            # 获取对白文本
            speaker = segment.get("speaker", "narrator")
            dialogue_text = story_data["segments"][story_index]["text"]

            # 获取时长
            duration = segment.get("duration", 2000)  # 如果没有 duration, 默认 2秒
            tts_audio = load_or_create_tts(segment["file"], duration)
            final_audio += tts_audio

            # 添加字幕
            subtitles.append({
                "index": len(subtitles) + 1,
                "start": ms_to_srt_time(current_time),
                "end": ms_to_srt_time(current_time + len(tts_audio)),
                "speaker": speaker,
                "text": dialogue_text
            })

            current_time += len(tts_audio)
            story_index += 1  # 下一段对白

        # ----------------------
        # SFX
        # ----------------------
        elif seg_type == "sfx":
            path = segment["file"]
            if not os.path.exists(path):
                print(f"⚠ SFX 文件不存在 {path}")
                continue
            sfx = AudioSegment.from_file(path)
            final_audio += sfx
            current_time += len(sfx)

            # 不生成字幕，只更新时间

        # ----------------------
        # BGM
        # ----------------------
        elif seg_type == "bgm":
            path = segment["file"]
            if not os.path.exists(path):
                print(f"⚠ BGM 文件不存在 {path}")
                continue
            bgm_audio = AudioSegment.from_file(path)
            while len(bgm_audio) < len(final_audio):
                bgm_audio += bgm_audio
            final_audio = final_audio.overlay(bgm_audio[:len(final_audio)])

            # 不生成字幕，只更新时间
            current_time += len(bgm_audio)

        # ----------------------
        # pause
        # ----------------------
        elif seg_type == "pause":
            duration = segment.get("duration", 500)
            silence = AudioSegment.silent(duration=duration)
            final_audio += silence
            current_time += duration

            # 不生成字幕，只更新时间

    # 如果 BGM 比 final_audio 长，最后混入剩余部分
    if bgm_audio and len(final_audio) < len(bgm_audio):
        final_audio = final_audio.overlay(bgm_audio[:len(final_audio)])

    # 输出音频
    output_file = os.path.join(OUTPUT_DIR, "final_audio.wav")
    final_audio.export(output_file, format="wav")
    print("Final audio generated:", output_file)

    # 输出字幕 SRT
    srt_file = os.path.join(OUTPUT_DIR, SUBTITLE_FILE)
    with open(srt_file, "w", encoding="utf-8") as f:
        for sub in subtitles:
            f.write(f"{sub['index']}\n")
            f.write(f"{sub['start']} --> {sub['end']}\n")
            f.write(f"[{sub['speaker']}] {sub['text']}\n\n")

    print("Subtitle file generated:", srt_file)
    return output_file, srt_file