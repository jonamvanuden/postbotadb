from new_utils import Locator

class OpenInstagramCommand:
    def __init__(self):
        pass
    def execute(self, ctx):
        ctx.human.wake_and_unlock_and_open_insta("0000")


class CloseInstagramCommand:
    def __init__(self):
        pass
    
    def execute(self, ctx):
        # 2. PERFORM THE FLICK
        ctx.human.close_instagram_natural()
        ctx.human.lock_phone()