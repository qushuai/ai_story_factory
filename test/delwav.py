#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import argparse

def remove_pinyin(text_with_pinyin):
    """
    去掉拼音注音，只保留汉字和标点
    """
    # 匹配模式：汉字+空格+拼音+空格
    # 例如："北 bei3 京 jin1"
    pattern = r'([\u4e00-\u9fff]+)\s+[a-z]+\d*\s*'
    
    # 替换为只保留汉字
    pure_text = re.sub(pattern, r'\1', text_with_pinyin)
    
    # 处理行尾可能残留的拼音
    pure_text = re.sub(r'\s+[a-z]+\d*$', '', pure_text)
    
    # 清理多余空格
    pure_text = ' '.join(pure_text.split())
    
    return pure_text

def parse_line(line):
    """
    解析一行数据，返回文件名和带拼音的文本
    格式：文件名\t带拼音的文本
    """
    parts = line.strip().split('\t')
    if len(parts) >= 2:
        filename = parts[0]
        pinyin_text = parts[1]
        return filename, pinyin_text
    return None, None

def extract_lines_to_files(input_file, keywords, output_dir=None, case_sensitive=False):
    """
    从输入文件中提取包含指定关键词的行，每行生成一个独立的txt文件
    
    Args:
        input_file: 输入文件路径
        keywords: 关键词列表或单个关键词字符串
        output_dir: 输出目录（可选，默认在当前目录创建以输入文件名命名的文件夹）
        case_sensitive: 是否区分大小写
    """
    # 处理关键词
    if isinstance(keywords, str):
        keywords = [keywords]
    
    # 如果不区分大小写，将所有关键词转为小写用于比较
    if not case_sensitive:
        keywords = [k.lower() for k in keywords]
    
    # 创建输出目录
    if output_dir is None:
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_dir = f"{base_name}_extracted"
    
    # 如果目录不存在，创建它
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📁 创建输出目录: {output_dir}")
    
    extracted_count = 0
    line_count = 0
    match_count = 0
    generated_files = []
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                line_count += 1
                line = line.strip()
                if not line:
                    continue
                
                filename, pinyin_text = parse_line(line)
                if filename is None or pinyin_text is None:
                    print(f"⚠️ 第{line_count}行格式错误，跳过: {line[:50]}...")
                    continue
                
                # 检查是否包含关键词
                text_to_check = pinyin_text.lower() if not case_sensitive else pinyin_text
                match = False
                
                for keyword in keywords:
                    if keyword in text_to_check:
                        match = True
                        break
                
                if match:
                    match_count += 1
                    # 去掉拼音
                    pure_text = remove_pinyin(pinyin_text)
                    
                    # 生成文件名：原WAV文件名（去掉扩展名）+ .txt
                    base_filename = os.path.splitext(filename)[0]  # 去掉.wav后缀
                    output_file = os.path.join(output_dir, f"{base_filename}.txt")
                    
                    # 写入文件
                    with open(output_file, 'w', encoding='utf-8') as out_f:
                        out_f.write(pure_text)
                    
                    generated_files.append(output_file)
                    extracted_count += 1
                    print(f"  ✓ 生成: {os.path.basename(output_file)} -> {pure_text}")
        
        print(f"\n✅ 处理完成！")
        print(f"   输入文件: {input_file}")
        print(f"   输出目录: {output_dir}")
        print(f"   总行数: {line_count}")
        print(f"   匹配行数: {match_count}")
        print(f"   生成文件数: {extracted_count}")
        
        if generated_files:
            print(f"\n📄 生成的文件列表:")
            for i, file_path in enumerate(generated_files, 1):
                print(f"   {i}. {os.path.basename(file_path)}")
        
        return generated_files
        
    except FileNotFoundError:
        print(f"❌ 错误：找不到文件 {input_file}")
        return []
    except Exception as e:
        print(f"❌ 错误：{str(e)}")
        return []

def main():
    parser = argparse.ArgumentParser(description='从拼音标注的文本中提取指定内容，每行生成一个独立的txt文件')
    parser.add_argument('input_file', help='输入文件路径')
    parser.add_argument('keywords', nargs='+', help='要提取的关键词（可以多个）')
    parser.add_argument('-o', '--output-dir', help='输出目录（可选，默认自动创建）')
    parser.add_argument('-c', '--case-sensitive', action='store_true', help='区分大小写（默认不区分）')
    
    args = parser.parse_args()
    
    extract_lines_to_files(args.input_file, args.keywords, args.output_dir, args.case_sensitive)

def quick_extract():
    """
    快速提取函数，可以直接调用
    """
    print("=" * 60)
    print("拼音文本提取工具 - 每行生成独立文件")
    print("=" * 60)
    
    input_file = input("请输入输入文件路径: ").strip()
    if not input_file:
        print("❌ 文件路径不能为空")
        return
    
    keywords_input = input("请输入要提取的关键词（多个关键词用逗号分隔）: ").strip()
    keywords = [k.strip() for k in keywords_input.split(',') if k.strip()]
    
    if not keywords:
        print("❌ 关键词不能为空")
        return
    
    case_input = input("是否区分大小写？(y/N): ").strip().lower()
    case_sensitive = case_input == 'y'
    
    output_dir = input("输出目录（直接回车自动创建）: ").strip() or None
    
    extract_lines_to_files(input_file, keywords, output_dir, case_sensitive)

if __name__ == "__main__":
    import sys
    
    # 如果有命令行参数，使用命令行模式
    if len(sys.argv) > 1:
        main()
    else:
        # 否则使用交互模式
        quick_extract()