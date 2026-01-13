from new_utils import Locator

class SwipeDownCommand:
    def __init__(self, type="top"):
        print(f"miniswipe command")
        self.type = type

    def execute(self, ctx):
        print(f"executing swipdowncommand with type {self.type}")
        if self.type == "mini":
            ctx.human.mini_swipe_down()
        else:
            ctx.swipe_top_down_percentage(14)

class SwipeDrownFromBoxCommand:
    def __init__(self):
        """
        Docstring for __init__
        
        :param self: Description
        """
        
    def execute(self, ctx):
        ctx.snap()
        start_x, start_y, width, height = Locator.find_comment_header(ctx.screen)
        ctx.human.swipe_down_from_box(start_x, start_y, width, height)



        
            