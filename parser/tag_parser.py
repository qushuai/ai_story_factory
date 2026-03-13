import re
from core.models import Segment


class TagParser:

    def parse(self, text):

        lines = text.splitlines()

        title = None
        segments = []

        current_speaker = None
        reading_title = False

        for line in lines:

            line = line.strip()

            if not line:
                continue

            # -------- TITLE --------
            if line == "[TITLE]":
                reading_title = True
                continue

            if reading_title:
                title = line
                reading_title = False
                continue

            # -------- STORY TAG (忽略) --------
            if line == "[STORY]":
                continue

            # -------- SPEAKER --------
            speaker_match = re.match(r"\[SPEAKER:(.*?)\]", line)

            if speaker_match:
                current_speaker = speaker_match.group(1)
                continue

            # -------- SFX --------
            sfx_match = re.match(r"\[SFX:(.*?)\]", line)

            if sfx_match:
                segments.append(
                    Segment(
                        type="sfx",
                        name=sfx_match.group(1)
                    )
                )
                continue

            # -------- PAUSE --------
            pause_match = re.match(r"\[PAUSE:(\d+)\]", line)

            if pause_match:
                segments.append(
                    Segment(
                        type="pause",
                        duration=int(pause_match.group(1))
                    )
                )
                continue

            # -------- DIALOGUE --------
            if current_speaker:  # 防止没有 speaker
                segments.append(
                    Segment(
                        type="dialogue",
                        speaker=current_speaker,
                        text=line
                    )
                )

        return title, segments