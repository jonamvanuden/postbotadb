from new_context import Context
from commands import *
from new_system import *
import os, cv2
from new_utils import *
import json 
import time
import random

def do_work():
    bot = Context()

    OpenInstagramCommand().execute(bot)
    stalkmtf = [
        ClickButtonCommand("back"),
        ClickButtonCommand("back"),
        ClickButtonCommand("back"),
        ClickButtonCommand("main_profile"),
        ClickButtonCommand("main_inbox"),
        ScrollCommand(direction="down"),
        ScrollCommand(direction="down"),
        ScrollCommand(direction="down"),
        ScrollCommand(direction="down"),
        OpenConversationCommand(0),
        ClickButtonCommand("back"),
        OpenConversationCommand(1),
        ClickButtonCommand("back"),
        OpenConversationCommand(2),
        ClickButtonCommand("back"),
        OpenConversationCommand(3),
        ClickButtonCommand("back"),
        OpenConversationCommand(4),
        ClickButtonCommand("back"),
        ScrollCommand(direction="down"),
        ScrollCommand(direction="down"),
        ScrollCommand(direction="down"),
        ScrollCommand(direction="down"),
        ScrollCommand(direction="down"),
        ScrollCommand(direction="down"),
        OpenConversationCommand(0),
        ClickButtonCommand("back"),
        OpenConversationCommand(1),
        ClickButtonCommand("back"),
        OpenConversationCommand(2),
        ClickButtonCommand("back"),
        OpenConversationCommand(3),
        ClickButtonCommand("back"),
        OpenConversationCommand(4),
        ClickButtonCommand("back"),
        OpenConversationCommand(5),
        ClickButtonCommand("back"),
        OpenConversationCommand(6),
        ClickButtonCommand("back")
    ]

    #for item in stalkmtf:
        #item.execute(bot)

    # done stalking.. now waiting a bit..d

    for i in range(10):
        ClickButtonCommand("main_inbox").execute(bot)
        FindAndOpenUnreadCommand().execute(bot)
        for x in range(20):
            SendMessageCommand(onlyreply=True).execute(bot)
            bot.human.sleep(5,10)
    
    CloseInstagramCommand().execute(bot)

def main_loop():
    print("=== STARTING INFINITE LOOP ===")
    
    while True:
        try:
            # 1. DO THE WORK
            do_work() # <--- Your bot logic here
            print("🤖 Bot finished a session.")

            # 2. CALCULATE RANDOM PAUSE (1 to 4 Hours)
            # Random number of seconds between 3600 (1hr) and 14400 (4hrs)
            sleep_seconds = random.randint(180, 1200)
            
            # Calculate Minutes and remaining Seconds
            minutes, seconds = divmod(sleep_seconds, 60)
            
            print(f"✅ Pausing for {minutes}m {seconds}s...")
            
            # 3. SLEEP
            time.sleep(sleep_seconds)
            
            print("⏰ Waking up! Starting next cycle...\n")

        except KeyboardInterrupt:
            print("\n🛑 Loop stopped by user.")
            break
        except Exception as e:
            print(f"⚠️ Error occurred: {e}")
            time.sleep(60) # Wait 1 min on error before retrying

if __name__ == "__main__":
    main_loop()