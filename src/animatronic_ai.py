import threading
import random
import logging
import os
from datetime import datetime

# Ensure the logs directory exists
LOGS_DIR = os.path.join(os.path.dirname(__file__), '../logs')
os.makedirs(LOGS_DIR, exist_ok=True)

# Generate a unique log file name for each game session
log_filename = os.path.join(LOGS_DIR, f'animatronic_ai_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')

# Configure logging
logging.basicConfig(
    filename=log_filename,
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(message)s'
)

# Ensure the animatronic_ai logs directory exists
ANIMATRONIC_LOGS_DIR = os.path.join(os.path.dirname(__file__), '../logs/animatronic_ai')
os.makedirs(ANIMATRONIC_LOGS_DIR, exist_ok=True)

# Configure logging for animatronic AI
animatronic_log_filename = os.path.join(ANIMATRONIC_LOGS_DIR, f'animatronic_ai_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
logging.basicConfig(
    filename=animatronic_log_filename,
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

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
        logging.info(f"Initialized {self.name} AI with level {self.ai_level}, move interval {self.move_interval}, move range {self.move_range}.")

    def try_move(self):
        if not self.active:
            return
        roll = random.randint(0, self.move_range)
        if roll <= self.ai_level:
            self.position += 1
            logging.info(f"{self.name} rolled {roll} (<= {self.ai_level}) and moved to position {self.position}.")
            if self.position > len(self.camera_path) - 1:
                self.position = len(self.camera_path) - 1
                logging.info(f"{self.name} reached the final position: {self.position} ({self.camera_path[self.position]}).")
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
        logging.info(f"{self.name} reset to initial position.")
