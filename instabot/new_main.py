from new_context import Context
from commands import *
from new_system import *
import os, cv2
from new_utils import *
import json

def instagram_test():
    bot = Context()

    my_actions = [
        #ClickButtonCommand("main_inbox"),
        #ClickButtonCommand("main_reel"),
        #ClickButtonCommand("main_profile"),        
        ClickButtonCommand("main_home"),
        SnapToTopCommand2(),
        ClickButtonCommand("home_comment"),
        SwipeDownCommand("mini"),
        SwipeDrownFromBoxCommand()

    ]

    # Add 10 SnapToTopCommands to the sequence
    for _ in range(20):
        my_actions.append(SnapToTopCommand2())


    i = 0
    for command in my_actions: 
        command_type = type(command)   
        try:    
            
            print(f"======== {i} ==========")
            i+=1       
            success = command.execute(bot)         
            print(f"{command_type} succesfully executed")

        except Exception as e:
            print(f"{command_type} stopped due exception e")
                
    print("✅ Sequence Finished!")

def get_screenshots():
    pull_all_existing_screenshots()

def test_chat():

    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 2. This gets the PARENT: C:\platform-tools\instabotfinal
    parent_dir = os.path.dirname(current_dir)
    
    full_path = os.path.join(parent_dir, "instabot", "all_screenshots", "Screenshots", "Screenshot_20260113-145041.png")
    full_path =  os.path.normpath(full_path)

    screen = cv2.imread(full_path)
    
    json1 = OCR.extract_chat_from_screen(screen)

    print(json.dumps(json1, indent=4, ensure_ascii=False))

def test_ocr_from_filepath():
    current_dir = os.path.dirname(os.path.abspath(__file__))        
    # 2. This gets the PARENT: C:\platform-tools\instabotfinal
    parent_dir = os.path.dirname(current_dir)        
    full_path = os.path.join(parent_dir, "instabot", "all_screenshots", "Screenshots", "screen.png")
    full_path =  os.path.normpath(full_path)
    screen = cv2.imread(full_path)
    
    json1 = OCR.extract_comments_by_filepath(full_path)

    print(json.dumps(json1, indent=4, ensure_ascii=False))

def test_ocr_from_screen():
    current_dir = os.path.dirname(os.path.abspath(__file__))      
    parent_dir = os.path.dirname(current_dir)        
    full_path = os.path.join(parent_dir, "instabot", "all_screenshots", "Screenshots", "screen.png")
    full_path =  os.path.normpath(full_path)
    screen = cv2.imread(full_path)

    json1 = OCR.extract_comments_from_screen(screen)
    print(json.dumps(json1, indent=4, ensure_ascii=False))



if __name__ == "__main__":
    #instagram_test()
    #clean_screenshots()
    
    #get_screenshots()
    #test_ocr_from_filepath()
    #test_ocr_from_screen()
    #test_chat()
    
