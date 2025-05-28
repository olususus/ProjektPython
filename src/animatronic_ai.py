import threading
import random

class AnimatronicAI:
    def __init__(self, name, ai_level, move_interval, move_range, camera_path):
        self.name = name
        self.ai_level = ai_level
        self.move_interval = move_interval
        self.move_range = move_range
        self.camera_path = camera_path  # [5,4,3,2,1,'door']
        self.position = -1  # -1 = poza kamerami, 0 = kamera 5, ... 4 = kamera 1, 5 = drzwi
        self.timer = None
        self.active = True

    def try_move(self):
        if not self.active:
            return
        roll = random.randint(0, self.move_range)
        if roll <= self.ai_level:
            self.position += 1
            if self.position > len(self.camera_path) - 1:
                self.position = len(self.camera_path) - 1
        self.start_timer()

    def start_timer(self):
        if not self.active:
            return
        self.timer = threading.Timer(self.move_interval, self.try_move)
        self.timer.daemon = True
        self.timer.start()

    def stop(self):
        self.active = False
        if self.timer:
            self.timer.cancel()

    def reset(self):
        self.position = -1
