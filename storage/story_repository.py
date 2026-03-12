import json
import uuid
from pathlib import Path


class StoryRepository:

    def __init__(self, output_dir="output/stories"):

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save(self, segments):

        story_id = str(uuid.uuid4())

        data = {
            "story_id": story_id,
            "segments": [seg.__dict__ for seg in segments]
        }

        file_path = self.output_dir / f"{story_id}.json"

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return file_path