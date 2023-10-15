import asyncio
from enum import Enum


class Timer:
    STANDBY = "STANDBY"
    RACING = "RACING"
    EMERGENCY = "EMERGENCY"
    ENDED = "ENDED"
    SYSTEMTIME = "SYSTEMTIME"

    MODE_COUNT_DOWN = 0
    MODE_COUNT_UP = 1
    MODE_SYSTEM_TIME = 2

    SYSTEM_TIME_INTERVAL = 500./1000
    STOPWATCH_INTERVAL = 35./1000

    def __init__(
        self,
        interval,
        duration,
        emergency_duration,
        mode=0,
        status_callback=None,
        render_callback=None,
        config_callback=None,
    ):
        # Config variables
        self.STOPWATCH_INTERVAL = interval
        self.interval = self.STOPWATCH_INTERVAL
        self.duration = duration
        self.emergency_duration = min(emergency_duration, duration)
        self.mode = mode
        # Callbacks
        self.status_callback = status_callback
        self.render_callback = render_callback
        self.config_callback = config_callback
        # State variables
        self.remaining_time = duration
        self.running = False
        self.elapsed_time = 0
        self.previous_status = None
        self.previous_running = None

    async def update(self):
        if self.mode == self.MODE_SYSTEM_TIME:
            # For system time
            new_status = Timer.SYSTEMTIME
            self.render_callback(None)
        else:
            # For stop watch
            self.remaining_time = self.duration - self.elapsed_time
            match self.remaining_time:
                case r if r <= 0:
                    new_status = Timer.ENDED
                    self.remaining_time = 0
                    self.previous_running = self.running
                    self.running = False
                case r if 0 < r <= self.emergency_duration:
                    new_status = Timer.EMERGENCY
                case r if r == self.duration:
                    new_status = Timer.STANDBY
                case _:
                    new_status = Timer.RACING
            display_time = self.elapsed_time if self.mode == self.MODE_COUNT_UP else self.remaining_time
            self.render_callback(display_time)

        # For status change
        if self.previous_status != new_status or self.previous_running != self.running:
            self.status_callback(self.previous_status, new_status, self.previous_running, self.running)
        self.previous_status = new_status
        self.previous_running = self.running

    async def update_config(self):
        if self.config_callback:
            self.config_callback()

    async def loop(self):
        if self.running:
            return

        self.previous_running = self.running
        self.running = True
        last_update_time = asyncio.get_event_loop().time()
        while self.running:
            now = asyncio.get_event_loop().time()
            self.elapsed_time += now - last_update_time
            last_update_time = now
            await self.update()
            await asyncio.sleep(self.interval)

    def play(self):
        asyncio.ensure_future(self.loop())

    def pause(self):
        self.previous_running = self.running
        self.running = False
        asyncio.ensure_future(self.update())

    def time_is_up(self):
        return self.remaining_time <= 0

    def toggle_play_pause(self):
        if self.running:
            self.pause()
        else:
            self.play()

    def reset(self) -> bool:
        self.previous_running = self.running
        self.running = False
        nothing_to_reset = self.elapsed_time <= 0 or self.mode == self.MODE_SYSTEM_TIME
        self.elapsed_time = 0
        asyncio.ensure_future(self.update())
        # return False if nothing to reset
        return not nothing_to_reset

    def toggle_mode(self):
        self.set_mode(self.mode + 1)

    def toggle_mode_count_updown(self):
        if self.mode != self.MODE_COUNT_DOWN:
            self.set_mode(self.MODE_COUNT_DOWN)
        else:
            self.set_mode(self.MODE_COUNT_UP)

    def set_mode(self, mode):
        self.mode = mode % 3
        if self.mode == self.MODE_SYSTEM_TIME:
            self.interval = self.SYSTEM_TIME_INTERVAL
            self.play()
        else:
            self.interval = self.STOPWATCH_INTERVAL
            self.pause()
        asyncio.ensure_future(self.update())
        asyncio.ensure_future(self.update_config())

    def adjust_elapsed_time(self, seconds):
        self.elapsed_time += seconds
        asyncio.ensure_future(self.update())

    # -------- Formatting / Parsing the MM:SS
    def parse_duration(self, text):
        i = self.parse_mmss(text)
        if i is not None:
            self.duration = i
            asyncio.ensure_future(self.update())
            asyncio.ensure_future(self.update_config())

    def parse_emergency_duration(self, text):
        i = self.parse_mmss(text)
        if i is not None:
            self.emergency_duration = min(self.duration, i)
            asyncio.ensure_future(self.update())
            asyncio.ensure_future(self.update_config())

    def format_duration(self):
        return self.format_mmss(self.duration)

    def format_emergency_duration(self):
        return self.format_mmss(self.emergency_duration)

    @staticmethod
    def parse_mmss(text):
        try:
            minutes = max(0, min(59, int(text.split(":")[0])))
            seconds = max(0, min(59, int(text.split(":")[1])))
            return minutes * 60 + seconds
        except Exception:
            return None

    @staticmethod
    def format_mmss(seconds) -> str:
        ss = seconds % 60
        mm = int((seconds - ss) / 60)
        return f"{mm:02d}:{ss:02d}"
