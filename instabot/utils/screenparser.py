import cv2
import numpy as np
import os, glob
import ollama
import json
import easyocr
from PIL import Image
import torch
from transformers import TrOCRProcessor, VisionEncoderDecoderModel, AutoModel, AutoTokenizer
import numpy as np
import logging, warnings
from paddleocr import PaddleOCR
from transformers import AutoModelForCausalLM, AutoProcessor
import time

# Silence all standard transformer and system warnings
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
logging.getLogger("transformers").setLevel(logging.ERROR)
warnings.filterwarnings("ignore")

#paddle ocr
os.environ.setdefault("DISABLE_MODEL_SOURCE_CHECK", "True") 
_got_tokenizer = None
_got_model = None

class ScreenParser:
    def __init__(self):
        # Define phrases that indicate a message is from the System
        self.system_phrases = [
            "tap and hold to react",
            "seen",
            "sent",
            "typing...",
            "message...",
            "disappearing messages",
            "turned on disappearing",
            "change" 
        ]

    def get_chat_header(self, full_img):
        """
        Extracts the Username/Handle from the top of the screen.
        """
        h, w = full_img.shape[:2]

        # --- STEP 1: DEFINE THE HEADER BOX ---
        # Based on your screenshots (1080x2400 typical):
        # Y: 5% to 15% (Skips the status bar clock, captures the name)
        # X: 15% to 70% (Skips the Back Arrow/Avatar, captures the text)
        
        y1, y2 = int(h * 0.05), int(h * 0.15)
        x1, x2 = int(w * 0.18), int(w * 0.70) # Start at 18% to skip the Avatar face

        header_crop = full_img[y1:y2, x1:x2]

        # --- STEP 2: REUSE YOUR ROBUST READER ---
        # We reuse the reader we just built because:
        # 1. It has Gamma Correction (makes the grey @username readable).
        # 2. It has Lanczos Upscaling (makes small text sharp).
        
        # We use a custom prompt for this specific task
        return self.read_header_with_qwen(header_crop)

    def read_header_with_qwen(self, header_image, model_name='qwen2.5vl:latest'):
        """
        Specialized reader for the Header (Name + Handle).
        """
        if header_image is None or header_image.size == 0: return "Unknown"

        # Reuse your Gamma/Upscale logic (Copy-paste the good parts)
        invGamma = 1.0 / 1.5
        table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
        header_image = cv2.LUT(header_image, table)
        
        # Zoom in for clarity
        header_image = cv2.resize(header_image, None, fx=3.0, fy=3.0, interpolation=cv2.INTER_LANCZOS4)
        
        # Add padding
        header_image = cv2.copyMakeBorder(header_image, 20, 20, 20, 20, cv2.BORDER_CONSTANT, value=[0, 0, 0])

        success, buffer = cv2.imencode('.jpg', header_image)
        image_bytes = buffer.tobytes()

        # --- PROMPT: HEADER EXTRACTION ---
        prompt = (
            "Read the social media header.\n"
            "It usually contains a Display Name (white) and a Username/Handle (grey).\n"
            "Output format: 'Name (@handle)'.\n"
            "If only one name is visible, output that.\n"
            "Do NOT output the status (like 'Active now').\n"
            "Output ONLY the name info."
        )

        try:
            response = ollama.chat(
                model=model_name,
                options={'temperature': 0, 'num_ctx': 1024},
                messages=[{'role': 'user', 'content': prompt, 'images': [image_bytes]}]
            )
            return response['message']['content'].strip()
        except:
            return "Unknown"

    def crop_box_from_image(self, image, box, padding=0):
        """
        Crops a region from an image based on a bounding box.
        
        :param image: The full numpy image array (cv2.imread result).
        :param box: A list or tuple of [x, y, w, h].
        :param padding: Optional pixels to add around the box (default 0).
        :return: The cropped numpy image array.
        """
        if image is None or len(box) < 4:
            return None

        # Unpack the box
        x, y, w, h = box
        img_h, img_w = image.shape[:2]

        # Calculate coordinates with optional padding
        # We use max/min to ensure we never go outside the image boundaries (which causes crashes)
        x1 = max(0, x - padding)
        y1 = max(0, y - padding)
        x2 = min(img_w, x + w + padding)
        y2 = min(img_h, y + h + padding)

        # Perform the slice
        cropped_img = image[y1:y2, x1:x2]

        return cropped_img\
               
    def read_bubble_with_qwen(self, bubble_image, is_system_message=False, model_name='qwen2.5vl:latest'):       

        """
        THE ULTIMATE READER.
        Philosophy: Do not distort the pixels. Just make them brighter and bigger.
        
        1. Gamma Correction: Lifts invisible gray text without adding noise.
        2. Lanczos Upscale: Smooths text naturally (fixes 'Hell' vs 'Hello').
        3. Heavy Framing: Focuses the AI's attention (fixes 'goingd').
        """
        if bubble_image is None or bubble_image.size == 0:
            return ""

        # --- STEP 1: GAMMA CORRECTION (The Secret Sauce) ---
        # Instead of CLAHE (which adds noise), we use Gamma. 
        # Gamma=1.5 makes dark-gray text bright enough to read, but keeps black black.
        # This prevents the AI from hallucinating in the dark background.
        invGamma = 1.0 / 1.5
        table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
        bubble_image = cv2.LUT(bubble_image, table)

        # --- STEP 2: INTELLIGENT UPSCALE ---
        # We check the height. We want the text to be large (approx 50-100px tall).
        h, w = bubble_image.shape[:2]
        
        # If it's a tiny "Ok" bubble, zoom 4x. If it's a paragraph, zoom 2x.
        if h < 50:
            zoom = 4.0
        elif h < 100:
            zoom = 3.0
        else:
            zoom = 2.0
            
        bubble_image = cv2.resize(bubble_image, None, fx=zoom, fy=zoom, interpolation=cv2.INTER_LANCZOS4)

        # --- STEP 3: THE "ATTENTION" FRAME ---
        # We add a MASSIVE black border. 
        # Why? VLMs often ignore the outer 10% of an image. This pushes text to the "safe center".
        bubble_image = cv2.copyMakeBorder(
            bubble_image, 60, 60, 60, 60, cv2.BORDER_CONSTANT, value=[0, 0, 0]
        )

        # Encode
        success, buffer = cv2.imencode('.jpg', bubble_image)
        if not success: return ""
        image_bytes = buffer.tobytes()

        # --- STEP 4: BINARY PROMPTING ---
        # We force the AI into two different "Modes" so it never confuses a timestamp for slang.
        
        if is_system_message:
            # MODE A: The "Robot" (System Messages)
            prompt = (
                "OCR TASK: Extract the alphanumeric text from this system label.\n"
                "- Content is usually a Date, Time, or Status (e.g., 'Thurs 07:50', 'Seen').\n"
                "- Output ONLY the text.\n"
                "- NO chat conversation. NO emojis."
            )
        else:
            # MODE B: The "Transcriber" (Chat Bubbles)
            prompt = (
                "You are a dumb OCR engine. You do NOT understand language. You only recognize shapes.\n"
            "TASK: Output the text string exactly as shown in the image.\n"
            "NEGATIVE CONSTRAINTS (CRITICAL):\n"
            "1. DO NOT fix spelling or grammar. If it says 'goingd', output 'goingd'.\n"
            "2. DO NOT add emojis that are not clearly visible pixels.\n"
            "3. DO NOT rephrase sentences. (e.g., Do not change 'Caught' to 'Can't wait').\n"
            "4. DO NOT autocomplete thoughts.\n"
            "Output ONLY the exact string."
            )

            prompt = (
            "You are a strict, pixel-perfect OCR engine.\n"
            "TASK: Transcribe the content exactly as it appears visually.\n"
            "CRITICAL RULES:\n"
            "1. EXACT SPELLING: Map letters one-to-one. If it says 'goingd', output 'goingd'. Do NOT fix grammar.\n"
            "2. EXACT COUNT: Respect visual quantity. If you see ONE emoji, output ONE. Do not repeat symbols (e.g. output '👋', not '👋👋').\n"
            "3. NO AUTOCOMPLETE: Do not finish sentences or add invisible punctuation.\n"
            "Output ONLY the raw string."
            )



        try:
            response = ollama.chat(
                model=model_name,
                options={
                    'temperature': 0,    # Absolute zero creativity
                    'num_ctx': 4096,      # High context window for precision
                    'repeat_penalty': 1.1
                },
                messages=[{
                    'role': 'user',
                    'content': prompt,
                    'images': [image_bytes]
                }]
            )
            return response['message']['content'].strip()

        except Exception as e:
            print(f"⚠️ Qwen Error: {e}")
            return ""

    def parse_chat_screen(self, image_path_or_array):

        # 1. LOAD & ROI
        if isinstance(image_path_or_array, str):
            img = cv2.imread(image_path_or_array)
        else:
            img = image_path_or_array


        username = self.get_chat_header(img)

        h, w, _ = img.shape
        debug_img = img.copy()

        y_start = int(h * 0.12)
        y_end = int(h * 0.92) 
        roi = img[y_start:y_end, :]

        # 2. EDGE DETECTION
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)

        # 3. HORIZONTAL SMEAR
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 1))
        closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
        
        # 4. FIND BOXES
        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        bubbles = []
        
        for cnt in contours:
            x, y, bw, bh = cv2.boundingRect(cnt)
            y_global = y + y_start
            
            # Filters
            if bh < 15 or bw < 40: continue
            if y_global > (h * 0.90): continue

            # Merging Overlaps
            is_new = True
            for b in bubbles:
                existing_y = b['box'][1]
                existing_h = b['box'][3]
                if abs(y_global - existing_y) < 50: 
                    new_y = min(y_global, existing_y)
                    new_h = max(y_global + bh, existing_y + existing_h) - new_y
                    b['box'] = [b['box'][0], new_y, b['box'][2], new_h]
                    b['y_pos'] = new_y
                    b['crop_coords'] = (b['crop_coords'][0], new_y, b['crop_coords'][2], new_y + new_h)
                    is_new = False
                    break
            
            if not is_new: continue

            # --- CATEGORIZE (Alignment Based) ---
            # FIX: Use Left/Right Edges instead of Center X
            
            # 1. Is it a LEFT bubble? (Starts near the left edge)
            # Limit: Starts within first 15% of screen width
            if x < (w * 0.15):
                cat = "left"
                sender = username # or "Them"
            
            # 2. Is it a RIGHT bubble? (Ends near the right edge)
            # Limit: Ends within last 15% of screen width
            elif (x + bw) > (w * 0.85):
                cat = "right"
                sender = "Me"
                
            # 3. Must be Middle/System (Timestamps, etc.)
            else:
                cat = "middle"
                sender = "System"

            bubbles.append({
                "category": cat,
                "sender": sender,
                "y_pos": y_global,
                "box": [x, y_global, bw, bh],
                "crop_coords": (x, y_global, x+bw, y_global+bh)
            })

        # 5. SORT & READ
        bubbles.sort(key=lambda x: x["y_pos"])

        final_history = []
        print(f"   [EdgeParser] Found {len(bubbles)} items.")

        # Keep only the last 4 bubbles (the most recent ones at the bottom)
        bubbles = bubbles[-4:]
        
        for b in bubbles:
            x1, y1, x2, y2 = b["crop_coords"]
            crop = img[y1:y2, x1:x2]
            
            try:
                is_system = b["sender"] == "System"
                content = self.read_bubble(crop, is_system)
                content = content.strip()
            except:
                content = ""

            # --- SYSTEM OVERRIDE ---
            # Even if it aligns left (like "Disappearing messages"), 
            # if the TEXT says it's system, we force it to System.
            for phrase in self.system_phrases:
                if phrase in content.lower():
                    # print(f"      ⚙️ Re-classified as System: '{content[:20]}...'")
                    b["sender"] = "System"
                    b["category"] = "middle"
                    break

            # Draw Debug
            if b["sender"] == "Me": color = (0, 255, 0) # Green
            elif b["sender"] == "System": color = (255, 255, 0) # Cyan
            else: color = (0, 165, 255) # Orange

            cv2.rectangle(debug_img, (x1, y1), (x2, y2), color, 2)

            final_history.append({
                "sender": b["sender"],
                "content": content,
                "box": b["box"],
                "category": b["category"],
                "type": "text"
            })

        # Save result
        cv2.imwrite("debug_edges_final_v4.jpg", debug_img)
        return final_history
    
    def read_bubble_with_paddleocr(self, bubble_image):
        model_id = "C:\platform-tools\instabotfinal\models\paddle"
        dtype = torch.bfloat16 # Blackwell's native language

        model = AutoModelForCausalLM.from_pretrained(
            model_id, 
            trust_remote_code=True, 
            torch_dtype=dtype,
            local_files_only=True
        ).to("cuda").eval()
    
        processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True, use_fast=True)

        # 1. Prepare Image
        # 1. Convert NumPy array (OpenCV) to PIL Image
            # Note: OpenCV uses BGR, PIL uses RGB. 
            # If your crop is already RGB, remove the .split()/.merge() part.
        if isinstance(bubble_image, np.ndarray):
            # Convert BGR (OpenCV) to RGB (PIL)
            image = Image.fromarray(cv2.cvtColor(bubble_image, cv2.COLOR_BGR2RGB))
        else:
            # If it's already a PIL image, just use it
            image = bubble_image.convert("RGB")

        # 2. Correct Prompt with Placeholder
        # The <image> tag tells the model WHERE the visual features belong
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": "OCR:"}, # Chat template adds the tag automatically
                ],
            }
        ]
        
        # Let the chat template handle the formatting
        text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = processor(text=[text], images=[image], return_tensors="pt").to("cuda")

        with torch.no_grad():
            _ = model.generate(**inputs, max_new_tokens=1, do_sample=False)

        # 4. THE REAL RUN

        start = time.time()
        with torch.no_grad():
            out = model.generate(
                **inputs, 
                max_new_tokens=256, 
                do_sample=False,
                num_beams=1
            )
        
        # Decode only the Assistant's response
        input_len = inputs.input_ids.shape[-1]
        result = processor.decode(out[0][input_len:], skip_special_tokens=True)
        
        return result.strip()



        
    def read_bubble(self, screen, params=None):
        is_system = params
        #return self.read_bubble_with_qwen(screen, is_system)
        return self.read_bubble_with_paddleocr(screen)
        

def do_one():
    path = "C:/platform-tools/instabotfinal/instabot/all_screenshots/Screenshots/Screenshot_20260118-124400.png"  #david baron?
    #path = "C:/platform-tools/instabotfinal/instabot/all_screenshots/Screenshots/Screenshot_20260118-111247.png"
    path = "C:/platform-tools/instabotfinal/instabot/all_screenshots/Screenshots/Screenshot_20260113-145041.png"

    path = "C:/platform-tools/instabotfinal/instabot/all_screenshots/Screenshots/Screenshot_20260118-155148.png"   #jasmine fight with aime
    # Initialize logic
    parser = ScreenParser()

    img = cv2.imread(path)
    
    # Run on your screenshot
    history = parser.parse_chat_screen(path)
    
    # 3. Output the JSON
    print("\n--- FINAL JSON ---")
    print(json.dumps(history, indent=4))

    # DRAW DEBUG BOXES
    debug_img = cv2.imread(path)
    i = 1
    for item in history:
        x, y, w, h = item["box"]
        # Draw Rectangle (Green)
        cv2.rectangle(debug_img, (x, y), (x+w, y+h), (0, 255, 0), 2)
        # Put Label (Red)
        cv2.putText(debug_img, item["sender"], (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        bubble = parser.crop_box_from_image(img, item["box"])
        cv2.imwrite(f"bubble_{i}.png", bubble)
        is_system = item["sender"] == "System" 
        #print(f"bubble content {i} - {item["sender"]}: {parser.read_bubble_with_qwen(bubble, is_system)} ")
        #print(f"bubble content {i} - {item['sender']}: {parser.read_bubble_with_paddleocr(bubble)} ")
        i+=1

    
    cv2.imwrite("debug_output.png", debug_img)
    print("📸 Saved debug_output.png with boxes drawn!")

def do_directory():
    # 1. SETUP PATHS
    input_dir = "C:/platform-tools/instabotfinal/instabot/utils/test"
    output_dir = os.path.join(input_dir, "debug_results")
    
    # Create output folder if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    print(f"📂 Scanning directory: {input_dir}")
    print(f"📂 Saving results to: {output_dir}\n")

    # IMPORTANT: Use the latest 'EdgeBubbleParser' class
    parser = ScreenParser() 

    # 3. GET ALL PNG FILES
    image_files = glob.glob(os.path.join(input_dir, "*.png"))

    if not image_files:
        print("❌ No .png files found in directory!")

    # 4. PROCESS LOOP
    for img_path in image_files:
        filename = os.path.basename(img_path)
        print(f"--------------------------------------------------")
        print(f"🖼️ Processing: {filename}")

        try:
            # A. PARSE
            history = parser.parse_chat_screen(img_path)

            # B. PRINT JSON (Shortened for readability)
            print(f"   ✅ Found {len(history)} messages.")
            # print(json.dumps(history, indent=4)) # Uncomment to see full JSON per file

            # C. DRAW DEBUG BOXES
            debug_img = cv2.imread(img_path)
            
            for item in history:
                x, y, w, h = item["box"]
                
                # Color Code: Green = Me, Orange = Them, Blue = System
                if item["sender"] == "Me": color = (0, 255, 0)
                elif item["sender"] == "jazzysexyjasmine": color = (0, 165, 255)
                else: color = (255, 255, 0)

                # Draw Box
                cv2.rectangle(debug_img, (x, y), (x+w, y+h), color, 2)
                
                # Draw Label (Sender Name)
                cv2.putText(debug_img, item["sender"], (x, y-5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            # D. SAVE DEBUG IMAGE
            save_path = os.path.join(output_dir, f"debug_{filename}")
            cv2.imwrite(save_path, debug_img)
            print(f"   📸 Saved debug image to: {save_path}")

        except Exception as e:
            print(f"   ❌ Failed to process {filename}: {e}")

    print("\n🎉 Batch processing complete!")
    

if __name__ == "__main__":
    #do_directory()
    do_one()

