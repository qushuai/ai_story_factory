#!/bin/bash

echo "🔍 测试字体..."

# 先创建一个测试字幕文件
cat > test_font.srt << 'INNER'
1
00:00:01,000 --> 00:00:05,000
中文测试：半夜洗车房，鬼影浮现
INNER

# 测试你的 mk.ttf
echo "1. 测试 mk.ttf"
ffmpeg -y -f lavfi -i "color=c=black:s=1080x1920:d=5" \
    -vf "subtitles=test_font.srt:force_style='FontName=$(pwd)/assets/fonts/lfeng.ttf,FontSize=48'" \
    -frames:v 1 test_mk.jpg

if [ -f test_mk.jpg ]; then
    echo "✅ test_mk.jpg 生成成功"
else
    echo "❌ test_mk.jpg 生成失败"
fi

# 测试系统字体
echo "2. 测试系统字体 WenQuanYi Micro Hei"
ffmpeg -y -f lavfi -i "color=c=black:s=1080x1920:d=5" \
    -vf "subtitles=test_font.srt:force_style='FontName=WenQuanYi Micro Hei,FontSize=48'" \
    -frames:v 1 test_wqy.jpg

if [ -f test_wqy.jpg ]; then
    echo "✅ test_wqy.jpg 生成成功"
else
    echo "❌ test_wqy.jpg 生成失败"
fi

# 测试系统字体 Noto Sans
echo "3. 测试系统字体 Noto Sans CJK SC"
ffmpeg -y -f lavfi -i "color=c=black:s=1080x1920:d=5" \
    -vf "subtitles=test_font.srt:force_style='FontName=Noto Sans CJK SC,FontSize=48'" \
    -frames:v 1 test_noto.jpg

if [ -f test_noto.jpg ]; then
    echo "✅ test_noto.jpg 生成成功"
else
    echo "❌ test_noto.jpg 生成失败"
fi

# 显示结果
echo ""
echo "生成的文件:"
ls -la test_*.jpg 2>/dev/null || echo "没有生成任何测试图片"

echo ""
echo "请打开查看（用图片查看器）："
echo "  test_mk.jpg  - 你的 mk.ttf 字体"
echo "  test_wqy.jpg - 文泉驿系统字体"
echo "  test_noto.jpg - Noto Sans 字体"
