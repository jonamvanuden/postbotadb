import os, cv2, re, random, time, subprocess, numpy as np

class Humanizer:
    def __init__(self, verbose=True):
        self.verbose = verbose
        self.device = None

        # ⌨️ QWERTY Keyboard Layout Map (for realistic typos)
        # We map each key to its immediate left/right neighbors
        self.key_neighbors = {
            'q': 'w', 'w': 'qe', 'e': 'wr', 'r': 'et', 't': 'ry', 'y': 'tu', 'u': 'yi', 'i': 'uo', 'o': 'ip', 'p': 'o',
            'a': 's', 's': 'ad', 'd': 'sf', 'f': 'dg', 'g': 'fh', 'h': 'gj', 'j': 'hk', 'k': 'jl', 'l': 'k',
            'z': 'x', 'x': 'zc', 'c': 'xv', 'v': 'cb', 'b': 'vn', 'n': 'bm', 'm': 'n'
        }

    
    
    def _adb_command(self, cmd, capture=False):
        """
        Run an adb command.
        - capture=False (default): silent, returns None (for actions like input swipe)
        - capture=True: returns stdout/stderr text (for queries like wm size)
        """
        if capture:
            result = subprocess.run(
                ["adb"] + cmd.split(),
                capture_output=True,
                text=True,
                shell=False
            )
            out = (result.stdout or "").strip()
            err = (result.stderr or "").strip()
            return out if out else err  # return something usable
        else:
            subprocess.run(f"adb {cmd} > nul 2>&1", shell=True)
            return None
    
    def wake_and_unlock_and_open_insta(self, pin):
        # 26 is the keycode for Power. This toggles the screen.
        self._adb_command("shell input keyevent 224")
        time.sleep(1)

        # Swipes from bottom-middle to top-middle
        self._adb_command("shell input swipe 500 1500 500 500 200")
        time.sleep(1)
        # Sends the text of your pin and presses Enter (keycode 66)
        self._adb_command(f"shell input text {pin}")
        self._adb_command("shell input keyevent 66")
        time.sleep(1)

        # This command searches for the launcher automatically
        self._adb_command("shell monkey -p com.instagram.android -c android.intent.category.LAUNCHER 1")
    
    def close_instagram_natural(self):
        """
        Executes the full 'Human Close' sequence:
        1. Open Recent Apps view.
        2. Wait for animation.
        3. Flick the app card upward with drift and momentum.
        4. Return to Home screen.
        """
        print("   [Action] Closing Instagram naturally...")
        
        # STEP 1: Trigger 'Recent Apps' View
        # KeyCode 187 is the standard Android App Switcher key
        self._adb_command("shell input keyevent 187")
        
        # CRITICAL PAUSE: Wait for the app card to visually zoom out.
        # If you swipe too early, the phone ignores it.
        self.sleep(1.5, 2.5)

        # STEP 2: Calculate the "Human Flick" Physics
        # Start Point: We grab the card slightly below the center (y=1300).
        # (Don't start at 1600+ or you might hit the nav bar/background)
        start_x = 540 + random.randint(-50, 50) 
        start_y = 1300 + random.randint(-50, 50) 

        # End Point: We throw it towards the top (y=200).
        # Drift: Add random horizontal movement (-100 to +100 px) so it's not a robot line.
        drift = random.randint(-100, 100)
        end_x = start_x + drift
        end_y = 200 + random.randint(-50, 50) 

        # Duration: FAST (150ms - 250ms) to trigger "Fling" momentum.
        duration = random.randint(150, 250)

        # STEP 3: Execute the Swipe
        cmd = f"shell input swipe {start_x} {start_y} {end_x} {end_y} {duration}"
        self._adb_command(cmd)
        
        # STEP 4: Reset to Home
        # Wait a second for the card to fly off screen
        self.sleep(1.0, 1.5)
        self._adb_command("shell input keyevent 3")

    def _log(self, msg):
        if self.verbose: 
            print(f"🤖 [Humanizer]: {msg}")
    
    def sleep(self, min_s=0.2, max_s=0.7):
        t = random.uniform(min_s, max_s)
        time.sleep(t)
    
    def tap(self, x, y, var=15):
        rx = x + random.randint(-var, var)
        ry = y + random.randint(-var, var)        
        self._adb_command(f"shell input tap {rx} {ry}")        
        self._log(f"Natural tap at {rx},{ry}")
        self.sleep(0.3, 0.8)

    def swipe(self, x1, y1, x2, y2):
        duration = random.randint(200, 450)        
        self._adb_command(f"shell input swipe {x1} {y1} {x2} {y2} {duration}")        
        self._log(f"Natural swipe: {duration}ms")
        self.sleep(0.5, 1.2)

    def mini_swipe_down(self):
        """
        Performs a short downward swipe in the center of the screen.
        Used to minimize comment sections or hide keyboards.
        """
        # Get screen dimensions (assuming 1080x1920, adjust if your phone differs)
        # Or better yet, use self.device.wm_size() to get them dynamically
        center_x = 540  
        start_y = 960  # Middle of screen
        end_y = 1100   # Move down slightly (140 pixels)
        
        # We use a very fast duration for a 'flick' feel
        duration = random.randint(100, 200) 
        
        self._log(f"Mini-swipe to minimize comments...")
        self._adb_command(f"shell input swipe {center_x} {start_y} {center_x} {end_y} {duration}")
        
        # Small wait for the UI animation to finish
        self.sleep(0.4, 0.8)
    


    def swipe_down(self, start_height_percentage=25, swipe_length_percentage=40):
        """
        High-speed natural 'flick' for the Blackwell pipeline.
        """
        size_output = self._adb_command("shell wm size", capture=True)
        m = re.search(r"(\d+)\s*x\s*(\d+)", str(size_output))
        if not m: return

        width, height = int(m.group(1)), int(m.group(2))

        # 1. Randomize X (Middle 20% of screen)
        x = int(width * (0.5 + random.uniform(-0.1, 0.1)))

        # 2. Faster Coordinate calculation
        start_y = int(height * (start_height_percentage / 100.0))
        end_y = int(start_y + height * (swipe_length_percentage / 100.0))

        # 3. QUICK DURATION (Human Flick range: 150ms - 250ms)
        # The 'Beast' needs to move fast to avoid detection of slow, linear drags.
        duration = random.randint(160, 240) 

        self._log(f"Flick down: y {start_y}->{end_y} ({duration}ms)")

        # Execute
        self._adb_command(f"shell input swipe {x} {start_y} {x} {end_y} {duration}")
        
        # Lower sleep for higher pipeline throughput
        self.sleep(0.2, 0.4)

    
    def swipe_down_from_box(box_x, box_y, box_w, box_h, duration_ms=300):
        # 1. Randomize Start Position (slightly off-center)
        start_x = box_x + (box_w // 2) + random.randint(-10, 10)
        start_y = box_y + (box_h // 4) + random.randint(-10, 10)
        
        # 2. Randomize End Position
        end_x = start_x + random.randint(-5, 5) # Keep swipe relatively straight
        end_y = box_y + (box_h * 3 // 4) + random.randint(-10, 10)
        
        # 3. Randomize Duration (between 400ms and 900ms)
        # This range feels like a natural "swipe" rather than a slow drag
        duration = random.randint(duration_ms, duration_ms + 100)


        # Calculate the starting point (center-top of the box)
        start_x = box_x + (box_w // 2)
        start_y = box_y + (box_h // 4)
        
        # Calculate the end point (bottom of the box)
        end_x = start_x
        end_y = box_y + (box_h * 3 // 4)
        
        # Construct the ADB command
        # Syntax: adb shell input swipe <x1> <y1> <x2> <y2> [duration]
        command = f"adb shell input swipe {start_x} {start_y} {end_x} {end_y} {duration_ms}"
        
        # Execute in Termux
        try:
            subprocess.run(command, shell=True, check=True)
            print(f"Swiped down from ({start_x}, {start_y}) to ({end_x}, {end_y})")
        except subprocess.CalledProcessError as e:
            print(f"Error executing ADB command: {e}")
    
    def swipe_random_feed(self):
        """A big, natural thumb swipe to move the feed."""
        h, w = 1920, 1080 # Or get from context
        start_y = random.randint(1200, 1500)
        end_y = random.randint(400, 700)
        start_x = random.randint(400, 600)
        self.swipe(start_x, start_y, start_x + random.randint(-50, 50), end_y)
    
    def tap_within_box(self, box, padding=5):
        """
        Clicks a random point inside the provided (x, y, w, h) box.
        padding: keeps the click away from the very edge of the button 
                to avoid missing it.
        """
        if not box or len(box) != 4:
            self._log("❌ Error: Invalid box provided to tap_within_box")
            return False

        x, y, w, h = box

        # 1. Define the 'Safe Zone' (contract the box slightly by padding)
        # This ensures we don't click the 1-pixel border of the button
        inner_x1 = x + padding
        inner_x2 = x + w - padding
        inner_y1 = y + padding
        inner_y2 = y + h - padding

        # 2. Pick a random coordinate within that safe zone
        # We use randint to simulate human touch variance
        target_x = random.randint(inner_x1, inner_x2)
        target_y = random.randint(inner_y1, inner_y2)

        # 3. Perform the ADB tap
        self._adb_command(f"shell input tap {target_x} {target_y}")
        
        self._log(f"Human-like tap inside box at: {target_x}, {target_y}")
        
        # 4. Human-like pause after clicking
        self.sleep(0.4, 0.9)
        return True
    
    def double_tap(self, x, y):
        """
        Executes a HUMAN-LIKE rapid double tap.
        - Creates a script on the phone (Termux/Shell) to bypass USB latency.
        - Adds random 'Jitter' so the 2nd tap is not on the exact same pixel.
        """
        print(f"🤖 [Humanizer]: Double-tapping around {x}, {y}")
        
        # 1. Calculate the jitter for the second tap
        # We move the second tap by 2-4 pixels randomly
        x2 = x + random.randint(-4, 4)
        y2 = y + random.randint(-4, 4)

        # 2. Prepare the script content
        # Input tap -> Sleep 40ms -> Input tap (offset)
        # We use single quotes for the echo content to avoid parsing issues
        script_content = f"input tap {x} {y}; sleep 0.04; input tap {x2} {y2}"
        
        # 3. Create the script on the phone
        # WE SEND THIS AS A LIST to prevent Windows from trying to interpret the ">" symbol
        create_cmd = f"echo '{script_content}' > /data/local/tmp/dt.sh"
        self._run_shell(create_cmd)
        
        # 4. Execute the script
        self._run_shell("sh /data/local/tmp/dt.sh")
        
        # 5. Cleanup
        self._run_shell("rm /data/local/tmp/dt.sh")
    
    def tap_left_of(self, anchor_box, min_offset=300, max_offset=400, padding_y=5):
        """
        Takes an anchor box [x, y, w, h] and taps a random spot 
        to the left of it (the conversation area).
        """
        ax, ay, aw, ah = anchor_box
        
        # Calculate the vertical center
        center_y = ay + (ah // 2)
        
        # Define the target area (400-500px to the left)
        # We create a virtual "target box" to tap within
        target_x_start = max(10, ax - max_offset)
        target_x_end = max(20, ax - min_offset)
        
        target_y_start = center_y - padding_y
        target_y_end = center_y + padding_y
        
        # Use a list format compatible with your tap_within_box [x, y, w, h]
        # target_w = distance between start and end
        new_box = [
            target_x_start, 
            target_y_start, 
            (target_x_end - target_x_start), 
            (target_y_end - target_y_start)
        ]
        
        self._log(f"Tapping relative left of anchor. Target Box: {new_box}")
        return self.tap_within_box(new_box)

    def _run_shell(self, cmd):
        """
        INTERNAL HELPER: Runs commands via Device Object OR Subprocess.
        """
        if self.device:
            # If using PPADB (Client)
            self.device.shell(cmd)
        else:
            # If using Pure ADB (Subprocess)
            # FIX: We verify if the command contains redirection (>)
            # If it does, we must be careful. The safest way for "echo > file" 
            # is to assume cmd is the full string to be executed ON THE DEVICE.
            try:
                # We pass the arguments as a list: ["adb", "shell", "COMMAND_STRING"]
                # This forces 'adb' to handle the string, not the Windows terminal.
                subprocess.run(["adb", "shell", cmd], check=True)
            except subprocess.CalledProcessError:
                pass
            except FileNotFoundError:
                print("❌ Error: 'adb' not found. Check your PATH.")
    
    def type_quick(self, text):
        self._log(f"Fast typing: {text}")
        
        for char in text:
            if char == " ":
                self._adb_command("shell input keyevent 62")
            else:
                # Escape single quotes and backslashes for the shell
                clean_char = char.replace("'", "'\\''")
                self._adb_command(f"shell input text '{clean_char}'")
            
            # 0.02s is the limit for the Blackwell/5090 sync speed
            time.sleep(0.02)

        # --- THE SYNC FIX ---
        # 1. Send an 'Enter' or 'Tab' to force the IME to commit the buffer
        # This prevents the 'd' from sticking to the end of the word
        self._adb_command("shell input keyevent 66") # 66 is ENTER
        
        # 2. Add a tiny 'Cool down' so the UI catches up
        time.sleep(0.4)

    def type_text(self, text, typo_chance=0.01):
        """
        Types string character by character with a chance of neighbor-key typos.
        Uses a robust backspace-and-wait loop to ensure typos are cleared.
        """
        self._log(f"Typing: '{text}'")
        
        for char in text:
            # 🎲 1. Typos Logic
            if char.lower() in self.key_neighbors and random.random() < typo_chance:
                neighbors = self.key_neighbors[char.lower()]
                typo_char = random.choice(neighbors)
                if char.isupper():
                    typo_char = typo_char.upper()
                
                self._log(f" oops... typo: '{typo_char}' instead of '{char}'")
                
                # 1. Type the typo
                self._send_key(typo_char)
                
                # 🛑 FIX 1: Heavy wait to ensure the typo is rendered in the text field
                # If we backspace too fast, Android ignores it.
                time.sleep(random.uniform(0.2, 0.4)) 
                
                # 2. Backspace (Keycode 67)
                # 🛑 FIX 2: Send the keyevent and add a secondary pause 
                # to let the cursor reposition
                self._adb_command("shell input keyevent 67") 
                time.sleep(random.uniform(0.3, 0.45))
                
                # 🛑 FIX 3: Optional "double backspace" safety
                # Un-comment if the phone is very laggy:
                # self._adb_command("shell input keyevent 67")
                # time.sleep(0.1)

            # ⌨️ 2. Type the correct character
            self._send_key(char)
            
            # ⏱️ 3. Natural Typing Speed
            # Slightly slower for better reliability on mobile
            time.sleep(random.uniform(0.08, 0.28))

        # Natural delay after finishing the sentence
        time.sleep(random.uniform(0.5, 0.8))

    def _send_key(self, char):
        """Helper to send single character via ADB safely."""
        if char == " ":
            self._adb_command("shell input text %s") # %s is ADB code for space
        elif char == "'":
            self._adb_command(r"shell input text \'") # Escape single quote
        elif char == '"':
            self._adb_command(r'shell input text \"') # Escape double quote
        else:
            # Standard input
            self._adb_command(f"shell input text {char}")

    def human_scroll_inbox(self, direction="down"):
        """
        Advanced human-like scrolling.
        - Flexible Speed: Duration is calculated based on distance + random velocity noise.
        - Human Jitter: Start/End points never repeat.
        - Thumb Arc: Adds horizontal drift to mimic right-handed thumb usage.
        """
        # 1. DECIDE INTENT (Scanning vs. Reading)
        # "Normal" = Fast scan. "Micro" = Slow adjustment.
        scroll_type = "normal" if random.random() < 0.8 else "micro"

        # 2. X-AXIS JITTER (Thumb Drift)
        # Humans tend to scroll on the right side (right-handed bias)
        # but the start point jitters left/right every time.
        base_x = 540 + random.randint(50, 150) 
        start_x = base_x + random.randint(-20, 20)
        
        # The drift: As the thumb moves up, it naturally pulls slightly inward or outward.
        drift = random.randint(-50, 50)
        end_x = start_x + drift

        # 3. Y-AXIS & DISTANCE CALCULATION
        # Determine how far we want to scroll based on intent
        if scroll_type == "normal":
             # Big swipe (scanning feed)
            target_distance = random.randint(450, 700)
            # Speed Factor: 1.2 to 1.8 pixels per ms (Fast/Casual)
            speed_factor = random.uniform(1.2, 1.8) 
        else:
            # Micro adjustment (oops, missed a line)
            target_distance = random.randint(100, 250)
            # Speed Factor: 0.5 to 0.9 pixels per ms (Slow/Precise)
            speed_factor = random.uniform(0.5, 0.9)

        # 4. CALCULATE DURATION (Flexible Speed Logic)
        # Physics: Time = Distance / Speed
        calculated_duration = int(target_distance / speed_factor)
        
        # Add "Human Noise" to duration (imperfection)
        # Humans aren't robots; sometimes we drag slightly slower/faster mid-swipe
        noise = random.randint(-50, 50)
        final_duration = max(100, calculated_duration + noise)

        # 5. DIRECTION LOGIC
        if direction == "down":
            # Drag UP to see content DOWN
            start_y = 1500 + random.randint(-100, 100) # Start low
            end_y = start_y - target_distance
        else:
            # Drag DOWN to see content UP
            start_y = 400 + random.randint(-50, 50) # Start high
            end_y = start_y + target_distance

        # 6. EXECUTE
        # We ensure coordinates stay within screen bounds (roughly)
        start_x = max(100, min(980, start_x))
        end_x = max(100, min(980, end_x))
        start_y = max(200, min(2000, start_y))
        end_y = max(200, min(2000, end_y))

        cmd = f"shell input swipe {start_x} {start_y} {end_x} {end_y} {final_duration}"
        self._adb_command(cmd)

        # 7. MOMENTUM PAUSE
        # The "Reading" pause is critical. 
        # Variable pause based on how far we scrolled (longer scroll = eye needs more time to settle)
        pause_base = random.uniform(0.6, 1.2)
        if scroll_type == "normal":
            pause_base += 0.5 # Add extra time to "read" after a big scroll
            
        self.sleep(pause_base, pause_base + 0.5)
    
    def scroll_to_bottom(self):
        
        stuck_count = 0
        max_scrolls = 50 # Safety limit
        
        for i in range(max_scrolls):
            
            # 1. Capture State BEFORE
            img_before = self._get_screenshot()
            
            # 2. Scroll
            self.human_scroll_inbox(direction="down")
            
            # 3. Capture State AFTER
            img_after = self._get_screenshot()
            
            # 4. Check if we moved
            if self.is_screen_identical(img_before, img_after):
                print("⚠️ Screen didn't move. Possible bottom?")
                stuck_count += 1
            else:
                stuck_count = 0 # Reset if we moved successfully
                
            # 5. Confirmation Logic
            # If we are stuck for 2 consecutive tries, we are definitely at the bottom.
            if stuck_count >= 2:
                print("✅ Reached the bottom of the inbox.")
                break
                
            # Random human pause between scrolls
            self.sleep(1.0, 2.0)

    def _get_screenshot(self):
        """This is your get_live_screen function, moved here."""
        cmd = ["adb", "exec-out", "screencap", "-p"]
        try:
            raw_data = subprocess.check_output(cmd)
            # Update the 'eyes'
            return cv2.imdecode(np.frombuffer(raw_data, np.uint8), cv2.IMREAD_COLOR)
        except Exception as e:
            print(f"❌ ADB Capture Failed: {e}")
            return False
    
    def lock_phone(self):
        """
        Turns the screen off (simulates pressing the Power button).
        """
        print("   [Action] Locking phone (Screen Off)...")
        # KeyCode 26 = POWER
        self._adb_command("shell input keyevent 26")
    
    def is_screen_identical(self, old_image, new_image):
        """
        Compares old_image against new_image to see if we moved.
        Returns True if the screen is STATIC (didn't move/reached bottom).
        """
        if old_image is None or new_image is None:
            return False

        # 1. CROP (Crucial Step)
        # We assume 1080x1920 (Portrait). 
        # Crop out Top Bar (Clock) and Bottom Bar (Nav) to avoid noise.
        h, w, _ = new_image.shape
        crop_top = int(h * 0.15)    # Skip top 15%
        crop_bottom = int(h * 0.85) # Skip bottom 15%

        # Use new_image here instead of self.screen
        img1_crop = old_image[crop_top:crop_bottom, :, :]
        img2_crop = new_image[crop_top:crop_bottom, :, :]

        # 2. COMPARE
        # Convert to grayscale for speed
        gray1 = cv2.cvtColor(img1_crop, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2_crop, cv2.COLOR_BGR2GRAY)

        # Calculate absolute difference
        diff = cv2.absdiff(gray1, gray2)
        
        # Count how many pixels are different
        non_zero = np.count_nonzero(diff)
        
        # If less than 1% of pixels changed, we are stuck.
        total_pixels = diff.size
        similarity = 1 - (non_zero / total_pixels)
        
        return similarity > 0.99