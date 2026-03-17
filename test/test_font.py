cat > test_fonts.sh << 'EOF'
#!/bin/bash

echo "🔍 测试字体..."

# 测试你的 mk.ttf
echo "1. 测试 mk.ttf"
ffmpeg -y -f lavfi -i "color=c=black:s=1080x1920:d=5" \
    -vf "subtitles=test_font.srt:force_style='FontName=$(pwd)/assets/fonts/mk.ttf,FontSize=48'" \
    -frames:v 1 test_mk.jpg 2>/dev/null

# 测试系统字体
echo "2. 测试系统字体"
ffmpeg -y -f lavfi -i "color=c=black:s=1080x1920:d=5" \
    -vf "subtitles=test_font.srt:force_style='FontName=WenQuanYi Micro Hei,FontSize=48'" \
    -frames:v 1 test_wqy.jpg 2>/dev/null

# 显示结果
echo ""
echo "生成的文件:"
ls -la test_*.jpg
echo ""
echo "请打开查看:"
echo "  test_mk.jpg  - 你的 mk.ttf 字体"
echo "  test_wqy.jpg - 文泉驿系统字体"
EOF

chmod +x test_fonts.sh
./test_fonts.sh