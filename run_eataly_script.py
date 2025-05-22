import subprocess

def run_eataly_script():
    try:
        # Path to your AppleScript file
        applescript_path = "/Users/mason/eataly_script.applescript"

        # Run the AppleScript using osascript
        subprocess.run(["osascript", applescript_path], check=True)
        print("✅ Successfully ran the Eataly AppleScript!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to run the Eataly AppleScript: {e}")

# Example usage
if __name__ == "__main__":
    run_eataly_script()