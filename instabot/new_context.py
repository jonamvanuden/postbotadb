from new_humanizer import *
import subprocess
import cv2
import numpy as np

class Context:
    def __init__(self):
        self.screen = None
        self.vars = {}  # Store found coordinates here
        self.human = Humanizer()

    def snap(self):
        """This is your get_live_screen function, moved here."""
        cmd = ["adb", "exec-out", "screencap", "-p"]
        try:
            raw_data = subprocess.check_output(cmd)
            # Update the 'eyes'
            self.screen = cv2.imdecode(np.frombuffer(raw_data, np.uint8), cv2.IMREAD_COLOR)
            return True
        except Exception as e:
            print(f"❌ ADB Capture Failed: {e}")
            return False