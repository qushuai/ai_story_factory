from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Segment:
    type: str
    speaker: Optional[str] = None
    text: Optional[str] = None
    name: Optional[str] = None
    duration: Optional[int] = None


@dataclass
class Story:
    segments: List[Segment]