"""
auto_sfx_downloader.py
自动从 Freesound 下载恐怖音效（增强版）
"""

import os
import requests
import time
from pathlib import Path
import json
from typing import Dict, List, Optional
import argparse

class AutoSFXDownloader:
    """自动恐怖音效下载器"""
    
    def __init__(self, api_key: str = None):
        """
        初始化下载器
        
        Args:
            api_key: Freesound API密钥
        """
        self.api_key = api_key
        if not self.api_key:
            self.api_key = input("请输入你的Freesound API密钥: ").strip()
        
        self.base_url = "https://freesound.org/apiv2"
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Token {self.api_key}"})
        
        # 恐怖音效搜索配置 - 每个分类多准备几个关键词
        self.categories = {
            "ambient": {
                "keywords": [
                    "horror ambient", "creepy atmosphere", "scary background",
                    "eerie ambiance", "haunted atmosphere", "dark ambiance"
                ],
                "description": "环境氛围音（风声、嗡鸣）",
                "target": 2
            },
            "heartbeat": {
                "keywords": [
                    "heartbeat scary", "fear heartbeat", "tension heartbeat",
                    "pulse horror", "heart thump"
                ],
                "description": "心跳声",
                "target": 1
            },
            "door": {
                "keywords": [
                    "door creak horror", "scary door", "creaking door",
                    "haunted door", "door open creepy"
                ],
                "description": "门声",
                "target": 1
            },
            "footstep": {
                "keywords": [
                    "footsteps horror", "scary footsteps", "creepy walk",
                    "footsteps on wood", "ghost footsteps"
                ],
                "description": "脚步声",
                "target": 1
            },
            "jump": {
                "keywords": [
                    "jump scare", "horror scream", "scary scream",
                    "fear scream", "horror sting"
                ],
                "description": "惊吓音",
                "target": 1
            },
            "monster": {
                "keywords": [
                    "monster growl", "demon voice", "evil laugh",
                    "creature roar", "beast sound"
                ],
                "description": "怪物音",
                "target": 1
            },
            "whisper": {
                "keywords": [
                    "ghost whisper", "scary whisper", "evil whisper",
                    "demonic whisper", "creepy voice"
                ],
                "description": "低语声",
                "target": 1
            },
            "metal": {
                "keywords": [
                    "scary metal", "creepy chain", "metal scrape",
                    "rusty gate", "metal drag"
                ],
                "description": "金属音",
                "target": 1
            },
            "wind": {
                "keywords": [
                    "scary wind", "haunted wind", "eerie wind",
                    "howling wind", "ghost wind"
                ],
                "description": "风声",
                "target": 1
            }
        }
        
        # 创建目录结构
        self.sfx_dir = Path("assets/sfx")
        self._create_directories()
        
        # 统计
        self.downloaded_count = 0
        self.results = {}
    
    def _create_directories(self):
        """创建音效目录"""
        print("\n📁 创建目录结构...")
        for category in self.categories.keys():
            cat_path = self.sfx_dir / category
            cat_path.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ {category}/")
        
        # 创建BGM目录
        bgm_dir = Path("assets/bgm")
        bgm_dir.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ bgm/")
    
    def search_sounds(self, query: str, max_duration: float = 5.0, max_results: int = 5) -> List[Dict]:
        """
        搜索音效
        
        Args:
            query: 搜索关键词
            max_duration: 最大时长（秒）
            max_results: 最大返回结果数
        """
        params = {
            "query": query,
            "filter": f"duration:[0 TO {max_duration}]",
            "page_size": max_results,
            "fields": "id,name,duration,previews,license"
        }
        
        try:
            response = self.session.get(
                f"{self.base_url}/search/text/",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
        except Exception as e:
            print(f"    搜索失败 '{query}': {e}")
            return []
    
    def download_sound(self, sound_id: int, sound_name: str, category: str, index: int) -> Optional[Path]:
        """
        下载音效文件
        
        Args:
            sound_id: 音效ID
            sound_name: 音效名称
            category: 分类
            index: 序号
        """
        try:
            # 获取音效详情
            detail_url = f"{self.base_url}/sounds/{sound_id}/"
            detail_response = self.session.get(detail_url, timeout=10)
            detail_response.raise_for_status()
            sound_detail = detail_response.json()
            
            # 获取预览URL
            preview_url = sound_detail.get("previews", {}).get("preview-lq-mp3")
            if not preview_url:
                return None
            
            # 下载文件
            response = self.session.get(preview_url, timeout=30)
            response.raise_for_status()
            
            # 生成安全的文件名
            safe_name = "".join(c for c in sound_name if c.isalnum() or c in "._- ").strip()
            if not safe_name:
                safe_name = f"sound_{sound_id}"
            
            filename = f"{category}_{index:02d}_{safe_name[:30]}.mp3"
            filepath = self.sfx_dir / category / filename
            
            # 保存文件
            with open(filepath, "wb") as f:
                f.write(response.content)
            
            print(f"    ✅ 已下载: {filename}")
            return filepath
            
        except Exception as e:
            print(f"    ❌ 下载失败: {e}")
            return None
    
    def download_category(self, category: str, info: dict, max_retries: int = 3):
        """
        下载单个分类的音效
        
        Args:
            category: 分类名
            info: 分类信息
            max_retries: 最大重试次数
        """
        print(f"\n📂 分类: {category} - {info['description']}")
        print(f"   目标: {info['target']} 个音效")
        
        downloaded = 0
        attempted_keywords = set()
        
        # 如果已经达到目标，直接返回
        if downloaded >= info['target']:
            return downloaded
        
        # 遍历所有关键词
        for keyword in info['keywords']:
            if downloaded >= info['target']:
                break
            
            # 避免重复搜索相同的关键词
            if keyword in attempted_keywords:
                continue
            attempted_keywords.add(keyword)
            
            print(f"  🔍 搜索: '{keyword}'")
            
            # 搜索音效
            sounds = self.search_sounds(keyword, max_duration=5.0, max_results=5)
            
            if not sounds:
                print(f"    没有找到音效，尝试下一个关键词")
                continue
            
            # 下载找到的音效
            for idx, sound in enumerate(sounds):
                if downloaded >= info['target']:
                    break
                
                sound_id = sound["id"]
                sound_name = sound.get("name", f"sound_{sound_id}")
                duration = sound.get("duration", "?")
                
                print(f"    🎵 找到: {sound_name[:40]}... ({duration:.1f}秒)")
                
                # 尝试下载，最多重试3次
                for retry in range(max_retries):
                    filepath = self.download_sound(
                        sound_id=sound_id,
                        sound_name=sound_name,
                        category=category,
                        index=downloaded + 1
                    )
                    
                    if filepath:
                        downloaded += 1
                        self.downloaded_count += 1
                        self.results[f"{category}_{downloaded}"] = {
                            "id": sound_id,
                            "name": sound_name,
                            "file": str(filepath),
                            "category": category,
                            "duration": duration
                        }
                        break
                    else:
                        if retry < max_retries - 1:
                            print(f"    重试 {retry + 1}/{max_retries}...")
                            time.sleep(2)
                
                # 避免请求过快
                time.sleep(1)
        
        print(f"  ✅ 分类完成: 下载 {downloaded}/{info['target']} 个")
        return downloaded
    
    def download_all(self, total_sounds: int = 10):
        """
        下载所有音效，确保达到总数量
        
        Args:
            total_sounds: 总共要下载的音效数量
        """
        print("\n" + "="*60)
        print("🎧 自动恐怖音效下载器")
        print("="*60)
        print(f"目标下载数量: {total_sounds} 个音效")
        print("="*60)
        
        # 先按分类目标下载
        for category, info in self.categories.items():
            if self.downloaded_count >= total_sounds:
                break
            self.download_category(category, info)
        
        # 如果还不够，继续从所有分类补足
        if self.downloaded_count < total_sounds:
            print(f"\n🔄 还需要 {total_sounds - self.downloaded_count} 个音效，继续搜索...")
            
            all_keywords = []
            for info in self.categories.values():
                all_keywords.extend(info['keywords'])
            
            # 随机打乱关键词顺序
            import random
            random.shuffle(all_keywords)
            
            for keyword in all_keywords:
                if self.downloaded_count >= total_sounds:
                    break
                
                print(f"\n🔍 补充分类搜索: '{keyword}'")
                sounds = self.search_sounds(keyword, max_duration=5.0, max_results=3)
                
                for sound in sounds:
                    if self.downloaded_count >= total_sounds:
                        break
                    
                    # 随机选一个分类存放
                    category = random.choice(list(self.categories.keys()))
                    
                    sound_id = sound["id"]
                    sound_name = sound.get("name", f"sound_{sound_id}")
                    duration = sound.get("duration", "?")
                    
                    print(f"    🎵 找到: {sound_name[:40]}... ({duration:.1f}秒)")
                    
                    filepath = self.download_sound(
                        sound_id=sound_id,
                        sound_name=sound_name,
                        category=category,
                        index=len([f for f in self.results.keys() if f.startswith(category)]) + 1
                    )
                    
                    if filepath:
                        self.downloaded_count += 1
                        self.results[f"{category}_{self.downloaded_count}"] = {
                            "id": sound_id,
                            "name": sound_name,
                            "file": str(filepath),
                            "category": category,
                            "duration": duration
                        }
                    
                    time.sleep(1)
        
        # 生成报告
        self._generate_report()
        return self.results
    
    def _generate_report(self):
        """生成下载报告"""
        report_path = self.sfx_dir / "download_report.json"
        
        # 按分类统计
        category_stats = {}
        for category in self.categories.keys():
            cat_files = list(self.sfx_dir.glob(f"{category}/*.mp3"))
            category_stats[category] = len(cat_files)
        
        report = {
            "download_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_downloaded": self.downloaded_count,
            "category_stats": category_stats,
            "files": self.results
        }
        
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print("\n" + "="*60)
        print(f"✅ 下载完成！共 {self.downloaded_count} 个音效")
        print(f"📄 报告已保存: {report_path}")
        print("\n📊 分类统计:")
        
        for category, count in category_stats.items():
            if count > 0:
                print(f"  {category}/: {count} 个文件")
    
    def generate_audio_plan(self):
        """生成音频计划模板"""
        # 检查实际下载的文件
        available_sfx = {}
        for category in self.categories.keys():
            files = list(self.sfx_dir.glob(f"{category}/*.mp3"))
            if files:
                available_sfx[category] = files[0].name  # 用第一个文件
        
        template = []
        
        # 按恐怖故事节奏生成模板
        if "ambient" in available_sfx:
            template.append({"type": "sfx", "file": f"assets/sfx/ambient/{available_sfx['ambient']}"})
        
        template.append({"type": "dialogue", "duration": 5000})
        
        if "heartbeat" in available_sfx:
            template.append({"type": "sfx", "file": f"assets/sfx/heartbeat/{available_sfx['heartbeat']}"})
        
        template.append({"type": "dialogue", "duration": 4000})
        
        if "door" in available_sfx:
            template.append({"type": "sfx", "file": f"assets/sfx/door/{available_sfx['door']}"})
        
        template.append({"type": "dialogue", "duration": 3000})
        
        if "footstep" in available_sfx:
            template.append({"type": "sfx", "file": f"assets/sfx/footstep/{available_sfx['footstep']}"})
        
        template.append({"type": "dialogue", "duration": 3000})
        
        if "jump" in available_sfx:
            template.append({"type": "sfx", "file": f"assets/sfx/jump/{available_sfx['jump']}"})
        
        template_path = Path("config") / "audio_plan_template.json"
        template_path.parent.mkdir(exist_ok=True)
        
        with open(template_path, "w", encoding="utf-8") as f:
            json.dump(template, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 音频计划模板已生成: {template_path}")
        return template_path


def quick_demo():
    """快速演示：下载10个音效"""
    print("🚀 快速下载模式：下载10个恐怖音效")
    
    # 使用您提供的API密钥
    downloader = AutoSFXDownloader(api_key="hHMqbjrS5LpwHe7npYjRaP61bamSX2nzph6pRVVp")
    
    # 下载音效
    results = downloader.download_all(total_sounds=10)
    
    # 生成模板
    downloader.generate_audio_plan()
    
    print("\n💡 使用提示:")
    print("1. 查看 assets/sfx/ 目录下的音效文件")
    print("2. 运行 ls -la assets/sfx/*/ 查看所有下载的文件")
    print("3. 在 audio_plan.json 中引用这些音效")
    
    return results


if __name__ == "__main__":
    quick_demo()