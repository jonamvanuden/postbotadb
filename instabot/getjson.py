from new_context import Context
from commands import *
from new_system import *
import os, cv2
from new_utils import *
import json


if __name__ == "__main__":
    bot = Context()
    bot.snap()
    jsonf =  OCR.extract_chat_from_screen(bot.screen)

    print(json.dumps(jsonf, indent=4, sort_keys=True, ensure_ascii=False))

