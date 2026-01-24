from new_utils import Locator

class ScrollCommand:
    def __init__(self, direction="down"):
        self.direction = direction

    def execute(self, ctx):
        ctx.human.human_scroll_inbox(self.direction)

class ScrollToBottomCommand:
    def __init__(self):
        pass
    
    def execute(self, ctx):
        ctx.human.scroll_to_bottom()


        
