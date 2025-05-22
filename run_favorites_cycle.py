import subprocess
import time

# List of favorite scripts for each account
favorite_scripts = [
    "glindajr_favorites.py",  # Account 1
    "fluffyfavorites.py",     # Account 2
    "show_favorites.py",      # Account 3
    "show_favoritesjr.py",    # Account 4
    "gideon2favorites.py",    # Account 5
    "gideonfavorites.py"      # Account 6
]

# Function to execute a favorites script
def execute_favorites(script):
    print(f"🚀 Executing {script}...")
    try:
        result = subprocess.run(
            ["python3", script],
            text=True,
            capture_output=True,
            check=True
        )
        print(f"✅ Successfully executed {script}")
        print(result.stdout)

        # Check if the response contains a CAPTCHA
        if "captcha" in result.stdout.lower():
            print(f"❌ CAPTCHA detected in {script}. Aborting further requests.")
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Error while executing {script}: {e}")
        print(e.stdout)
        print(e.stderr)
    return True

# Main function to run the favorites cycle
def main():
    print("⏰ Starting favorites cycle...")
    while True:
        cycle_start_time = time.time()  # Record the start time of the cycle

        for i, script in enumerate(favorite_scripts):
            success = execute_favorites(script)
            if not success:
                print("❌ Aborting further requests due to CAPTCHA.")
                return  # Stop the script if a CAPTCHA is detected

            # Wait 10 seconds before the next account's request
            if i < len(favorite_scripts) - 1:  # No need to wait after the last script
                print("⏳ Waiting for 10 seconds before the next account...")
                time.sleep(10)

        # Wait until 61 seconds have passed since the start of the cycle
        cycle_elapsed_time = time.time() - cycle_start_time
        remaining_time = max(0, 61 - cycle_elapsed_time)  # Ensure no negative wait time
        print(f"⏳ Waiting for {remaining_time:.2f} seconds before the next cycle...")
        time.sleep(remaining_time)

if __name__ == "__main__":
    main()