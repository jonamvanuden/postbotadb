import cv2
import numpy as np
import os
import ollama
import json_repair

class OCR:
    @staticmethod
    def extract_comments_from_screen(screen):
        img = screen
        
        # 2. THE FIX: CLAHE (Contrast Limited Adaptive Histogram Equalization)
        # This makes the faint Blue mentions (@username) pop out as dark text.
        
        # Convert to LAB color space (Luminance, A, B)
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE to the L (Lightness) channel
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        cl = clahe.apply(l)
        
        # Merge back and convert to BGR
        limg = cv2.merge((cl, a, b))
        final_img = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        
        # Optional: Slight sharpening to separate "you" from "Leon"
        kernel = np.array([[0, -1, 0], [-1, 5,-1], [0, -1, 0]])
        final_img = cv2.filter2D(final_img, -1, kernel)

        # ---------------------------------------------------------
        # 2. THE MEMORY FIX: Encode directly to Bytes (No Disk I/O)
        # ---------------------------------------------------------
        # We "pretend" to save it as a JPG, but keep it in RAM variable 'buffer'
        success, buffer = cv2.imencode('.jpg', final_img)
        
        if not success:
            print("❌ Failed to encode image to bytes")
            return []

        image_bytes = buffer.tobytes()

        # 3. THE PROMPT (Specific instructions for @mentions)
        prompt = """
        Extract ALL comments from this Instagram screenshot.
        
        CRITICAL RULES FOR ACCURACY:
        1. **Detect Mentions:** If a comment starts with or contains a username (often blue), KEEP IT (e.g., "@vinny thanks").
        2. **Fix Merged Text:** If a name is stuck to a word (e.g., "thankyouLeon"), split it ("thank you Leon").
        3. **Capture Replies:** Do not ignore the "@username" at the start of a reply.
        
        Structure:
        {
          "comments": [
            { "username": "exact_handle", "time" : "2w 1d whatever", " "content": "@target_user text ❤️" }
          ]
        }
        """

        try:
            response = ollama.chat(
                model='qwen2.5vl:latest', 
                format='json',
                options={
                    'temperature': 0,
                    'num_ctx': 8192,
                    'repeat_penalty': 1.1 
                },
                messages=[{
                    'role': 'user',
                    'content': prompt,
                    'images': [image_bytes]
                }]
            )

            data = json_repair.loads(response['message']['content'])
            if isinstance(data, dict):
                return data.get('comments', [])
            elif isinstance(data, list):
                return data
            return []

        except Exception as e:
            print(f"❌ Error: {e}")
            return []

    @staticmethod
    def extract_comments_by_filepath(image_path):
        print(f"👁️ Qwen 7B (Contrast Boost) is reading {image_path}...")
        
        if not os.path.exists(image_path):
            return []

        # 1. LOAD IMAGE
        img = cv2.imread(image_path)
        
        # 2. THE FIX: CLAHE (Contrast Limited Adaptive Histogram Equalization)
        # This makes the faint Blue mentions (@username) pop out as dark text.
        
        # Convert to LAB color space (Luminance, A, B)
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE to the L (Lightness) channel
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        cl = clahe.apply(l)
        
        # Merge back and convert to BGR
        limg = cv2.merge((cl, a, b))
        final_img = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        
        # Optional: Slight sharpening to separate "you" from "Leon"
        kernel = np.array([[0, -1, 0], [-1, 5,-1], [0, -1, 0]])
        final_img = cv2.filter2D(final_img, -1, kernel)

        # Save for AI
        temp_path = "temp_boosted.jpg"
        cv2.imwrite(temp_path, final_img)

        # 3. THE PROMPT (Specific instructions for @mentions)
        prompt = """
        Extract ALL comments from this Instagram screenshot.
        
        CRITICAL RULES FOR ACCURACY:
        1. **Detect Mentions:** If a comment starts with or contains a username (often blue), KEEP IT (e.g., "@vinny thanks").
        2. **Fix Merged Text:** If a name is stuck to a word (e.g., "thankyouLeon"), split it ("thank you Leon").
        3. **Capture Replies:** Do not ignore the "@username" at the start of a reply.
        
        Structure:
        {
          "comments": [
            { "username": "exact_handle", "time" : "2w 1d whatever", " "content": "@target_user text ❤️" }
          ]
        }
        """

        try:
            response = ollama.chat(
                model='qwen2.5vl:latest', 
                format='json',
                options={
                    'temperature': 0,
                    'num_ctx': 8192,
                    'repeat_penalty': 1.1 
                },
                messages=[{
                    'role': 'user',
                    'content': prompt,
                    'images': [temp_path]
                }]
            )

            data = json_repair.loads(response['message']['content'])
            if isinstance(data, dict):
                return data.get('comments', [])
            elif isinstance(data, list):
                return data
            return []

        except Exception as e:
            print(f"❌ Error: {e}")
            return []
            
    @staticmethod
    def extract_chat_from_screen(screen):
        img = screen
        
        # 2. THE FIX: CLAHE (Contrast Limited Adaptive Histogram Equalization)
        # This makes the faint Blue mentions (@username) pop out as dark text.
        
        # Convert to LAB color space (Luminance, A, B)
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE to the L (Lightness) channel
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        cl = clahe.apply(l)
        
        # Merge back and convert to BGR
        limg = cv2.merge((cl, a, b))
        final_img = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        
        # Optional: Slight sharpening to separate "you" from "Leon"
        kernel = np.array([[0, -1, 0], [-1, 5,-1], [0, -1, 0]])
        final_img = cv2.filter2D(final_img, -1, kernel)

        # ---------------------------------------------------------
        # 2. THE MEMORY FIX: Encode directly to Bytes (No Disk I/O)
        # ---------------------------------------------------------
        # We "pretend" to save it as a JPG, but keep it in RAM variable 'buffer'
        success, buffer = cv2.imencode('.jpg', final_img)
        
        if not success:
            print("❌ Failed to encode image to bytes")
            return []

        image_bytes = buffer.tobytes()

        # 3. THE PROMPT (Specific instructions for @mentions)
        prompt = """
        You are a specialized OCR engine for Instagram CHAT SCREENS only.

        CRITICAL VALIDATION:
        - If the image contains a list of multiple different people/profiles (Inbox view), RETURN AN EMPTY LIST.
        - DO NOT invent messages. If it's not in a bubble, it doesn't exist.

        STEP 1: IDENTIFY THE HEADER
        - Look at the VERY TOP of the screen for the current contact name. To the left are a white arrow and a 
          photo in the cirle. To the right are a phone and camera icon. Take the name there and use it as [HANDLE]

        STEP 2: SPATIAL BUBBLE RULES
        - RIGHT SIDE bubbles (Purple/Gradient): Set "sender": "Me".
        - LEFT SIDE bubbles (Gray/Black): Set "sender": "[HANDLE]".
        - IGNORE the small profile icons next to bubbles; only look at bubble position.
        - You MUST extract messages in the exact order they appear from TOP to BOTTOM.
        - Even if a sender speaks twice, if there is a message from someone else in between them vertically, you must preserve that order.
        - Vertical position (Y-coordinate) is the ONLY way to determine message order. 
        - DO NOT group messages by sender.

        STEP 3: NOISE REMOVAL
        - DO NOT extract: "Tap and hold to react", "Active now", "Seen", "Sent".
        - ONLY extract the text INSIDE the bubbles and timestamps as [TIMESTAMPS] when visible.

        OUTPUT JSON FORMAT:
        {
          "participant": { "handle": "[HANDLE]" },
          "messages": [
            { 
                "sender": "[HANDLE or Me]", 
                "content": "exact text", 
                "timestamp": "[TIMESTAMPS]", 
                "type": "text" 
            }
          ]
        }
        """


        try:
            response = ollama.chat(
                model='qwen2.5vl:latest', 
                format='json',
                options={
                    'temperature': 0,
                    'num_ctx': 8192,
                    'repeat_penalty': 1.1 
                },
                messages=[{
                    'role': 'user',
                    'content': prompt,
                    'images': [image_bytes]
                }]
            )

            data = json_repair.loads(response['message']['content'])
            if isinstance(data, dict):
                return data.get('messages', [])
            elif isinstance(data, list):
                return data
            return []

        except Exception as e:
            print(f"❌ Error: {e}")
            return []
        
class Locator:
    @staticmethod
    def find_btn(
        template_path,
        screen_image,
        threshold=0.8,
        screenpart="whole"  # "whole", "top", "bottom"
    ):

        if screen_image is None:
            print("No screen image found!")
            return None

        img_rgb = screen_image
        height, width = img_rgb.shape[:2]

        # --- Select screen region ---
        y_offset = 0

        match screenpart:
            case "top":
                img_rgb = img_rgb[: height // 2, :]
                y_offset = 0

            case "bottom":
                # Only search the bottom 10% of the screen
                # Start at 90% of height, go to the end
                img_rgb = img_rgb[int(height * 0.90) :, :]
                y_offset = int(height * 0.90)

            case "whole" | None:
                pass  # use full screen

            case _:
                raise ValueError(f"Invalid screenpart: {screenpart}")

        # Determine if we need to isolate white points (the dots)
        need_mask = "account-details" in template_path

        if need_mask:
            # --- MODE A: MASKED COLOR MATCHING ---
            template = cv2.imread(template_path)
            if template is None:
                raise FileNotFoundError(f"Template not found: {template_path}")
            
            # Create a mask targeting only the white dots (thresholding pixels above 200)
            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            _, mask = cv2.threshold(template_gray, 200, 255, cv2.THRESH_BINARY)
            
            # Masked matching works best with TM_CCORR_NORMED
            res = cv2.matchTemplate(img_rgb, template, cv2.TM_CCORR_NORMED, mask=mask)
            w, h = template.shape[1], template.shape[0]
        else:
            # --- MODE B: STANDARD GRAYSCALE MATCHING ---
            img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
            template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
            if template is None: raise FileNotFoundError(f"Template not found: {template_path}")
            
            res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
            w, h = template.shape[::-1]

        # --- PROCESS RESULTS ---
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        if max_val >= threshold:
            x, y = max_loc
            # Adjust Y coordinate based on the screenpart offset
            return (x, y + y_offset, w, h)

        print(f"No match found for: {os.path.basename(template_path)}")
        return None 
    
    @staticmethod
    def find_all_btns(template_path, screen_image, threshold=0.7):
        """Returns a list of all found (x, y, w, h) for a template."""
        print(f"trying to open file: {template_path}")
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        img_gray = cv2.cvtColor(screen_image, cv2.COLOR_BGR2GRAY)
        
        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        locs = np.where(res >= threshold)
        
        found = []
        w, h = template.shape[::-1]
        for pt in zip(*locs[::-1]):
            # Filter out points that are too close to each other (duplicates)
            if not any(abs(pt[0] - f[0]) < 10 and abs(pt[1] - f[1]) < 10 for f in found):
                found.append((pt[0], pt[1], w, h))
        
        # Sort by Y coordinate (top to bottom)
        return sorted(found, key=lambda x: x[1])

    @staticmethod
    def find_unread_conversations(template_path, screen_image, threshold=0.9):
        """
        Specifically finds unread message rows by looking for the camera icon 
        AND verifying the purple/blue unread dot exists via HSV color masking.
        """
        # 1. Standard Template Match (Grayscale) to find the Camera/Dot area
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        img_gray = cv2.cvtColor(screen_image, cv2.COLOR_BGR2GRAY)
        w, h = template.shape[::-1]
        
        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        locs = np.where(res >= threshold)
        
        candidates = []
        for pt in zip(*locs[::-1]):
            # Deduplicate matches that are too close (within 10px)
            if not any(abs(pt[0] - f[0]) < 10 and abs(pt[1] - f[1]) < 10 for f in candidates):
                candidates.append((pt[0], pt[1], w, h))

        # 2. Color Verification Loop
        unread_btns = []
        for (x, y, w, h) in candidates:
            # Define the Region of Interest (ROI) - the area of the detected button
            roi = screen_image[y:y+h, x:x+w]
            
            # Convert ROI to HSV color space
            hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            
            # Instagram's unread blue/purple dot in HSV
            # Adjust these if your screen brightness/blue-light filter is on
            lower_purple = np.array([105, 70, 70])
            upper_purple = np.array([135, 255, 255])
            
            mask = cv2.inRange(hsv_roi, lower_purple, upper_purple)
            purple_count = cv2.countNonZero(mask)
            
            # LOGGING: Helps you debug if it's missing real ones
            # print(f"Candidate at {x},{y} has {purple_count} purple pixels")

            if purple_count > 8:  # Requires a cluster of purple pixels to be "unread"
                unread_btns.append((x, y, w, h))
                
        # Sort top to bottom
        return sorted(unread_btns, key=lambda b: b[1])
    
    @staticmethod
    def find_inbox_btn(screen):
        # Define your templates and their specific thresholds in order of priority
        templates = [
            ("btn-inbox.png", 0.9),
            ("btn-inbox-selected.png", 0.9),
            ("btn-inbox-unread.png", 0.7),
            ("btn-inbox-selected-unread.png", 0.7)
        ]

        return Locator.find_btn_by_templates(screen, templates, "main", "bottom")
    
    @staticmethod
    def find_btn_send(screen):
        templates = [
            ("btn-inbox-send.png", 0.9)
        ] 
        return Locator.find_btn_by_templates(screen, templates, "inbox")
    
    @staticmethod
    def find_btn_back(screen):
        templates = [
            ("btn-back-transparent.png", 0.9),
            ("btn-back.png", 0.9)
        ]
        return Locator.find_btn_by_templates(screen, templates, "main")

    @staticmethod            
    def find_profile_btn(screen, username):
        match username:
            case "thelifeofaime":
                templates = [
                    ("btn-profile-aime.png", 0.90),
                    ("btn-profile-aime-selected.png", 0.90)                
                ]
            case "other":
                templates = [
                    ("btn-profile-whoever", 0.95)
            ]
        return Locator.find_btn_by_templates(screen, templates, "main", "bottom")

    @staticmethod
    def find_reel_btn(screen):
        templates = [
            ("btn-reel-selected.png", 0.9),
            ("btn-reel.png", 0.9)
        ]
        return Locator.find_btn_by_templates(screen, templates, "main", "bottom")
    
    @staticmethod
    def find_search_btn(screen):
        templates = [
            ("btn-search.png", 0.9)
        ]
        return Locator.find_btn_by_templates(screen, templates, "main", "bottom")

    @staticmethod
    def find_home_btn(screen):
        templates = [
            ("btn-home-selected.png", 0.9),
            ("btn-home.png", 0.9)
        ]

        return Locator.find_btn_by_templates(screen, templates, "main")
    
    @staticmethod
    def find_comment_btn_on_homefeed(screen):
        templates = [
            ("btn-comment.png", 0.9)
        ]

        return Locator.find_btn_by_templates(screen, templates, "home")
    
    @staticmethod
    def find_comment_header(screen):
        templates = [
            ("comment-header.png", 0.95)
        ]

        return Locator.find_btn_by_templates(screen, templates, "home", "top")

    @staticmethod
    def find_btn_by_templates(screen, templates, directory, screenpart=None):        
        for filename, threshold in templates:
            path = Locator.get_btn_filename(filename, directory)
            box = Locator.find_btn(path, screen, threshold, screenpart)
            
            if box:
                print(f"✅ Found inbox button state: {filename}")
                return box
            
        # If the loop finishes without returning, nothing was found
        names = ", ".join(filename for filename, _ in templates)
        raise Exception(f"{names} button not found in any known state!")
    
    @staticmethod
    def get_btn_filename(file, directory):
        # 1. This gets: C:\platform-tools\instabotfinal\instabot
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 2. This gets the PARENT: C:\platform-tools\instabotfinal
        parent_dir = os.path.dirname(current_dir)
        
        # 3. Now build the path from the parent
        full_path = os.path.join(parent_dir, "ui-images", directory, file)
        
        # 4. Clean up slashes for Windows
        return os.path.normpath(full_path)
    
    @staticmethod
    def get_screenshot_filename(file):
        parent = os.path.dirname(os.getcwd())
        return parent + "/instabot/all_screenshots/" + file