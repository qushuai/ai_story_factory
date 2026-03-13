AI Horror Story Factory

一个 AI自动恐怖故事生产系统。

系统可以自动：

生成恐怖小说

解析结构化标签

生成音频计划

自动混音

自动生成字幕

最终输出 带配音的恐怖故事音频，后续可扩展生成 短视频内容。

项目目标

构建一个 AI内容生产流水线（AI Content Pipeline），实现：

AI生成故事
      ↓
标签解析
      ↓
音频计划
      ↓
时间轴
      ↓
音频合成
      ↓
字幕生成
      ↓
（未来）
视频生成

目标是打造一个 自动化恐怖故事内容工厂。

项目结构
ai_story_factory/

config/
    config.yaml

core/

engine/
    audio_plan_builder.py
    audio_mixer.py
    timeline_engine.py

parser/
    tag_parser.py

story_engine/
    story_generator.py
    prompt_manager.py

storage/
    story_repository.py
    audio_plan_repository.py

assets/
    sfx/
    bgm/

output/
    tasks/

main.py
requirements.txt
README.md
系统架构

核心流水线：

StoryGenerator
        ↓
TagParser
        ↓
StoryRepository
        ↓
AudioPlanBuilder
        ↓
TimelineEngine
        ↓
AudioMixer
        ↓
Subtitle (SRT)
标签语法

AI生成的故事必须使用结构化标签。

角色
[SPEAKER:narrator]
[SPEAKER:ghost]
[SPEAKER:child]

示例：

[SPEAKER:narrator]
灯忽然灭了。
音效
[SFX:door]
[SFX:footstep]
[SFX:heartbeat]
[SFX:whisper]

示例：

[SFX:footstep]
停顿
[PAUSE:600]

单位：毫秒

示例故事
[SPEAKER:narrator]
地下停车场很安静。

[SFX:footstep]

[SPEAKER:narrator]
脚步声却越来越近。

[PAUSE:800]

[SPEAKER:ghost]
你看见我了吗。
输出结构

每次运行生成一个任务目录：

output/tasks/{task_id}/

story.json
audio_plan.json

timeline/
    timeline.json

audio/
    final_audio.wav

subtitle/
    subtitle.srt
运行项目
1 安装依赖
pip install -r requirements.txt
2 运行系统
python main.py

运行后会自动：

生成故事

解析标签

构建音频计划

混音

生成字幕

示例输出
output/tasks/7c3f5e3e/

audio/final_audio.wav
subtitle/subtitle.srt
timeline/timeline.json
技术栈

Python

pydub

YAML

LLM（DeepSeek / OpenAI）

未来计划

计划增加以下能力：

AI语音

接入：

Fish Speech

ChatTTS

实现真实角色配音。

AI绘图

接入：

Fooocus

Stable Diffusion

自动生成故事画面。

视频生成

使用：

FFmpeg

自动生成恐怖故事短视频。

最终目标

实现一键生成：

恐怖故事短视频

流程：

AI生成故事
      ↓
AI配音
      ↓
AI绘图
      ↓
视频合成
      ↓
自动发布

打造一个 AI Horror Content Factory。

License

MIT License

作者

qushuai