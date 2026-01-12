import os, cv2, random, time, subprocess, numpy as np

class Humanizer:
    def __init__(self, verbose=True):
        self.verbose = verbose
        self.device = None
    
    def _adb_command(self, cmd):
        """Internal helper to run ADB commands silently."""
        subprocess.run(f"adb {cmd} > nul 2>&1", shell=True)

    def _log(self, msg):
        if self.verbose: 
            print(f"🤖 [Humanizer]: {msg}")
    
    def sleep(self, min_s=0.2, max_s=1.1):
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
    
