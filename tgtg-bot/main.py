import json
import time
import os # For path joining and existence checks

# Assuming these modules are in the 'core' subdirectory relative to main.py
from core.account_manager import AccountManager
from core.notifier import Notifier
from core.sellout_tracker import SelloutTracker
from core.scheduler import Scheduler
from core.ui import CLI_UI
# TGTGClientWrapper is used by Scheduler, not directly instantiated in main usually

# --- Configuration Loading ---
DEFAULT_CONFIG = {
    "target_phone_numbers": [],
    "base_poll_interval_seconds": 70,
    "poll_interval_jitter_seconds": 10,
    "captcha_cooldown_hours": 1,
    "max_reservation_attempts": 3,
    "tracked_store_ids_for_sellout": [],
    "accounts_path": "./accounts/", # Relative to main.py's location (tgtg-bot/)
    "sellout_log_csv_path": "./sellout_log.csv" # Relative to main.py's location
}

def load_config(config_path="config.json"):
    """Loads configuration from a JSON file, using defaults if file or keys are missing."""
    if not os.path.exists(config_path):
        print(f"Warning: Configuration file '{config_path}' not found. Using default settings.")
        # Optionally, create a default config.json here if it's critical
        # with open(config_path, 'w') as f:
        #     json.dump(DEFAULT_CONFIG, f, indent=4)
        # print(f"A default '{config_path}' has been created. Please review and customize it.")
        return DEFAULT_CONFIG

    loaded_config = DEFAULT_CONFIG.copy() # Start with defaults
    try:
        with open(config_path, 'r') as f:
            user_config = json.load(f)
            loaded_config.update(user_config) # Override defaults with user settings
            # Basic validation for critical paths
            if not isinstance(loaded_config.get("target_phone_numbers"), list):
                print("Warning: 'target_phone_numbers' in config is not a list. Using default.")
                loaded_config["target_phone_numbers"] = DEFAULT_CONFIG["target_phone_numbers"]

    except json.JSONDecodeError:
        print(f"Error: Configuration file '{config_path}' is not valid JSON. Using default settings.")
        return DEFAULT_CONFIG # Fallback to defaults
    except Exception as e:
        print(f"Error loading configuration '{config_path}': {e}. Using default settings.")
        return DEFAULT_CONFIG # Fallback
        
    return loaded_config

def main():
    print("Starting TGTG Reservation Bot...")

    # 1. Load Configuration
    # Assume config.json is in the same directory as main.py
    config = load_config("config.json") 
    
    # --- Verify critical configuration ---
    if not config.get("target_phone_numbers"):
        print("ALERT: 'target_phone_numbers' is not configured in config.json. Notifications will not be sent.")
        # Depending on strictness, could exit here or just warn.
        # For now, let it run but without notification capability.

    # Ensure paths are constructed correctly if they are relative from config.json
    # For this project, paths are relative to the project root (where main.py is)
    accounts_dir = config["accounts_path"]
    sellout_log_path = config["sellout_log_csv_path"]

    # Ensure the accounts directory exists, as AccountManager might expect it.
    if not os.path.isdir(accounts_dir):
        print(f"Warning: Accounts directory '{accounts_dir}' not found. Creating it.")
        try:
            os.makedirs(accounts_dir, exist_ok=True)
            print(f"Please add account subdirectories with credentials.json to '{accounts_dir}'.")
        except OSError as e:
            print(f"Error: Could not create accounts directory '{accounts_dir}': {e}. Exiting.")
            return

    # 2. Initialize Components
    print("Initializing components...")
    try:
        account_manager = AccountManager(accounts_dir=accounts_dir)
        # account_manager.load_accounts() # Scheduler calls this now
        
        notifier = Notifier(phone_numbers=config["target_phone_numbers"])
        
        sellout_tracker = SelloutTracker(
            sellout_log_csv_path=sellout_log_path,
            accounts_base_dir=accounts_dir
        )
        
        # Scheduler needs the config dict for its own settings
        scheduler = Scheduler(
            account_manager=account_manager,
            notifier=notifier,
            sellout_tracker=sellout_tracker,
            config=config # Pass the whole config dict
        )
        
        # Pass a reference to the actual scheduler instance, not a placeholder
        cli_ui = CLI_UI(
            account_manager=account_manager,
            scheduler=scheduler 
            # tgtg_clients_provider can be omitted if UI gets data via Scheduler/AccountManager
        )
    except Exception as e:
        print(f"Error during component initialization: {e}")
        # Log this error in more detail if a logging framework were in place
        return # Exit if components can't be initialized

    # 3. Start Services
    print("Starting services...")
    try:
        scheduler.start()
        cli_ui.start() # UI should start after scheduler so it can pull initial data

        # Keep the main thread alive until a shutdown signal (e.g., Ctrl+C)
        # The UI and Scheduler are running in daemon threads.
        # The UI's KeyboardInterrupt handler will set its `running` to False.
        # We also need to handle it here to stop the scheduler.
        while True:
            if not cli_ui.running and not scheduler.running: # Both somehow stopped
                print("Main: Both UI and Scheduler appear to have stopped unexpectedly.")
                break
            if not cli_ui.running and scheduler.running: # UI stopped (e.g. Ctrl+C in UI)
                print("Main: UI has stopped. Initiating scheduler shutdown...")
                scheduler.stop()
                break
            # Could add checks here if scheduler stops unexpectedly too.
            time.sleep(1) # Keep main thread responsive

    except KeyboardInterrupt:
        print("Main: KeyboardInterrupt received. Shutting down services...")
    except Exception as e: # Catch any other unexpected errors in the main execution block
        print(f"Main: An unexpected error occurred: {e}")
    finally:
        print("Main: Initiating graceful shutdown...")
        if 'cli_ui' in locals() and cli_ui.running:
            print("Main: Stopping UI...")
            cli_ui.stop()
        
        if 'scheduler' in locals() and scheduler.running: # Check if scheduler is defined and running
            print("Main: Stopping Scheduler...")
            scheduler.stop()
        
        print("TGTG Reservation Bot has shut down.")

if __name__ == "__main__":
    # This structure assumes that all 'core' modules are in a subdirectory named 'core'
    # and main.py is in the parent directory of 'core'.
    # e.g. tgtg-bot/main.py and tgtg-bot/core/scheduler.py
    
    # If scripts are in the same directory, imports would be:
    # from account_manager import AccountManager (etc.)
    main()
```
