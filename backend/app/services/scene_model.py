from dataclasses import dataclass
from typing import Optional

@dataclass
class Scene:
    sketch_path: str          # local path to sketch image
    text: str                 # on-screen text
    duration: float           # seconds
    motion: str               # "zoom_in", "pan_left", etc.
    audio_path: Optional[str] = None
    narration: Optional[str] = None
