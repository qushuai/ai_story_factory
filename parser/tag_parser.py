import re
from core.models import Segment


class TagParser:

    def parse(self, text):

        lines = text.splitlines()

        segments = []

        current_speaker = None

        for line in lines:

            line = line.strip()

            if not line:
                continue

            speaker_match = re.match(r"\[SPEAKER:(.*?)\]", line)

            if speaker_match:
                current_speaker = speaker_match.group(1)
                continue

            sfx_match = re.match(r"\[SFX:(.*?)\]", line)

            if sfx_match:
                segments.append(
                    Segment(
                        type="sfx",
                        name=sfx_match.group(1)
                    )
                )
                continue

            pause_match = re.match(r"\[PAUSE:(\d+)\]", line)

            if pause_match:
                segments.append(
                    Segment(
                        type="pause",
                        duration=int(pause_match.group(1))
                    )
                )
                continue

            segments.append(
                Segment(
                    type="dialogue",
                    speaker=current_speaker,
                    text=line
                )
            )
        
        return segments