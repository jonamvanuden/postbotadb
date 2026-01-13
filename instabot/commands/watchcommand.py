import time
import random

class WatchPostCommand:
    def execute(self, ctx):
        watch_time = random.uniform(2.0, 8.0)
        print(f"👀 Watching for {watch_time:.1f}s...")
        time.sleep(watch_time)
        return True