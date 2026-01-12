import os
import subprocess

def pull_all_existing_screenshots(local_folder="./all_screenshots"):
    if not os.path.exists(local_folder):
        os.makedirs(local_folder)

    # Standard Android screenshot directory
    remote_folder = "/sdcard/Pictures/Screenshots/"

    print(f"📂 Attempting to pull all files from {remote_folder}...")
    
    try:
        # Pulls the entire directory to your local folder
        # The trailing slash on the remote folder and the local path handles the transfer
        subprocess.run(["adb", "pull", remote_folder, local_folder], check=True)
        print(f"✅ Success! Check the '{local_folder}' directory.")
    except subprocess.CalledProcessError:
        print("❌ Error: Could not pull screenshots. Ensure the path exists on your device.")

def clean_screenshots():
    """Deletes all PNG and JPG screenshots from the phone."""
    print("🧹 Cleaning up old screenshots on device...")
    
    # List of common screenshot folders on Android
    # We use quotes around the path in the command to be safe
    targets = [
        "/sdcard/Pictures/Screenshots/*.png",
        "/sdcard/DCIM/Screenshots/*.png",
        "/sdcard/Pictures/Screenshots/*.jpg", 
        "/sdcard/DCIM/Screenshots/*.jpg"
    ]

    for target in targets:
        # We construct the ADB command. 
        # We use check=False so the script doesn't crash if a folder is already empty.
        cmd = ["adb", "shell", f"rm {target}"]
        
        try:
            subprocess.run(cmd, check=False)
            print(f"   Checked/Cleaned: {target}")
        except Exception as e:
            print(f"   ⚠️ Could not access {target}: {e}")

