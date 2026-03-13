import json
import os
import uuid

OUTPUT_DIR = "output/audio_plan"


def save_audio_plan(plan, file_path=None):
    """
    保存 audio_plan.json

    支持两种模式：
    1 默认保存到 output/audio_plan/
    2 指定 file_path（任务系统使用）
    """

    # 如果指定路径
    if file_path:

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        path = file_path

    # 默认路径
    else:

        os.makedirs(OUTPUT_DIR, exist_ok=True)

        file_name = f"{uuid.uuid4()}.json"

        path = os.path.join(OUTPUT_DIR, file_name)

    with open(path, "w", encoding="utf-8") as f:

        json.dump(plan, f, indent=2, ensure_ascii=False)

    return path