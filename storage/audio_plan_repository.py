import json
import os
import uuid


OUTPUT_DIR = "output/audio_plan"


def save_audio_plan(plan):

    """
    保存 audio_plan.json
    """

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    file_name = f"{uuid.uuid4()}.json"

    path = os.path.join(OUTPUT_DIR, file_name)

    with open(path, "w", encoding="utf-8") as f:

        json.dump(plan, f, indent=2, ensure_ascii=False)

    return path