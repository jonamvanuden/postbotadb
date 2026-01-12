import cv2
import numpy as np
import os


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
            if template is None:
                raise FileNotFoundError(f"Template not found: {template_path}")
            
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
    def find_profile_btn(screen, username):
        match username:
            case "thelifeofaime":
                templates = [
                    ("btn-profile-aime.png", 0.95)                
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