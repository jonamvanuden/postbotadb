from new_utils import Locator
import time
import random

class ClickButtonCommand:
    def __init__(self, btn_type, username=None):
        self.username = username
        self.btn_type = btn_type
    
    def execute(self, ctx):
        ctx.snap()

        match self.btn_type:
            case "main_inbox": box = Locator.find_inbox_btn(ctx.screen)
            case "main_reel": box = Locator.find_reel_btn(ctx.screen)
            case "main_profile": box = Locator.find_profile_btn(ctx.screen, "thelifeofaime")
            case "main_home" : box = Locator.find_home_btn(ctx.screen)
            case _: raise ValueError(f"Unknown button: {self.btn_type}")           


        if box:
            ctx.human.tap_within_box(box)
            return True
        
        print("ClickInboxCommand failed")
        return False


import random
import time

class SnapToTopCommand:
    def __init__(self):
        self.header_anchor = Locator.get_btn_filename("btn-account-details.png", "home")

        self.blacklist = [
            Locator.get_btn_filename("suggested_persons.png", "exceptions"),
            Locator.get_btn_filename("suggested_reels.png", "exceptions")
        ]

    def execute(self, ctx):
        screen_h = ctx.screen.shape[0]
        screen_w = ctx.screen.shape[1]
        start_x = screen_w // 2

        # --- STEP 1: THE POWER SWIPE ---
        # "Make one big powerswipe"
        # We use a consistent 75% swipe.
        swipe_dist = int(screen_h * 0.75)
        
        ctx.human.swipe(start_x, int(screen_h * 0.85), start_x, int(screen_h * 0.85) - swipe_dist)
        # We wait 1.0s to ensure the scroll momentum is completely dead 
        # so our coordinate math is perfect.
        time.sleep(1.0)

        # --- STEP 2: FIND HIGHEST VISIBLE HEADER ---
        # "Find the highest account details"
        ctx.snap()
        headers = Locator.find_all_btns(self.header_anchor, ctx.screen, threshold=0.7)

        if not headers:
            # Emergency: If we landed on a long caption with no header, nudge up.
            print("🔎 No header. Searching...")
            ctx.human.swipe(start_x, screen_h // 2, start_x, int(screen_h * 0.35))
            time.sleep(1.0)
            return self.execute(ctx)

        # SELECTION LOGIC:
        # We want the highest header on the screen.
        # We do NOT filter out headers at the top edge anymore.
        # If the swipe landed it at Y=50, we want to grab that one and pull it DOWN to Y=240.
        headers.sort(key=lambda h: h[1])
        best_header = headers[0]

        # --- STEP 3: EXACT MATH SNAP (Top 10%) ---
        # "Swipe it to the top 10 procent"
        header_y = best_header[1]
        target_y = int(screen_h * 0.10) # Strictly 10%
        
        diff = target_y - header_y
        
        print(f"🎯 Header at {header_y}px. Target is {target_y}px.")
        print(f"⚖️ Correction: Moving {diff}px.")
        
        # EXECUTE THE MOVE
        # We don't care if it's huge (-1000) or positive (+100). We just do it.
        if abs(diff) > 15:
            ctx.human.swipe(start_x, screen_h // 2, start_x, (screen_h // 2) + diff)
            time.sleep(0.6) # Wait for snap to settle

# --- STEP 3: WATCH & (MAYBE) LIKE ---
        watch_time = random.uniform(2.0, 8.0)
        
        if random.random() < 0.50: 
            # --- NEW: THE BLACKLIST CHECK ---
            print("🧐 Thinking about liking... Checking forbidden patterns.")
            
            # Take a fresh picture to be sure
            ctx.snap()
            found_bad_pattern = False
            
            for bad_img in self.blacklist:
                # We check if the bad image exists anywhere on screen
                matches = Locator.find_all_btns(bad_img, ctx.screen, threshold=0.8)
                if matches:
                    print(f"🚫 Forbidden Pattern Found ({bad_img})! ABORTING LIKE.")
                    found_bad_pattern = True
                    break
            
            if not found_bad_pattern:
                print(f"❤️ Clean Post! Triggering Like. (Watching {watch_time:.1f}s)")
                time.sleep(random.uniform(1.0, 2.0))
                
                tap_x = (screen_w // 2) + random.randint(-20, 20)
                tap_y = (screen_h // 2) + random.randint(-20, 20)
                
                ctx.human.double_tap(tap_x, tap_y)
                time.sleep(max(0, watch_time - 2.0))
            else:
                # If we blocked the like, we just watch normally
                time.sleep(watch_time)

        else:
            print(f"✅ Watching for {watch_time:.1f}s...")
            time.sleep(watch_time)
        
        return True