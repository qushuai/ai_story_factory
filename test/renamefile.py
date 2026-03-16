# rename_images_sequential.py
import os
from pathlib import Path
import sys

# 修改这里为你的 pics 路径（相对或绝对路径）
BASE_DIR = Path("/Users/shuaiqu/Desktop/pics")  # 如果脚本和 pics 同级，就这样写

def scan_and_rename(dry_run=True):
    total_renamed = 0
    total_skipped = 0
    total_folders = 0

    print("=== 扫描开始 ===")
    print(f"目标目录: {BASE_DIR.resolve()}\n")

    for folder in sorted(BASE_DIR.iterdir()):
        if not folder.is_dir():
            continue

        total_folders += 1
        print(f"\n处理文件夹: {folder.name}")

        # 收集所有 .jpg / .jpeg 文件，按名称排序（保持原有顺序）
        image_files = sorted(
            [f for f in folder.iterdir() if f.is_file() and f.suffix.lower() in ('.jpg', '.jpeg')],
            key=lambda x: x.name.lower()  # 按文件名排序，忽略大小写
        )

        if not image_files:
            print("  → 该文件夹没有 .jpg/.jpeg 文件，跳过")
            continue

        print(f"  找到 {len(image_files)} 张图片")

        if dry_run:
            print("  预览（不会实际改名）：")
        else:
            print("  执行重命名：")

        counter = 1
        for old_file in image_files:
            new_name = f"{counter}.jpg"
            new_path = folder / new_name

            if new_path.exists():
                print(f"  警告：{new_name} 已存在，跳过 {old_file.name}")
                total_skipped += 1
                continue

            if dry_run:
                print(f"    {old_file.name}  →  {new_name}")
            else:
                try:
                    old_file.rename(new_path)
                    print(f"    {old_file.name}  →  {new_name}")
                    total_renamed += 1
                except Exception as e:
                    print(f"    失败: {old_file.name} → {new_name}   错误: {e}")
                    total_skipped += 1

            counter += 1

    print("\n=== 操作完成 ===")
    print(f"处理的文件夹数: {total_folders}")
    print(f"成功重命名图片: {total_renamed}")
    print(f"跳过/失败图片: {total_skipped}")


if __name__ == "__main__":
    print("脚本将扫描 pics 下所有子文件夹内的 .jpg / .jpeg 文件")
    print("每个子文件夹内部从 1.jpg 开始重新编号")
    print("注意：只影响 .jpg/.jpeg 文件，其他文件不动\n")

    # 先预览（dry_run=True）
    print("第一步：预览将要进行的改名操作（不会实际修改）")
    scan_and_rename(dry_run=True)

    print("\n如果预览正确，请输入 y 并回车来执行真实重命名（不可逆！）")
    print("输入其他任意内容或直接回车则取消：")
    confirm = input("> ").strip().lower()

    if confirm == 'y':
        print("\n开始真实重命名...")
        scan_and_rename(dry_run=False)
    else:
        print("已取消操作。")