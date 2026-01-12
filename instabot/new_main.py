from new_context import Context
from new_commands import *
from new_system import *

def instagram_test():
    bot = Context()

    my_actions = [
        #ClickButtonCommand("main_inbox"),
        #ClickButtonCommand("main_reel"),
        ClickButtonCommand("main_profile"),        
        ClickButtonCommand("main_home")
    ]

    # Add 10 SnapToTopCommands to the sequence
    for _ in range(20):
        my_actions.append(SnapToTopCommand())


    i = 0
    for command in my_actions:
        success = command.execute(bot)

        print (f"======== {i} ==========")
        i+=1

        if not success:
            print("actions stopped due to failure")
            break
    
    print("✅ Sequence Finished!")

def get_screenshots():
    pull_all_existing_screenshots()

if __name__ == "__main__":
    instagram_test()
    #clean_screenshots()
    #get_screenshots()
