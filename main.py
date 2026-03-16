import os
import uuid
import yaml
import json
import sys

from story_engine.story_generator import StoryGenerator
from story_engine.prompt_manager import PromptManager
from parser.tag_parser import TagParser

from storage.story_repository import StoryRepository
from storage.audio_plan_repository import save_audio_plan

from engine.audio_plan_builder import build_audio_plan
from engine.audio_mixer import mix_audio
from engine.timeline_engine import build_timeline


# ------------------------
# 读取配置
# ------------------------
def load_config():
    with open("config/config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ------------------------
# 创建任务目录
# ------------------------
def create_task_dir():

    task_id = str(uuid.uuid4())[:8]

    task_dir = os.path.join("output", "tasks", task_id)

    os.makedirs(task_dir, exist_ok=True)
    os.makedirs(os.path.join(task_dir, "story"), exist_ok=True)
    os.makedirs(os.path.join(task_dir, "audio_plan"), exist_ok=True)
    os.makedirs(os.path.join(task_dir, "audio"), exist_ok=True)
    os.makedirs(os.path.join(task_dir, "subtitle"), exist_ok=True)
    os.makedirs(os.path.join(task_dir, "timeline"), exist_ok=True)

    return task_id, task_dir


# ------------------------
# 主流程
# ------------------------
def main():

    print("AI Horror Story Factory\n")

    config = load_config()

    task_id, task_dir = create_task_dir()

    print("Task ID:", task_id)
    print("Task Dir:", task_dir)
    print()

    story_file = os.path.join(task_dir, "story", "story.json")
    audio_plan_file = os.path.join(task_dir, "audio_plan", "audio_plan.json")
    timeline_file = os.path.join(task_dir, "timeline", "timeline.json")

    # ------------------------
    # 1 判断是否有外部故事
    # ------------------------

    if len(sys.argv) > 1:

        story_path = sys.argv[1]

        print("Using external story file:")
        print(story_path)

        with open(story_path, "r", encoding="utf-8") as f:
            story_text = f.read()

    else:

        print("Generating story with AI...")

        generator = StoryGenerator(config)

        prompt = PromptManager.build_prompt()

        story_text = generator.generate(prompt)

    print("\nStory text:\n")
    print(story_text)
    print()

    # ------------------------
    # 2 解析标签
    # ------------------------

    parser = TagParser()

    title, segments = parser.parse(story_text)

    print("Parsed segments:")
    print(segments)
    print()

    # ------------------------
    # 3 保存 Story JSON
    # ------------------------

    repo = StoryRepository()

    story_path = repo.save(title, segments, story_file)

    print("Story JSON saved:")
    print(story_path)
    print()

    # ------------------------
    # 4 生成 Audio Plan
    # ------------------------

    print("Building audio plan...")

    story_data = {
        "segments": segments
    }

    audio_plan = build_audio_plan(story_data)

    audio_plan_path = save_audio_plan(audio_plan, audio_plan_file)

    print("Audio plan saved:")
    print(audio_plan_path)
    print()

    # ------------------------
    # 5 构建 Timeline
    # ------------------------

    print("Building timeline...")

    timeline = build_timeline(story_path, audio_plan_path)

    with open(timeline_file, "w", encoding="utf-8") as f:
        json.dump(timeline, f, indent=2, ensure_ascii=False)

    print("Timeline saved:")
    print(timeline_file)
    print()

    # ------------------------
    # 6 混音
    # ------------------------

    print("Mixing audio...")

    final_audio, subtitle_file, cover_file,video_file= mix_audio(
        story_path,
        audio_plan_path,
        task_dir,
        generate_cover=True,        # 生成封面
        generate_video=True,         # 生成视频
        video_params={                # 视频参数
            "min_images": 6,
            "max_images_per_sec": 0.1,
            "transition_sec": 1.2,
            "ken_burns_zoom": 0.0007,
            "resolution": (1080, 1920)
        }
    )

    print("\nAudio generated:")
    print(final_audio)

    print("\nSubtitle generated:")
    print(subtitle_file)

    print("\nTask completed!")

    print("\nAll outputs in:")
    print(task_dir)


# ------------------------
# 程序入口
# ------------------------
if __name__ == "__main__":
    main()