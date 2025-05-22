import subprocess
import time

# Time interval between executions (4 minutes and 30 seconds)
interval = 270  # 270 seconds

# Infinite loop to repeatedly execute fluffycreatepizza2.py
try:
    while True:
        print("🚀 Executing fluffycreatepizza2.py...")
        try:
            # Run the fluffycreatepizza2.py script
            subprocess.run(["python3", "fluffycreatepizza2.py"], check=True)
            print("✅ Successfully executed fluffycreatepizza2.py.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error while executing fluffycreatepizza2.py: {e}")
        
        # Wait for the specified interval
        print(f"⏳ Waiting for {interval} seconds before the next execution...")
        time.sleep(interval)
except KeyboardInterrupt:
    print("\n🛑 Script stopped by user.")