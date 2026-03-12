import yaml

from story_engine.story_generator import StoryGenerator
from story_engine.prompt_manager import PromptManager
from parser.tag_parser import TagParser

from storage.story_repository import StoryRepository
from storage.audio_plan_repository import save_audio_plan

from engine.audio_plan_builder import build_audio_plan
from engine.audio_mixer import mix_audio

def load_config():

    with open("config/config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():

    print("AI Horror Story Factory")

    # ------------------------
    # 1 读取配置
    # ------------------------

    config = load_config()

    # ------------------------
    # 2 生成故事
    # ------------------------

    generator = StoryGenerator(config)

    prompt = PromptManager.build_prompt()

    print("Generating story...")

    story_text = generator.generate(prompt)

    print("Story generated")

    print(story_text)

    # ------------------------
    # 3 解析标签
    # ------------------------

    parser = TagParser()

    segments = parser.parse(story_text)

    # ------------------------
    # 4 保存 story.json
    # ------------------------

    repo = StoryRepository()

    story_path = repo.save(segments)

    print("Story JSON saved:")

    print(story_path)

    # ------------------------
    # 5 生成 Audio Plan
    # ------------------------

    print("Building audio plan...")

    story_data = {
        "segments": segments
    }

    audio_plan = build_audio_plan(story_data)

    audio_plan_path = save_audio_plan(audio_plan)

    print("Audio plan saved:")

    print(audio_plan_path)
    
    print("Mixing audio...")

    final_audio = mix_audio(audio_plan_path)

    print("Audio file:")

    print(final_audio)

if __name__ == "__main__":
    main()