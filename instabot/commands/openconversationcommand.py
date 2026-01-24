from new_utils import Locator, OCR
import time
import random
import requests
import json
from utils import ScreenParser

class OpenConversationCommand:
    def __init__(self, selector):
        self.selector = selector
        self.API_BASE = "http://127.0.0.1:5000"
    
    def execute(self, ctx):
        ctx.snap()
        img_file = Locator.get_btn_filename("btn-inbox-camera.png", "inbox")
        list_convo_btns = Locator.find_all_btns( img_file, ctx.screen)

        if self.selector < len(list_convo_btns):
            # Unpack the anchor coordinates (x, y, width, height)
            anchor_x, anchor_y, anchor_w, anchor_h = list_convo_btns[self.selector]

            ctx.human.tap_left_of([anchor_x, anchor_y, anchor_w, anchor_h])
            ctx.snap()
            #chat_json = OCR.extract_chat_from_screen(ctx.screen)
            chat_json = ScreenParser().parse_chat_screen(ctx.screen)
            print(json.dumps(chat_json, indent=4, sort_keys=True, ensure_ascii=False))

            self.decide_and_call(chat_json, ctx)
            
        else:
            print(f"❌ Error: Conversation index {self.selector} not found on screen.")
    
    def decide_and_call(self, conversation_log, ctx):
        # A. Safety check for empty list
        if not conversation_log:
            print("❌ Error: History is empty.")
            return

        # ==========================================
        # 🛑 STALKER CHECK (New Rule)
        # ==========================================
        filtered_log = [msg for msg in conversation_log if msg["sender"] != 'System']
        if len(filtered_log) >= 2:
            last_sender = filtered_log[-1].get('sender')
            second_last_sender = filtered_log[-2].get('sender')
            
            if last_sender == "Me" and second_last_sender == "Me":
                print("🛑 dont stalk (Last 2 messages were yours. Waiting for reply.)")
                return

        # B. Get the VERY LAST message
        last_message = filtered_log[-1]
        sender = last_message.get('sender', 'Unknown')
        content = last_message.get('content', '')

        print(f"🔎 Last message was from: {sender}")

        # --- SMART USERNAME DETECTION ---
        # We need to know WHO we are talking to. 
        # If 'Me' spoke last, we look back to find the other person's name.
        target_user = "Stranger"
        
        # 1. First, try to find a name that isn't "Me" in the history
        for msg in reversed(filtered_log):
            if msg.get('sender') and msg.get('sender') != "Me":
                target_user = msg.get('sender')
                break
        
        # C. The Decision Logic
        if sender == "Me":
            print(f"👉 Sender is 'Me'. Re-engaging {target_user} via /initiate...")
            endpoint = f"{self.API_BASE}/initiate"
            payload = {"user": target_user} 
        else:
            print(f"👉 Sender is '{target_user}'. Replying via /chat...")
            endpoint = f"{self.API_BASE}/chat"
            payload = {"user": target_user, "message": content, "history" : filtered_log}

        # D. Execute the Web Call
        try:
            response = requests.post(endpoint, json=payload)
            
            if response.status_code == 200:
                reply_text = response.json()['response']
                print(f"✅ Success! API Response: {reply_text}")

                img_file = Locator.get_btn_filename("btn-message-icons.png", "inbox")
                box = Locator.find_btn(img_file, ctx.screen, 0.95)
                print(f"FOUND BOX AT: {box}")

                ctx.human.tap_left_of(box)
                ctx.human.sleep()
                
                # 1. Type the text
                ctx.human.type_text(reply_text)
                
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
