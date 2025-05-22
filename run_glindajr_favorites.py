import subprocess
import time
import random

# Initialize counters and start time
request_count = 0
start_time = time.time()

# Infinite loop to run glindajr_favorites.py
try:
    alternate = True  # Start with the shorter interval (10–30 seconds)
    while True:
        print("🚀 Executing glindajr_favorites.py...")
        try:
            # Run glindajr_favorites.py and capture the output
            result = subprocess.run(
                ["python3", "glindajr_favorites.py"],
                text=True,
                capture_output=True,
                check=True
            )
            request_count += 1  # Increment the request counter
            elapsed_time = time.time() - start_time  # Calculate elapsed time
            print(f"✅ Successfully executed glindajr_favorites.py. Request #{request_count}")
            print(f"⏱️ Total elapsed time: {elapsed_time:.2f} seconds")
            print(result.stdout)

            # Check if the response contains a CAPTCHA
            if "captcha" in result.stdout.lower():
                print("❌ CAPTCHA detected! Aborting the script.")
                print(f"📊 Total requests made: {request_count}")
                print(f"⏱️ Total elapsed time: {elapsed_time:.2f} seconds")
                break
        except subprocess.CalledProcessError as e:
            print(f"❌ Error while executing glindajr_favorites.py: {e}")
            print(e.stdout)
            print(e.stderr)
            break

        # Alternate between short and long intervals
        if alternate:
            # Short interval: 10–30 seconds
            base_interval = random.uniform(10, 30)
        else:
            # Long interval: 60–90 seconds
            base_interval = random.uniform(60, 90)

        # Add jitter to the interval
        jitter = random.uniform(-1, 1)  # Add or subtract up to 1 second
        interval = max(1, base_interval + jitter)  # Ensure the interval is at least 1 second

        # Log the interval and wait
        print(f"⏳ Waiting for {interval:.3f} seconds before the next request...")  # Print with millisecond precision
        time.sleep(interval)

        # Toggle the alternate flag
        alternate = not alternate
except KeyboardInterrupt:
    elapsed_time = time.time() - start_time
    print("\n🛑 Script stopped by user.")
    print(f"📊 Total requests made: {request_count}")
    print(f"⏱️ Total elapsed time: {elapsed_time:.2f} seconds")