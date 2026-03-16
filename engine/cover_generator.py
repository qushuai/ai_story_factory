"""
封面生成器 - 根据故事标题生成封面图
支持标签解析、随机选图、文字叠加、暗红滤镜
"""

import random
import datetime
from pathlib import Path
from typing import Tuple, Optional, List, Union
from PIL import Image, ImageDraw, ImageFont
import re


class CoverGenerator:
    """封面图生成器"""
    
    def __init__(self, assets_dir: Union[str, Path] = "assets"):
        """
        初始化封面生成器
        
        Args:
            assets_dir: 资源根目录（包含fonts/和images/）
        """
        self.assets_dir = Path(assets_dir)
        self.font_path = self.assets_dir / "fonts" / "lfeng.ttf"
        
        # 检查字体是否存在
        if not self.font_path.exists():
            print(f"⚠️ 警告: 字体文件不存在: {self.font_path}")
        
    def generate(
        self,
        title: str,
        output_path: Union[str, Path],
        size: Tuple[int, int] = (1080, 1920),
        quality: int = 92
    ) -> Path:
        """
        根据故事标题生成封面图
        
        格式: "[theater] 舞台上的提线木偶 突然对我眨了眨眼"
        - 标签 [theater] 决定从 assets/images/theater/ 随机选图
        - 如果对应文件夹不存在，使用 fallback 文件夹
        
        Args:
            title: 故事标题（可能包含标签）
            output_path: 输出图片路径
            size: 图片尺寸 (宽, 高)
            quality: JPEG 压缩质量
        
        Returns:
            输出文件路径
        """
        # 解析标题标签
        pure_title, tag = self._parse_title_tag(title)
        if not pure_title:
            pure_title = title
        
        print(f"🖼️ 生成封面: {title}")
        print(f"  标签: {tag if tag else '无'}")
        print(f"  纯标题: {pure_title}")
        
        # 获取背景图片
        bg_img = self._get_background_image(tag, size)
        
        # 应用暗红滤镜
        bg_img = self._apply_dark_red_filter(bg_img)
        
        # 添加文字到图片
        bg_img = self._add_text_to_image(bg_img, pure_title)
        
        # 保存图片
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        bg_img.save(output_path, "JPEG", quality=quality)
        print(f"✅ 封面已生成: {output_path}")
        
        return output_path
    
    def _parse_title_tag(self, title: str) -> Tuple[str, Optional[str]]:
        """
        从标题解析标签，用于封面图选择
        
        格式: "[theater] 舞台上的提线木偶 突然对我眨了眨眼"
        
        Returns:
            (纯标题, 标签或None)
        """
        if not title:
            return title, None
        
        # 匹配方括号标签 [xxx]
        match = re.match(r'^\[([^\]]+)\]\s*(.*)', title.strip())
        if match:
            tag = match.group(1).strip()
            pure_title = match.group(2).strip()
            return pure_title, tag
        
        return title, None
    
    def _get_background_image(self, tag: Optional[str], size: Tuple[int, int]) -> Image.Image:
        """获取背景图片"""
        # 确定图片文件夹
        if tag:
            image_dir = self.assets_dir / "images" / tag
        else:
            image_dir = self.assets_dir / "images" / "fallback"
        
        # 如果标签文件夹不存在或没有图片，使用 fallback
        if not image_dir.exists() or not self._has_images(image_dir):
            print(f"⚠️ 文件夹不存在或无图片: {image_dir}，使用 fallback")
            image_dir = self.assets_dir / "images" / "fallback"
        
        # 确保 fallback 存在
        if not image_dir.exists():
            image_dir.mkdir(parents=True, exist_ok=True)
            print(f"📁 创建 fallback 目录: {image_dir}")
            # 创建一个纯色背景作为 fallback
            fallback_img_path = image_dir / "default.jpg"
            if not fallback_img_path.exists():
                img = Image.new('RGB', size, color=(40, 20, 30))
                img.save(fallback_img_path, "JPEG", quality=92)
        
        # 随机选择一张图片
        image_files = self._get_image_files(image_dir)
        
        if not image_files:
            print(f"⚠️ 未找到图片，使用纯色背景")
            return Image.new('RGB', size, color=(40, 20, 30))
        
        bg_path = random.choice(image_files)
        print(f"📷 选择背景: {bg_path.name}")
        bg_img = Image.open(bg_path).convert('RGB')
        
        # 调整图片尺寸以适应封面大小
        return self._resize_and_crop(bg_img, size)
    
    def _has_images(self, directory: Path) -> bool:
        """检查目录是否包含图片"""
        for ext in ['*.jpg', '*.jpeg', '*.JPG', '*.JPEG', '*.png', '*.PNG']:
            if any(directory.glob(ext)):
                return True
        return False
    
    def _get_image_files(self, directory: Path) -> List[Path]:
        """获取目录中的所有图片文件"""
        image_files = []
        for ext in ['*.jpg', '*.jpeg', '*.JPG', '*.JPEG', '*.png', '*.PNG']:
            image_files.extend(list(directory.glob(ext)))
        return image_files
    
    def _resize_and_crop(self, img: Image.Image, target_size: Tuple[int, int]) -> Image.Image:
        """调整图片尺寸并裁剪以适应目标尺寸"""
        target_width, target_height = target_size
        img_width, img_height = img.size
        
        # 计算缩放比例
        width_ratio = target_width / img_width
        height_ratio = target_height / img_height
        scale = max(width_ratio, height_ratio)
        
        # 缩放图片
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # 裁剪中间部分
        left = (new_width - target_width) // 2
        top = (new_height - target_height) // 2
        right = left + target_width
        bottom = top + target_height
        
        return img.crop((left, top, right, bottom))
    
    def _apply_dark_red_filter(self, img: Image.Image) -> Image.Image:
        """应用暗红滤镜"""
        # 转换为RGBA以进行颜色叠加
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # 创建暗红色层 (R=60, G=20, B=30, 半透明)
        red_overlay = Image.new('RGBA', img.size, (60, 20, 30, 100))
        
        # 混合图像
        img = Image.alpha_composite(img, red_overlay)
        
        # 转换回RGB
        return img.convert('RGB')
    
    def _add_text_to_image(self, img: Image.Image, title: str) -> Image.Image:
        """向图片添加文字（不显示标签和日期）"""
        draw = ImageDraw.Draw(img)
        size = img.size
        
        # 加载字体
        try:
            # 根据标题长度动态调整字体大小（整体加大两号）
            title_length = len(title)
            if title_length <= 10:
                main_font_size = 100  # 原来80，加大到100
            elif title_length <= 20:
                main_font_size = 90   # 原来70，加大到90
            else:
                main_font_size = 80   # 原来60，加大到80
            
            # 主标题字体（白色）
            main_font = ImageFont.truetype(str(self.font_path), main_font_size)
        except Exception as e:
            print(f"⚠️ 字体加载失败: {e}，使用默认字体")
            main_font = ImageFont.load_default()
        
        # 计算文字位置（居中）
        center_x = size[0] // 2
        center_y = size[1] // 2  # 垂直居中
        
        # 处理标题换行 - 修复换行逻辑
        max_width = size[0] - 200  # 左右留100像素边距
        title_lines = self._wrap_text_fixed(title, main_font, max_width)
        
        # 如果没有成功换行，强制按字符数换行
        if len(title_lines) == 1 and len(title) > 15:
            # 强制按每行12个字符换行
            title_lines = []
            for i in range(0, len(title), 12):
                title_lines.append(title[i:i+12])
        
        print(f"📝 标题分 {len(title_lines)} 行显示")
        
        # 计算总高度以便垂直居中
        total_height = 0
        line_heights = []
        for line in title_lines:
            try:
                bbox = draw.textbbox((0, 0), line, font=main_font)
                line_height = bbox[3] - bbox[1]
            except:
                line_height = main_font_size + 10
            line_heights.append(line_height)
            total_height += line_height + 15
        total_height -= 15  # 减去最后一个的间距
        
        # 计算起始Y坐标（垂直居中）
        start_y = center_y - total_height // 2
        
        # 绘制主标题（白色）
        current_y = start_y
        for i, line in enumerate(title_lines):
            try:
                bbox = draw.textbbox((0, 0), line, font=main_font)
                line_width = bbox[2] - bbox[0]
                line_height = line_heights[i]
            except:
                line_width = main_font_size * len(line)
                line_height = main_font_size + 10
            
            line_x = center_x - line_width // 2
            
            # 绘制描边
            for offset_x, offset_y in [(-3,-3), (-3,3), (3,-3), (3,3), (0,-3), (0,3), (-3,0), (3,0)]:
                draw.text((line_x + offset_x, current_y + offset_y), line, font=main_font, fill="black")
            
            # 绘制主文字（白色）
            draw.text((line_x, current_y), line, font=main_font, fill="white")
            
            current_y += line_height + 15
        
        return img
    
    def _wrap_text_fixed(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
        """修复版的文本换行函数"""
        lines = []
        
        # 如果没有空格，按字符数换行
        if ' ' not in text:
            current_line = ""
            for char in text:
                test_line = current_line + char
                try:
                    bbox = font.getbbox(test_line)
                    line_width = bbox[2] - bbox[0]
                except:
                    line_width = len(test_line) * 30
                
                if line_width <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = char
            if current_line:
                lines.append(current_line)
            return lines
        
        # 有空格的情况，按单词换行
        words = text.split()
        if not words:
            return [text]
        
        current_line = words[0]
        for word in words[1:]:
            # 测试加入这个词后的宽度
            test_line = current_line + " " + word
            try:
                bbox = font.getbbox(test_line)
                line_width = bbox[2] - bbox[0]
            except:
                line_width = len(test_line) * 30
            
            if line_width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        
        lines.append(current_line)
        return lines
    
    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
        """将文本按最大宽度换行（保留原函数名以保持兼容）"""
        return self._wrap_text_fixed(text, font, max_width)


# 单独使用示例
if __name__ == "__main__":
    # 创建封面生成器
    generator = CoverGenerator(assets_dir="assets")
    
    # 测试短标题
    generator.generate(
        title="短标题示例",
        output_path="output/short_title.jpg"
    )
    
    # 测试长标题（应该换行）
    generator.generate(
        title="这是一个非常非常非常非常非常非常非常非常非常非常非常长的标题用来测试换行功能",
        output_path="output/long_title.jpg"
    )