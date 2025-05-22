import subprocess
import time
import sys

# List of scripts to run in sequence
scripts = [
    "CreatePizza.py",
    "CreatePizzaGideon.py"
]

# Time interval between the first set of scripts and the next set (in seconds)
interval = 10

# Function to run a script and check for CAPTCHA in the output
def run_script(script_name):
    try:
        print(f"🚀 Running {script_name}...")
        result = subprocess.run(["python3", script_name], text=True, capture_output=True, check=True)
        print(f"✅ Finished running {script_name}.")
        print(result.stdout)

        # Check for CAPTCHA in the output
        if "captcha" in result.stdout.lower():
            print("❌ CAPTCHA detected! Aborting the process.")
            sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error while running {script_name}: {e}")
        print(e.stdout)
        print(e.stderr)
        sys.exit(1)

# Run the first set of scripts sequentially
for script in scripts:
    run_script(script)

# Wait for the specified interval
print(f"⏳ Waiting for {interval} seconds before running the next set of scripts...")
time.sleep(interval)

# Run ShowFavorites.py and AbortPizza.py simultaneously
try:
    print("🚀 Running ShowFavorites.py and AbortPizza.py simultaneously...")
    show_favorites_process = subprocess.Popen(["python3", "ShowFavorites.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    abort_pizza_process = subprocess.Popen(["python3", "AbortPizza.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Wait for both processes to complete
    show_favorites_stdout, show_favorites_stderr = show_favorites_process.communicate()
    abort_pizza_stdout, abort_pizza_stderr = abort_pizza_process.communicate()

    # Print outputs
    print("✅ ShowFavorites.py Output:")
    print(show_favorites_stdout)
    print("✅ AbortPizza.py Output:")
    print(abort_pizza_stdout)

    # Check for CAPTCHA in either output
    if "captcha" in show_favorites_stdout.lower() or "captcha" in abort_pizza_stdout.lower():
        print("❌ CAPTCHA detected in one of the scripts! Aborting the process.")
        sys.exit(1)

except Exception as e:
    print(f"❌ Error while running ShowFavorites.py or AbortPizza.py: {e}")
    sys.exit(1)

print("🎉 All scripts have been executed successfully!")