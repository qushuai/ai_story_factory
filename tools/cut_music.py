import os
from pydub import AudioSegment

# --------------------------
# 强制 PATH 包含 ffmpeg / ffprobe 所在目录
# --------------------------
ffmpeg_dir = "/Users/shuaiqu/Desktop/auto_system"
os.environ["PATH"] += os.pathsep + ffmpeg_dir

# --------------------------
# 指定可执行文件全路径
# --------------------------
AudioSegment.converter = os.path.join(ffmpeg_dir, "ffmpeg")
AudioSegment.ffprobe   = os.path.join(ffmpeg_dir, "ffprobe")

# --------------------------
# 测试加载音频
# --------------------------
test_file = "/Users/shuaiqu/Desktop/auto_system/ai_story_factory/assets/ori_sfx/mixkit-horror-sci-fi-wind-tunnel-894.wav"
audio = AudioSegment.from_file(test_file)
print(f"[OK] 音频长度: {len(audio)}ms")
# ---------------------------
# 配置
# ---------------------------
project_dir = "/Users/shuaiqu/Desktop/auto_system/ai_story_factory/assets"
sfx_input_dir = "/Users/shuaiqu/Desktop/auto_system/ai_story_factory/assets/ori_sfx"   # 你下载的原始音效文件夹
bgm_input_dir = "/Users/shuaiqu/Desktop/auto_system/ai_story_factory/assets/ori_sfx"   # 原始 BGM 文件夹


# SFX 裁剪时长（毫秒）
SFX_DURATION = 2000   # 默认 2 秒
# BGM 裁剪时长（毫秒）
BGM_DURATION = 8000   # 默认 8 秒
sfx_output_dir = os.path.join(project_dir, "sfx") 
bgm_output_dir = os.path.join(project_dir, "bgm")
# 确保输出目录存在
os.makedirs(sfx_output_dir, exist_ok=True)
os.makedirs(bgm_output_dir, exist_ok=True)

# ---------------------------
# 工具函数
# ---------------------------
def process_file(input_path, output_path, duration_ms):
    # 自动加载 mp3 / wav
    audio = AudioSegment.from_file(input_path)
    # 如果音频比裁剪短，直接用原长度
    duration_ms = min(duration_ms, len(audio))
    trimmed = audio[:duration_ms]
    # 导出 wav
    trimmed.export(output_path, format="wav")
    print(f"[OK] {input_path} → {output_path} ({duration_ms}ms)")

# ---------------------------
# 处理 SFX
# ---------------------------
print("处理 SFX 音效...")
for filename in os.listdir(sfx_input_dir):
    if not filename.lower().endswith((".wav", ".mp3")):
        continue
    input_path = os.path.join(sfx_input_dir, filename)
    name, _ = os.path.splitext(filename)
    output_path = os.path.join(sfx_output_dir, f"{name}.wav")
    process_file(input_path, output_path, SFX_DURATION)

# ---------------------------
# 处理 BGM
# ---------------------------
print("处理 BGM 音效...")
for filename in os.listdir(bgm_input_dir):
    if not filename.lower().endswith((".wav", ".mp3")):
        continue
    input_path = os.path.join(bgm_input_dir, filename)
    name, _ = os.path.splitext(filename)
    output_path = os.path.join(bgm_output_dir, f"{name}.wav")
    process_file(input_path, output_path, BGM_DURATION)

print("处理完成！")