from new_utils import Locator, OCR
import time
import random
import requests
import json

class SendMessageCommand:
    def __init__(self, onlyreply = False):
        self.API_BASE = "http://127.0.0.1:5000"
        self.onlyreply = onlyreply
    
    def execute(self, ctx):
        ctx.snap()
        chat_json = OCR.extract_chat_from_screen(ctx.screen)
        print(json.dumps(chat_json, indent=4, sort_keys=True, ensure_ascii=False))


        
        # B. Get the VERY LAST message
        last_message = chat_json[-1]
        sender = last_message.get('sender', 'Unknown')
        content = last_message.get('content', '')

        print(f"🔎 Last message was from: {sender}")

        if (self.onlyreply and sender=="Me"):
            print("dont reply because only reply is true and last sender was me.")
            return False

        # --- SMART USERNAME DETECTION ---
        # We need to know WHO we are talking to. 
        # If 'Me' spoke last, we look back to find the other person's name.
        target_user = "Stranger"
        
        # 1. First, try to find a name that isn't "Me" in the history
        for msg in reversed(chat_json):
            if msg.get('sender') and msg.get('sender') != "Me":
                target_user = msg.get('sender')
                break

        endpoint = f"{self.API_BASE}/chat"
        payload = {"user": target_user, "message": content, "history" : chat_json }

        

        # D. Execute the Web Call
        try:
            response = requests.post(endpoint, json=payload)
            
            if response.status_code == 200:
                reply_text = response.json()['response']
                print(f"✅ Success! API Response: {reply_text}")

                img_file = Locator.get_btn_filename("btn-message-icons.png", "inbox")
                box = Locator.find_btn(img_file, ctx.screen, 0.95)
                print(f"check here is are the icons box: {box}")
                ctx.human.tap_left_of(box)
                ctx.human.sleep()
                           
                # 1. Type the text
                ctx.human.type_quick(reply_text)
                
                # 2. Look for Send Button
                ctx.snap()
                box = Locator.find_btn_send(ctx.screen)
                
                if box:
                    print(f"🚀 Tapping Send at {box}")
                    ctx.human.tap_within_box(box)
                else:
                    # Fallback: Sometimes 'Enter' works if button isn't seen
                    print("⚠️ Can't find Send button. Trying Enter key...")
                    ctx.human._adb_command("shell input keyevent 66")
                    
            else:
                print(f"❌ API Error {response.status_code}: {response.text}")

        except Exception as e:
            print(f"❌ Connection Failed: {e}")
            raise
