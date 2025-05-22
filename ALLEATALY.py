import subprocess
import time

# List of reservation scripts for each account
reservation_scripts = [
    "reserve_eataly_bag.py",          # Account 1
    "createeatalyscriptjr.py",        # Account 2
    "fuzzycreateeataly.py",           # Account 3
    "reserve_eataly_bag_glindajr.py", # Account 4
    "reserve_eataly_bag_glinda.py",   # Account 5
    "CreateEatalyGideon.py",          # Account 6
    "createeataly_joshua.py"          # Account 7 (Joshua)
]

# Function to execute a reservation script
def execute_reservation(script):
    print(f"🔄 Running {script}...")
    try:
        result = subprocess.run(
            ["python3", script],
            text=True,
            capture_output=True,
            check=True,
            timeout=10  # Timeout after 10 seconds
        )

        # Check if the script successfully reserved a bag
        if "Successfully reserved the bag!" in result.stdout:
            print(f"🎉 Bag reserved by {script}!")
            # Extract and print reservation details
            print("Reservation details:")
            print(result.stdout)
        else:
            print(f"✅ Script {script} executed successfully (no reservation).")

    except subprocess.TimeoutExpired:
        print(f"⏰ Timeout expired for {script}. Moving to the next script.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error while executing {script}: {e}")
    return True

# Main function to send requests
def main():
    print("⏰ Waiting for the Eataly bag to go online...")
    while True:
        current_time = time.strftime("%H:%M:%S.%f")[:-3]  # Include milliseconds
        if current_time >= "04:17:09.000":  # Adjusted start time
            print(f"🕒 Starting reservation attempts at {current_time}")
            break
        time.sleep(0.1)  # Check every 100ms

    # Run all reservation scripts every 0.2 seconds
    while True:
        for script in reservation_scripts:
            success = execute_reservation(script)
            if not success:
                print("❌ Aborting further requests due to CAPTCHA.")
                return  # Stop the script if a CAPTCHA is detected
            time.sleep(0.2)  # Wait 0.2 seconds before running the next script

if __name__ == "__main__":
    main()