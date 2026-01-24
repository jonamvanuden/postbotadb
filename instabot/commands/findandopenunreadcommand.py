from new_utils import Locator, OCR
import time
import random
import requests
import json

class FindAndOpenUnreadCommand:
    def __init__(self):
        self.API_BASE = "http://127.0.0.1:5000"
    
    def execute(self, ctx):
        ctx.snap()
        img_file = Locator.get_btn_filename("btn-unread.png", "inbox")
        print(f"filename: {img_file}")
        list_convo_btns = Locator.find_unread_conversations( img_file, ctx.screen, 0.95)

        if len(list_convo_btns)>0:
            # Unpack the anchor coordinates (x, y, width, height)
            anchor_x, anchor_y, anchor_w, anchor_h = list_convo_btns[0]
            ctx.human.tap_left_of([anchor_x, anchor_y, anchor_w, anchor_h])               

            return True
        else:
            print("no body is talking")
            return False
            