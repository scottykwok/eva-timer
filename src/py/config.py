
from js import console
from js import URLSearchParams, window
import datetime

class Config:
    def __init__(self) -> None:
        params = URLSearchParams.new(window.location.search)
        self.config = {
            "mode": int(params.get("mode") or 0),
            "autoplay": bool(int(params.get("autoplay") or 0)),
            "tilted": bool(int(params.get("tilted") or 1)),
            "fullscreen": bool(int(params.get("fullscreen") or 0)),
            "theme": params.get("theme") or "default",
            "duration": int(params.get("duration") or 300),
            "emergency_duration": int(params.get("emergency_duration") or 60),
        }
