import time
import random
from new_utils import Locator

class LikeWithDoubleTapCommand:
    def __init__(self):
        self.blacklist = [
            Locator.get_btn_filename("suggested_persons.png", "exceptions"),
            Locator.get_btn_filename("suggested_reels.png", "exceptions")
        ]
        self.like_probability = 0.50

    def execute(self, ctx):
        # 1. Dice Roll
        if random.random() > self.like_probability:
            print("🎲 Skipping like (Random).")
            return True

        # 2. Blacklist Check
        print("🧐 Checking for ads/blacklist...")
        ctx.snap() # Fresh screenshot required
        
        for bad_img in self.blacklist:
            if Locator.find_all_btns(bad_img, ctx.screen, threshold=0.8):
                print(f"🚫 Forbidden ({bad_img})! Like Aborted.")
                return False

        # 3. Double Tap
        print("❤️ Double Tapping!")
        h, w = ctx.screen.shape[:2]
        tap_x = (w // 2) + random.randint(-20, 20)
        tap_y = (h // 2) + random.randint(-20, 20)
        
        ctx.human.double_tap(tap_x, tap_y)
        time.sleep(1.5) # Natural pause after liking
        return True