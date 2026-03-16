import ffmpeg
from pathlib import Path
import random
import re
import subprocess
import shutil
from typing import Optional


def extract_scene_tag(title: str) -> str:
    """
    从标题提取场景标签，例如 "[midnight_elevator] ..." → "midnight_elevator"
    没找到返回 "fallback"
    """
    match = re.match(r'\[([^\]]+)\]', title.strip())
    if match:
        return match.group(1).strip().lower()
    return "fallback"


def select_images(
    image_base_dir: Path,
    scene_tag: str,
    num_needed: int,
    fallback_tag: str = "fallback"
) -> list[Path]:
    """
    根据场景标签选择图片文件夹，随机选 num_needed 张（不足则循环）
    """
    folder = image_base_dir / scene_tag
    if not folder.exists() or not folder.is_dir():
        print(f"警告: 场景文件夹不存在 {folder}，使用 fallback")
        folder = image_base_dir / fallback_tag
        if not folder.exists():
            raise FileNotFoundError(f"无可用图片文件夹: {scene_tag} 或 fallback")

    images = list(folder.glob("*.[jJ][pP][gG]")) + list(folder.glob("*.[jJ][pP][eE][gG]")) + list(folder.glob("*.[pP][nN][gG]"))
    if not images:
        raise FileNotFoundError(f"文件夹 {folder} 无 jpg/jpeg/png 图片")

    # 随机排序 + 循环取图
    random.shuffle(images)
    selected = []
    for i in range(num_needed):
        selected.append(images[i % len(images)])
    
    print(f"从 {folder.name} 选择了 {len(selected)} 张图片（循环使用）")
    return selected


def create_video(
    audio_path: str | Path,
    srt_path: str | Path,
    image_base_dir: str | Path,
    title: str,
    output_path: str | Path,
    min_images: int = 5,
    max_images_per_sec: float = 0.12,   # ≈ 每 8 秒换 1 张图
    transition_sec: float = 1.2,        # 渐变时长
    ken_burns_zoom: float = 0.0008,     # 每帧缩放幅度（轻微呼吸感）
    resolution: tuple = (1080, 1920),   # 竖屏
):
    """
    主函数：根据音频时长、标题、SRT 自动生成带转场和字幕的恐怖视频
    """
    audio_path = Path(audio_path)
    srt_path = Path(srt_path)
    image_base_dir = Path(image_base_dir)
    output_path = Path(output_path)

    if not audio_path.exists():
        raise FileNotFoundError(f"音频不存在: {audio_path}")
    if not srt_path.exists():
        raise FileNotFoundError(f"SRT 不存在: {srt_path}")

    # 获取音频时长（秒）
    probe = ffmpeg.probe(str(audio_path))
    duration_sec = float(probe['format']['duration'])
    print(f"音频时长: {duration_sec:.2f} 秒")

    # 计算需要多少张图
    num_images = max(min_images, int(duration_sec * max_images_per_sec))
    print(f"计划使用 {num_images} 张图片")

    # 提取场景并选图
    scene_tag = extract_scene_tag(title)
    selected_images = select_images(image_base_dir, scene_tag, num_images)

    # 每张图显示时长（平均分配）
    duration_per_image = duration_sec / len(selected_images)
    print(f"每张图片显示时长: {duration_per_image:.2f} 秒")
    print(f"转场时长: {transition_sec} 秒")

    # 创建临时目录
    temp_dir = Path("temp_frames")
    temp_dir.mkdir(exist_ok=True)
    
    try:
        print("开始生成视频...")
        
        # 设置帧率
        fps = 25
        
        # 使用命令行方式生成视频片段
        print("使用命令行方式生成视频片段...")
        
        # 为每张图片生成视频片段
        video_segments = []
        for i, img_path in enumerate(selected_images):
            temp_video = temp_dir / f"segment_{i:03d}.mp4"
            video_segments.append(temp_video)
            
            # 计算每张片段的时长
            segment_duration = duration_per_image + transition_sec
            
            # 构建滤镜字符串
            filter_complex = (
                f"[0:v]scale={resolution[0]}:{resolution[1]}:force_original_aspect_ratio=decrease,"
                f"pad={resolution[0]}:{resolution[1]}:(ow-iw)/2:(oh-ih)/2:color=black,"
                f"zoompan=z='1+{ken_burns_zoom}*on':d={int(fps*segment_duration)}:s={resolution[0]}x{resolution[1]}:fps={fps}[v]"
            )
            
            # 使用 subprocess 调用 ffmpeg
            cmd = [
                'ffmpeg',
                '-y',
                '-loop', '1',
                '-i', str(img_path),
                '-t', str(segment_duration),
                '-filter_complex', filter_complex,
                '-map', '[v]',
                '-vcodec', 'libx264',
                '-pix_fmt', 'yuv420p',
                '-crf', '23',
                '-preset', 'medium',
                '-r', str(fps),
                str(temp_video)
            ]
            
            print(f"  生成片段 {i+1}/{len(selected_images)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"  ❌ 片段 {i+1} 生成失败:")
                print(result.stderr)
                raise Exception(f"片段生成失败: {result.stderr}")
        
        print("所有片段生成完成，开始合并...")
        
        # 创建 concat 文件列表
        concat_file = temp_dir / "concat_list.txt"
        with open(concat_file, 'w') as f:
            for seg in video_segments:
                f.write(f"file '{seg.absolute()}'\n")
        
        # ===== 修改字幕样式 - 更小、更靠下 =====
        # 使用 ASS 字幕样式（更精确的控制）
        subtitle_style = (
            "FontName=Arial,"           # 字体
            "FontSize=16,"               # 字体大小（进一步减小到18）
            "PrimaryColour=&HFFFFFF&,"   # 白色
            "OutlineColour=&H000000&,"   # 黑色描边
            "BackColour=&H80000000&,"    # 半透明背景
            "BorderStyle=1,"              # 边框样式1（只有轮廓）
            "Outline=1,"                  # 描边宽度
            "Shadow=0,"                   # 关闭阴影（减少占用空间）
            "Alignment=2,"                # 底部居中
            "MarginL=40,"                  # 左边距
            "MarginR=40,"                  # 右边距
            "MarginV=50"                  # 底部边距（增加到底部150像素）
        )
        
        # 合并所有片段并添加音频和字幕
        output_cmd = [
            'ffmpeg',
            '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(concat_file),
            '-i', str(audio_path),
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-pix_fmt', 'yuv420p',
            '-preset', 'medium',
            '-crf', '23',
            '-vf', f"subtitles={str(srt_path)}:force_style='{subtitle_style}'",
            '-shortest',
            str(output_path)
        ]
        
        print("合并视频、添加音频和字幕...")
        result = subprocess.run(output_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print("❌ 合并失败:")
            print(result.stderr)
            raise Exception(f"合并失败: {result.stderr}")
        
        print(f"✅ 视频生成完成: {output_path}")
        print(f"   分辨率: {resolution[0]}x{resolution[1]}，时长 ≈ {duration_sec:.1f}秒")
        print(f"   使用图片: {len(selected_images)} 张")
        print(f"   字幕大小: 18px，底部边距: 50px")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        if 'result' in locals() and hasattr(result, 'stderr'):
            print(result.stderr)
    finally:
        # 清理临时文件
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            print(f"🧹 已清理临时文件")


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 示例调用
    create_video(
        audio_path="output_audio.wav",
        srt_path="output/tasks/1a8e65f2/subtitle/subtitle.srt",
        image_base_dir="assets/images",
        title="[house] 电梯停在13层，门缝里伸出一只烧焦的手",
        output_path="final_video.mp4",
        min_images=6,
        max_images_per_sec=0.1,      # ≈ 每10秒换一张
        transition_sec=1.2,
        ken_burns_zoom=0.0007,
    )