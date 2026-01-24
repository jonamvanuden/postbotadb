from new_utils import Locator
import time
import random

class ClickButtonCommand:
    def __init__(self, btn_type, username=None):
        self.username = username
        self.btn_type = btn_type
    
    def execute(self, ctx):
        ctx.snap()


        try:

            match self.btn_type:
                case "main_inbox": box = Locator.find_inbox_btn(ctx.screen)
                case "main_reel": box = Locator.find_reel_btn(ctx.screen)
                case "main_profile": box = Locator.find_profile_btn(ctx.screen, "thelifeofaime")
                case "main_home" : box = Locator.find_home_btn(ctx.screen)
                case "home_comment" : box = Locator.find_comment_btn_on_homefeed(ctx.screen)
                case "back" : box = Locator.find_btn_back(ctx.screen)
                case _: raise ValueError(f"Unknown button: {self.btn_type}")           


            if box:
                ctx.human.tap_within_box(box)
                return True
        except: 
            print("ClickInboxCommand failed")
            raise
        return False
