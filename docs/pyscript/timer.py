import asyncio
from enum import Enum


class Status(Enum):
    STANDBY = "STANDBY"
    RACING = "RACING"
    EMERGENCY = "EMERGENCY"
    ENDED = "ENDED"

class Stopwatch:
    def __init__(self, duration, interval, emergency_duration, status_callback=None, render_callback=None):
        self.duration = duration
        self.interval = interval
        self.emergency_duration = emergency_duration
        self.status_callback = status_callback
        self.render_callback = render_callback
        self.count_up = False
        self.running = False
        self.elapsed_time = 0
        self.previous_status = Status.STANDBY

    async def update(self):
        remaining_time = self.duration - self.elapsed_time
        match remaining_time:
            case r if r <= 0:
                new_status = Status.ENDED
                remaining_time = 0
                self.running = False
            case r if 0 < r <= self.emergency_duration:
                new_status = Status.EMERGENCY
            case r if r == self.duration:
                new_status = Status.STANDBY
            case _:
                new_status = Status.RACING

        display_time = self.elapsed_time if self.count_up else remaining_time
        self.render_callback(display_time)

        if self.previous_status != new_status:
            self.status_callback(self.previous_status, new_status)

        self.previous_status = new_status

    async def loop(self):
        if self.running:
            return

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
        self.running = False

    def toggle_play_pause(self):
        if self.running:
            self.pause()
        else:
            self.play()

    def reset(self):
        self.running = False
        self.elapsed_time = 0
        asyncio.ensure_future(self.update())

    def toggle_counting_mode(self):
        self.count_up = not self.count_up
        asyncio.ensure_future(self.update())

    def adjust_elapsed_time(self, seconds):
        self.elapsed_time += seconds
        asyncio.ensure_future(self.update())
