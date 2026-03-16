# rename_folders.py
import os
from pathlib import Path

# 当前目录下的 pics 文件夹
base_dir = Path("/Users/shuaiqu/Desktop/pics")  # 如果脚本不在 pics 旁边，可改成绝对路径

# 中文 → 英文 映射（可自行修改）
rename_map = {
    "剧场":     "theater",
    "房子":     "house",
    "楼房":     "building",
    "病房":     "hospital_room",
    "图书馆":   "library",
    "墓地":     "cemetery",
    "操场":     "playground",
    "楼梯":     "staircase",
    "镜子":     "mirror",
    "午夜电梯": "midnight_elevator",
}

def rename_folders():
    renamed_count = 0
    skipped_count = 0

    for item in base_dir.iterdir():
        if not item.is_dir():
            continue

        old_name = item.name
        new_name = rename_map.get(old_name)

        if new_name:
            new_path = item.parent / new_name

            # 防止目标已存在（加后缀避免覆盖）
            if new_path.exists():
                counter = 1
                while (item.parent / f"{new_name}_{counter}").exists():
                    counter += 1
                new_path = item.parent / f"{new_name}_{counter}"
                print(f"目标 {new_name} 已存在，重命名为 {new_path.name}")

            try:
                item.rename(new_path)
                print(f"重命名成功: {old_name} → {new_path.name}")
                renamed_count += 1
            except Exception as e:
                print(f"重命名失败: {old_name} → {new_name}   错误: {e}")
        else:
            print(f"跳过（无对应英文名）: {old_name}")
            skipped_count += 1

    print("\n完成！")
    print(f"成功重命名: {renamed_count} 个文件夹")
    print(f"跳过: {skipped_count} 个文件夹")

if __name__ == "__main__":
    print("即将重命名 pics 下的文件夹...")
    print("映射关系：")
    for cn, en in rename_map.items():
        print(f"  {cn:6} → {en}")
    print("\n按 Enter 确认执行（Ctrl+C 取消）...")
    input()  # 安全确认

    rename_folders()