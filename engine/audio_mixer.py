import requests
import json
import os
import time
import hashlib
import shutil
import tempfile
import re
from pathlib import Path
from pydub import AudioSegment
from pydub.generators import Sine
from typing import Optional, Dict, List, Tuple, Union


class TTSCache:
    """TTS 文件缓存管理器 - 负责生成、缓存和清理临时文件"""
    
    def __init__(self, cache_dir: str = ".tts_cache", max_age_hours: int = 24):
        """
        初始化缓存管理器
        
        Args:
            cache_dir: 缓存目录路径
            max_age_hours: 缓存文件最大存活时间（小时）
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_age_seconds = max_age_hours * 3600
        
        # 会话缓存（当前任务使用的文件）
        self.session_files: List[Path] = []
        
    def _generate_key(self, text: str, speaker: str) -> str:
        """根据文本和说话人生成唯一缓存键"""
        content = f"{speaker}:{text}".encode('utf-8')
        return hashlib.md5(content).hexdigest()
    
    def _get_cache_path(self, text: str, speaker: str) -> Path:
        """获取缓存文件路径"""
        key = self._generate_key(text, speaker)
        return self.cache_dir / f"{key}.wav"
    
    def _is_cache_valid(self, cache_path: Path) -> bool:
        """检查缓存文件是否有效（存在且未过期）"""
        if not cache_path.exists():
            return False
        
        file_age = time.time() - cache_path.stat().st_mtime
        return file_age < self.max_age_seconds
    
    def get_cached(self, text: str, speaker: str) -> Optional[Path]:
        """获取缓存的TTS文件路径（如果存在且有效）"""
        cache_path = self._get_cache_path(text, speaker)
        
        if self._is_cache_valid(cache_path):
            print(f"✅ 使用缓存: {cache_path.name} (说话人: {speaker})")
            self.session_files.append(cache_path)  # 记录本次使用
            return cache_path
        
        return None
    
    def save_to_cache(self, text: str, speaker: str, audio_data: bytes) -> Path:
        """保存TTS音频数据到缓存"""
        cache_path = self._get_cache_path(text, speaker)
        
        # 确保目录存在
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入文件
        with open(cache_path, "wb") as f:
            f.write(audio_data)
        
        print(f"💾 已缓存: {cache_path.name} (说话人: {speaker})")
        self.session_files.append(cache_path)
        return cache_path
    
    def cleanup_old_cache(self, older_than_hours: Optional[int] = None) -> int:
        """清理过期缓存文件"""
        cutoff_time = time.time() - (older_than_hours or self.max_age_seconds)
        cleaned = 0
        
        for cache_file in self.cache_dir.glob("*.wav"):
            if cache_file.stat().st_mtime < cutoff_time:
                cache_file.unlink()
                cleaned += 1
        
        if cleaned > 0:
            print(f"🧹 已清理 {cleaned} 个过期缓存文件")
        return cleaned
    
    def clear_session(self):
        """清空会话记录（不删除文件）"""
        self.session_files.clear()
    
    def get_session_files(self) -> List[Path]:
        """获取本次会话使用的所有缓存文件"""
        return self.session_files.copy()


class AudioMixer:
    """音频混合器 - 负责TTS生成、音频混合和字幕生成"""
    
    def __init__(
        self, 
        api_url: str = "http://localhost:8080/v1/tts",
        cache_dir: str = ".tts_cache",
        cache_hours: int = 24,
        temp_dir: Optional[str] = None,
        default_speaker: str = "qushuai"
    ):
        """
        初始化音频混合器
        
        Args:
            api_url: Fish-Speech API 地址
            cache_dir: 缓存目录
            cache_hours: 缓存保留时间（小时）
            temp_dir: 临时目录（如果不指定，自动创建）
            default_speaker: 默认说话人ID
        """
        self.api_url = api_url
        self.cache = TTSCache(cache_dir, cache_hours)
        self.default_speaker = default_speaker
        
        # 临时目录管理
        self._temp_dir = temp_dir
        self._own_temp_dir = False
        
        if self._temp_dir is None:
            # 自动创建临时目录
            self._temp_dir = tempfile.mkdtemp(prefix="fish_mixer_")
            self._own_temp_dir = True
        
        self.temp_dir = Path(self._temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"📁 临时目录: {self.temp_dir}")
        print(f"🎤 默认说话人: {self.default_speaker}")
        
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口 - 自动清理"""
        self.cleanup()
    
    def cleanup(self):
        """清理临时文件和过期缓存"""
        # 清理临时目录
        if self._own_temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            print(f"🧹 已清理临时目录: {self.temp_dir}")
        
        # 清理过期缓存
        self.cache.cleanup_old_cache()
        
        # 清空会话
        self.cache.clear_session()
    
    def generate_placeholder(self, duration: int = 2000) -> AudioSegment:
        """生成占位音频（当API调用失败时使用）"""
        tone = Sine(440)
        audio = tone.to_audio_segment(duration=duration)
        return (audio - 10)[:duration]
    
    def parse_speaker_from_text(self, text: str) -> Tuple[str, Optional[str]]:
        """
        从文本中解析speaker标记
        
        支持的格式：
        - "<speaker:qushuai> 你好啊" -> 返回 ("你好啊", "qushuai")
        - "[speaker:male_voice] 你好" -> 返回 ("你好", "male_voice")
        - "【speaker:female_voice】你好" -> 返回 ("你好", "female_voice")
        - "{speaker:ghost_voice} 你好" -> 返回 ("你好", "ghost_voice")
        - "你好啊" -> 返回 ("你好啊", None)
        
        Returns:
            (纯文本, speaker或None)
        """
        if not text:
            return text, None
        
        # 多种标记格式支持
        patterns = [
            (r'<speaker:([^>]+)>\s*(.*)', 1, 2),     # <speaker:xxx> 文本
            (r'\[speaker:([^\]]+)\]\s*(.*)', 1, 2),  # [speaker:xxx] 文本
            (r'【speaker:([^】]+)】\s*(.*)', 1, 2),   # 【speaker:xxx】文本
            (r'\{speaker:([^\}]+)\}\s*(.*)', 1, 2),  # {speaker:xxx} 文本
            (r'@speaker:([^\s]+)\s+(.*)', 1, 2),     # @speaker:xxx 文本
        ]
        
        for pattern, speaker_group, text_group in [(p[0], 1, 2) for p in patterns]:
            match = re.match(pattern, text.strip())
            if match:
                speaker = match.group(1).strip()
                pure_text = match.group(2).strip()
                return pure_text, speaker
        
        # 没有匹配到，返回原文本
        return text, None
    
    def synthesize_text(
        self, 
        text: str, 
        speaker: Optional[str] = None,
        force_refresh: bool = False,
        **kwargs
    ) -> Tuple[bool, Optional[AudioSegment], Optional[Path]]:
        """
        通过API合成语音 - 支持从文本解析speaker
        
        Args:
            text: 要合成的文本，可包含speaker标记如 "<speaker:qushuai> 你好"
            speaker: 直接指定说话人（优先级高于解析）
            force_refresh: 强制刷新（不使用缓存）
            **kwargs: 额外的API参数
        
        Returns:
            (success, audio_segment, file_path)
        """
        # 1. 从文本解析speaker
        pure_text, parsed_speaker = self.parse_speaker_from_text(text)
        
        # 2. 确定最终的说话人（优先级：参数 > 解析 > 默认）
        actual_speaker = speaker or parsed_speaker or self.default_speaker
        
        # 3. 如果解析出了speaker，打印信息
        if parsed_speaker:
            print(f"📝 解析到说话人: {parsed_speaker}")
        if pure_text != text:
            print(f"📝 纯文本: {pure_text[:50]}...")
        
        # 4. 检查缓存
        if not force_refresh:
            cached_path = self.cache.get_cached(pure_text, actual_speaker)
            if cached_path:
                try:
                    audio = AudioSegment.from_file(cached_path)
                    return True, audio, cached_path
                except Exception as e:
                    print(f"⚠ 缓存文件损坏: {e}")
        
        # 5. 构建请求参数
        payload = {
            "text": pure_text,
            "reference_id": actual_speaker,
            "format": "wav",
            "max_new_tokens": 1024,
            "top_p": 0.3,              # 很低，严格采样
            "temperature": 0.2,         # 很低，确定性高
            "repetition_penalty": 1.8,  # 很高，避免重复
            "seed": 42
        }

        headers = {"Content-Type": "application/json"}
        
        try:
            # 发送请求
            response = requests.post(
                self.api_url, 
                json=payload, 
                headers=headers, 
                timeout=120
            )
            
            if response.status_code == 200:
                # 保存到缓存（用纯文本和实际说话人）
                cache_path = self.cache.save_to_cache(pure_text, actual_speaker, response.content)
                
                # 加载音频
                audio = AudioSegment.from_file(cache_path)
                return True, audio, cache_path
            else:
                print(f"❌ API错误 {response.status_code}: {response.text}")
                return False, None, None
                
        except requests.exceptions.Timeout:
            print(f"❌ API请求超时")
            return False, None, None
        except Exception as e:
            print(f"❌ API请求异常: {str(e)}")
            return False, None, None
    
    def ms_to_srt_time(self, ms: int) -> str:
        """毫秒转SRT时间格式"""
        hours = ms // 3600000
        minutes = (ms % 3600000) // 60000
        seconds = (ms % 60000) // 1000
        milliseconds = ms % 1000
        return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"
    
    def mix_audio(
        self,
        story_json_path: Union[str, Path],
        audio_plan_path: Union[str, Path],
        task_dir: Union[str, Path],
        default_speaker: Optional[str] = None,
        bgm_volume_reduction: int = 10,
        cleanup_after: bool = True
    ) -> Tuple[Path, Path]:
        """
        生成最终音频并输出标准SRT字幕
        
        Args:
            story_json_path: 故事JSON文件路径
            audio_plan_path: 音频计划JSON文件路径
            task_dir: 任务输出目录
            default_speaker: 默认说话人ID（覆盖初始化时的设置）
            bgm_volume_reduction: BGM音量降低分贝数
            cleanup_after: 是否在完成后清理临时文件
        
        Returns:
            (audio_file_path, srt_file_path)
        """
        
        # 使用默认说话人
        active_default_speaker = default_speaker or self.default_speaker
        
        # 转换为Path对象
        story_json_path = Path(story_json_path)
        audio_plan_path = Path(audio_plan_path)
        task_dir = Path(task_dir)
        
        # 创建输出目录
        audio_dir = task_dir / "audio"
        subtitle_dir = task_dir / "subtitle"
        audio_dir.mkdir(parents=True, exist_ok=True)
        subtitle_dir.mkdir(parents=True, exist_ok=True)
        
        # 任务临时目录（用于存放本次生成的临时文件）
        task_temp_dir = self.temp_dir / f"task_{int(time.time())}"
        task_temp_dir.mkdir(exist_ok=True)
        
        try:
            # 读取数据
            with open(audio_plan_path, "r", encoding="utf-8") as f:
                audio_plan = json.load(f)
            
            with open(story_json_path, "r", encoding="utf-8") as f:
                story_data = json.load(f)
            
            # 初始化
            final_audio = AudioSegment.silent(duration=0)
            bgm_audio = None
            subtitles = []
            current_time = 0
            story_index = 0
            
            print(f"🎬 开始处理音频计划，共 {len(audio_plan)} 个片段")
            print(f"🎤 默认说话人: {active_default_speaker}")
            
            # 处理每个片段
            for seg_idx, segment in enumerate(audio_plan):
                seg_type = segment["type"]
                
                # ---------------- dialogue ----------------
                if seg_type == "dialogue":
                    # 获取对话文本
                    dialogue_text = ""
                    while story_index < len(story_data["segments"]):
                        s = story_data["segments"][story_index]
                        story_index += 1
                        if s.get("type") == "dialogue" and s.get("text"):
                            dialogue_text = s["text"]
                            break
                    
                    if not dialogue_text:
                        print(f"⚠ 片段 {seg_idx}: 未找到对话文本")
                        continue
                    
                    # 获取音色ID（可从segment中指定，但优先从文本解析）
                    segment_speaker = segment.get("speaker")
                    
                    # 获取时长（默认2秒）
                    duration = segment.get("duration", 2000)
                    
                    print(f"🎤 [{seg_idx}] 处理: {dialogue_text[:50]}...")
                    
                    # 生成TTS（文本可能自带speaker标记）
                    success, tts_audio, cache_path = self.synthesize_text(
                        text=dialogue_text,
                        speaker=segment_speaker,  # 如果segment指定了speaker，会覆盖文本解析的
                        force_refresh=False
                    )
                    
                    if not success or tts_audio is None:
                        print(f"⚠ 使用占位音频替代")
                        tts_audio = self.generate_placeholder(duration)
                    
                    # 添加到最终音频
                    final_audio += tts_audio
                    
                    # 生成字幕（用原始文本，但去掉speaker标记）
                    pure_text, _ = self.parse_speaker_from_text(dialogue_text)
                    if pure_text.strip() and pure_text != "None":
                        subtitles.append({
                            "index": len(subtitles) + 1,
                            "start": self.ms_to_srt_time(current_time),
                            "end": self.ms_to_srt_time(current_time + len(tts_audio)),
                            "text": pure_text
                        })
                    
                    current_time += len(tts_audio)
                
                # ---------------- sfx ----------------
                elif seg_type == "sfx":
                    path = segment.get("file")
                    
                    if path and Path(path).exists():
                        sfx = AudioSegment.from_file(path)
                        print(f"🔊 [{seg_idx}] 添加音效: {Path(path).name}")
                    else:
                        print(f"⚠ [{seg_idx}] 音效文件不存在: {path}")
                        sfx = AudioSegment.silent(duration=segment.get("duration", 500))
                    
                    final_audio += sfx
                    current_time += len(sfx)
                
                # ---------------- bgm ----------------
                elif seg_type == "bgm":
                    path = segment.get("file")
                    
                    if path and Path(path).exists():
                        bgm_audio = AudioSegment.from_file(path) - bgm_volume_reduction
                        print(f"🎵 [{seg_idx}] 加载BGM: {Path(path).name}")
                    else:
                        print(f"⚠ [{seg_idx}] BGM文件不存在: {path}")
                        bgm_audio = None
                
                # ---------------- pause ----------------
                elif seg_type == "pause":
                    duration = segment.get("duration", 500)
                    silence = AudioSegment.silent(duration=duration)
                    final_audio += silence
                    current_time += duration
                    print(f"⏸️ [{seg_idx}] 添加静音: {duration}ms")
            
            # 叠加BGM
            if bgm_audio:
                print("🎵 叠加背景音乐...")
                loop_count = (len(final_audio) // len(bgm_audio)) + 1
                bgm_loop = bgm_audio * loop_count
                final_audio = final_audio.overlay(bgm_loop[:len(final_audio)])
            
            # 输出最终音频
            output_file = audio_dir / "final_audio.wav"
            final_audio.export(output_file, format="wav")
            print(f"✅ 最终音频已生成: {output_file}")
            
            # 输出字幕文件
            srt_file = subtitle_dir / "subtitle.srt"
            with open(srt_file, "w", encoding="utf-8") as f:
                for sub in subtitles:
                    f.write(f"{sub['index']}\n")
                    f.write(f"{sub['start']} --> {sub['end']}\n")
                    f.write(f"{sub['text']}\n\n")
            print(f"✅ 字幕文件已生成: {srt_file}")
            print(f"📊 统计: 共 {len(subtitles)} 条字幕, 总时长 {current_time/1000:.2f}秒")
            
            return output_file, srt_file
            
        finally:
            # 清理任务临时文件
            if cleanup_after and task_temp_dir.exists():
                shutil.rmtree(task_temp_dir)
                print(f"🧹 已清理任务临时文件")
    
    def get_cache_stats(self) -> Dict:
        """获取缓存统计信息"""
        cache_files = list(self.cache.cache_dir.glob("*.wav"))
        total_size = sum(f.stat().st_size for f in cache_files)
        
        return {
            "cache_dir": str(self.cache.cache_dir),
            "file_count": len(cache_files),
            "total_size_mb": total_size / (1024 * 1024),
            "oldest_file": min(f.stat().st_mtime for f in cache_files) if cache_files else None,
            "newest_file": max(f.stat().st_mtime for f in cache_files) if cache_files else None,
        }


# ==================== 使用示例 ====================

def main():
    """使用示例"""
    
    # 创建音频混合器（使用上下文管理器自动清理）
    with AudioMixer(
        api_url="http://localhost:8080/v1/tts",
        cache_dir=".tts_cache",
        cache_hours=48,  # 缓存保留48小时
        default_speaker="qushuai"  # 设置默认说话人
    ) as mixer:
        
        # 示例1：直接调用，文本带speaker标记
        print("\n=== 示例1: 文本带speaker标记 ===")
        success, audio, path = mixer.synthesize_text(
            text="<speaker:male_voice> 你好，我是男声"
        )
        
        # 示例2：指定speaker参数
        print("\n=== 示例2: 指定speaker参数 ===")
        success, audio, path = mixer.synthesize_text(
            text="你好，我是女声",
            speaker="female_voice"
        )
        
        # 示例3：混合使用（参数优先级更高）
        print("\n=== 示例3: 混合使用 ===")
        success, audio, path = mixer.synthesize_text(
            text="<speaker:male_voice> 你好",
            speaker="female_voice"  # 这个会覆盖文本中的 male_voice
        )
        
        # 示例4：处理一个完整的任务
        print("\n=== 示例4: 完整任务 ===")
        
        # 创建示例数据
        os.makedirs("data", exist_ok=True)
        
        with open("data/story.json", "w") as f:
            json.dump({
                "segments": [
                    {"type": "dialogue", "text": "<speaker:male_voice> 欢迎收听今天的新闻"},
                    {"type": "dialogue", "text": "<speaker:female_voice> 接下来是天气预报"},
                    {"type": "dialogue", "text": "我是默认说话人"},  # 会用 qushuai
                ]
            }, f, ensure_ascii=False)
        
        with open("data/audio_plan.json", "w") as f:
            json.dump([
                {"type": "dialogue", "duration": 3000},
                {"type": "dialogue", "duration": 2500},
                {"type": "dialogue", "duration": 2000}
            ], f, ensure_ascii=False)
        
        # 执行任务
        output_audio, output_srt = mixer.mix_audio(
            story_json_path="data/story.json",
            audio_plan_path="data/audio_plan.json",
            task_dir="output/task_001"
        )
        
        # 查看缓存统计
        stats = mixer.get_cache_stats()
        print(f"\n📊 缓存统计:")
        print(f"  缓存目录: {stats['cache_dir']}")
        print(f"  文件数量: {stats['file_count']}")
        print(f"  总大小: {stats['total_size_mb']:.2f} MB")


# 不使用上下文管理器的手动方式
def manual_usage():
    """手动管理资源"""
    
    mixer = AudioMixer(
        api_url="http://localhost:8080/v1/tts",
        cache_dir=".tts_cache",
        default_speaker="male"
    )
    
    try:
        # 执行任务
        mixer.mix_audio(
            story_json_path="data/story.json",
            audio_plan_path="data/audio_plan.json",
            task_dir="output/task_002"
        )
    finally:
        # 手动清理
        mixer.cleanup()


# 兼容旧代码的接口
def mix_audio(story_json_path, audio_plan_path, task_dir, **kwargs):
    """兼容旧版本的函数调用"""
    with AudioMixer(**kwargs) as mixer:
        return mixer.mix_audio(story_json_path, audio_plan_path, task_dir)


if __name__ == "__main__":
    main()