import os
import datetime
import subprocess
import cv2
import numpy as np

from humanizehelper import *


def wake_and_unlock(pin):
    write("Waking up device...")
    # 26 is the keycode for Power. This toggles the screen.
    adb_command("shell input keyevent 224")
    time.sleep(1)

    write("Swiping up to show PIN entry...")
    # Swipes from bottom-middle to top-middle
    adb_command("shell input swipe 500 1500 500 500 200")
    time.sleep(1)

    write(f"Entering PIN...")
    # Sends the text of your pin and presses Enter (keycode 66)
    adb_command(f"shell input text {pin}")
    adb_command("shell input keyevent 66")
    time.sleep(2)

def open_instagram():
    write("Opening Instagram...")
    # This command searches for the launcher automatically
    adb_command("shell monkey -p com.instagram.android -c android.intent.category.LAUNCHER 1")

def open_calculator():
    write("Opening Calculator...")
    # Using the monkey command to launch
    adb_command(f"shell monkey -p {myconfig.CALC_PACKAGE} 1")
    
    # Wait for the app to actually render on screen
    human_delay(2.0, 3.0)

