import os
os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "1"

from commands import SwipeDownCommand
from new_context import Context

bot = Context()
cmd = SwipeDownCommand()
cmd.execute(bot)
