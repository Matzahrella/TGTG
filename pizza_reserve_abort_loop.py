import subprocess
import time
import os
from threading import Thread

# Function to delete last_order_id.json after 5 minutes
def delete_last_order_id_after_delay(file_path, delay):
    def delete_file():
        time.sleep(delay)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑️ File {file_path} deleted after {delay} seconds.")
    # Run the deletion in a separate thread
    Thread(target=delete_file).start()

# Function to execute fluffyabortpizza.py after 30 seconds, regardless of the state of fluffycreatepizza2.py
def start_abort_after_delay(delay):
    def run_abort():
        time.sleep(delay)
        print("🚀 Executing fluffyabortpizza.py...")
        try:
            subprocess.run(["python3", "fluffyabortpizza.py"], check=True)
            print("✅ Successfully executed fluffyabortpizza.py.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error while executing fluffyabortpizza.py: {e}")
    # Run the abort process in a separate thread
    Thread(target=run_abort).start()

# Infinite loop to execute fluffycreatepizza2.py and fluffyabortpizza.py
try:
    while True:
        # Step 1: Execute fluffycreatepizza2.py
        print("🚀 Executing fluffycreatepizza2.py...")
        try:
            # Start fluffyabortpizza.py after 30 seconds in a separate thread
            start_abort_after_delay(30)

            # Run fluffycreatepizza2.py
            subprocess.run(["python3", "fluffycreatepizza2.py"], check=True)
            print("✅ Successfully executed fluffycreatepizza2.py.")
            # Schedule deletion of last_order_id.json after 5 minutes
            delete_last_order_id_after_delay("last_order_id.json", 300)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error while executing fluffycreatepizza2.py: {e}")

        # Step 2: Wait 10 seconds before starting the next iteration
        print("⏳ Waiting for 10 seconds before repeating the process...")
        time.sleep(10)
except KeyboardInterrupt:
    print("\n🛑 Script stopped by user.")