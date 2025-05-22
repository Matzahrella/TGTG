import subprocess
import time
import random

# Initialize counters and logs
request_count = 0
start_time = time.perf_counter()  # Use perf_counter for high-precision timing

# List of scripts to execute in sequence
scripts = [
    "show_favorites.py",
    "createpizza.py",
    "show_favorites.py",
    "abortpizza.py"
]

# Infinite loop to execute scripts in sequence
try:
    while True:
        for script in scripts:
            print(f"🚀 Executing {script}...")
            try:
                # Run the script and capture the output
                result = subprocess.run(
                    ["python3", script],
                    text=True,
                    capture_output=True,
                    check=True
                )
                request_count += 1  # Increment the request counter
                elapsed_time = time.perf_counter() - start_time  # Calculate elapsed time
                print(f"✅ Successfully executed {script}. Request #{request_count}")
                print(f"⏱️ Elapsed time since start: {elapsed_time:.9f} seconds")  # High precision for elapsed time
                print(result.stdout)

                # Check if the response contains a CAPTCHA
                if "captcha" in result.stdout.lower():
                    print("❌ CAPTCHA detected! Stopping the script.")
                    print(f"📊 Total normal responses before CAPTCHA: {request_count - 1}")
                    print(f"⏱️ Total elapsed time: {elapsed_time:.9f} seconds")
                    exit(0)
            except subprocess.CalledProcessError as e:
                print(f"❌ Error while executing {script}: {e}")
                print(e.stdout)
                print(e.stderr)
                exit(1)

            # Wait for a random interval between 35 and 60 seconds with jitter
            base_interval = random.uniform(35, 60)  # Generate a random base interval
            jitter = random.uniform(-5, 5)  # Add or subtract up to 5 seconds
            interval = max(1, base_interval + jitter)  # Ensure the interval is at least 1 second
            print(f"⏳ Waiting for {interval:.9f} seconds before the next request...")  # Print with 9 decimal places
            time.sleep(interval)
except KeyboardInterrupt:
    print("\n🛑 Script stopped by user.")
    elapsed_time = time.perf_counter() - start_time
    print(f"📊 Total requests made: {request_count}")
    print(f"⏱️ Total elapsed time: {elapsed_time:.9f} seconds")