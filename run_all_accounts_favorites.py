import subprocess
import time

# List of favorite scripts for each account
favorite_scripts = [
    "glindajr_favorites.py",
    "fluffyfavorites.py",
    "show_favorites.py",
    "show_favoritesjr.py",
    "gideon2favorites.py",
    "gideonfavorites.py"
]

# Initialize counters and logs
request_count = 0
script_usage = {script: 0 for script in favorite_scripts}  # Track how many times each script is used
start_time = time.time()

# Infinite loop to run favorites requests for all accounts
try:
    while True:
        cycle_start_time = time.time()  # Record the start time of the cycle

        for script in favorite_scripts:
            print(f"🚀 Executing {script}...")
            try:
                # Run the script and capture the output
                result = subprocess.run(
                    ["python3", script],
                    text=True,
                    capture_output=True,
                    check=True
                )
                request_count += 1  # Increment the total request counter
                script_usage[script] += 1  # Increment the usage counter for this script
                elapsed_time = time.time() - start_time  # Calculate total elapsed time
                print(f"✅ Successfully executed {script}. Request #{request_count}")
                print(f"⏱️ Total elapsed time: {elapsed_time:.2f} seconds")
                print(result.stdout)

                # Check if the response contains a CAPTCHA
                if "captcha" in result.stdout.lower():
                    print(f"❌ CAPTCHA detected in {script}. Aborting the script.")
                    print(f"📊 Total requests made: {request_count}")
                    print(f"📊 Script usage: {script_usage}")
                    print(f"⏱️ Total elapsed time: {elapsed_time:.2f} seconds")
                    exit(0)
            except subprocess.CalledProcessError as e:
                print(f"❌ Error while executing {script}: {e}")
                print(e.stdout)
                print(e.stderr)

            # Wait 0.5 seconds before the next account's request
            print("⏳ Waiting for 0.5 seconds before the next account...")
            time.sleep(0.5)

        # Wait until 1 minute has passed since the start of the cycle
        cycle_elapsed_time = time.time() - cycle_start_time
        remaining_time = max(0, 60 - cycle_elapsed_time)  # Ensure no negative wait time
        print(f"⏳ Waiting for {remaining_time:.2f} seconds before the next cycle...")
        time.sleep(remaining_time)
except KeyboardInterrupt:
    elapsed_time = time.time() - start_time
    print("\n🛑 Script stopped by user.")
    print(f"📊 Total requests made: {request_count}")
    print(f"📊 Script usage: {script_usage}")
    print(f"⏱️ Total elapsed time: {elapsed_time:.2f} seconds")