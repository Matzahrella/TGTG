import subprocess
import time

# Initialize counters and start time
request_count = 0
start_time = time.time()

# Infinite loop to run glinda_favorites.py every 61 seconds
try:
    while True:
        print("🚀 Executing glinda_favorites.py...")
        try:
            # Run glinda_favorites.py and capture the output
            result = subprocess.run(
                ["python3", "glinda_favorites.py"],
                text=True,
                capture_output=True,
                check=True
            )
            request_count += 1  # Increment the request counter
            elapsed_time = time.time() - start_time  # Calculate elapsed time
            print(f"✅ Successfully executed glinda_favorites.py. Request #{request_count}")
            print(f"⏱️ Total elapsed time: {elapsed_time:.2f} seconds")
            print(result.stdout)

            # Check if the response contains a CAPTCHA
            if "captcha" in result.stdout.lower():
                print("❌ CAPTCHA detected! Aborting the script.")
                print(f"📊 Total requests made: {request_count}")
                print(f"⏱️ Total elapsed time: {elapsed_time:.2f} seconds")
                break
        except subprocess.CalledProcessError as e:
            print(f"❌ Error while executing glinda_favorites.py: {e}")
            print(e.stdout)
            print(e.stderr)
            break

        # Wait for exactly 50 seconds before the next request
        print("⏳ Waiting for 50 seconds before the next request...")
        time.sleep(50)
except KeyboardInterrupt:
    elapsed_time = time.time() - start_time
    print("\n🛑 Script stopped by user.")
    print(f"📊 Total requests made: {request_count}")
    print(f"⏱️ Total elapsed time: {elapsed_time:.2f} seconds")