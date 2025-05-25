import time
import random
import threading
# from .account_manager import AccountManager # Use this if running as part of the package
# from .tgtg_client import TGTGClientWrapper
# from .notifier import Notifier
# from .sellout_tracker import SelloutTracker

# Placeholder for actual classes if not running in package context for subtask
class AccountManager: # Placeholder
    def __init__(self, accounts_dir): 
        self.accounts_dir = accounts_dir
        self._accounts_data = {} # Store credentials here
        self._account_status = {} # Store status like active, cooldown, captcha
        self._cooldown_end_times = {} # Store cooldown end times
        print(f"AccountManager (Placeholder) initialized for directory: {accounts_dir}")

    def load_accounts(self):
        print("AccountManager (Placeholder): Loading accounts...")
        # Simulate loading a couple of accounts
        # In a real scenario, this would scan self.accounts_dir
        example_accounts = {
            "acc1": {"user_id": "user1", "access_token": "acc1_at", "refresh_token": "acc1_rt", "cookie": "acc1_ck"},
            "acc2": {"user_id": "user2", "access_token": "acc2_at", "refresh_token": "acc2_rt", "cookie": "acc2_ck"},
            "acc_captcha": {"user_id": "user_captcha", "access_token": "captcha_at", "refresh_token": "captcha_rt", "cookie": "captcha_ck"},
            "acc_cooldown": {"user_id": "user_cooldown", "access_token": "cooldown_at", "refresh_token": "cooldown_rt", "cookie": "cooldown_ck"}
        }
        for name, creds in example_accounts.items():
            self._accounts_data[name] = creds
            if name == "acc_captcha":
                 self._account_status[name] = "captcha" # Pre-set for testing
            elif name == "acc_cooldown":
                self._account_status[name] = "cooldown" # Pre-set for testing
                self._cooldown_end_times[name] = time.time() + 30 # 30s cooldown for testing
            else:
                self._account_status[name] = "active"
        print(f"AccountManager (Placeholder): Loaded accounts: {list(self._accounts_data.keys())}")
        return list(self._accounts_data.keys())

    def get_all_account_names(self):
        return list(self._accounts_data.keys())

    def get_credentials(self, acc_name):
        return self._accounts_data.get(acc_name)

    def get_status(self, acc_name):
        return self._account_status.get(acc_name, "unknown")

    def set_status(self, acc_name, status):
        print(f"AccountManager (Placeholder): Setting {acc_name} to {status}")
        self._account_status[acc_name] = status
        if status != "cooldown": # Clear cooldown timer if status changes to something else
            if acc_name in self._cooldown_end_times:
                del self._cooldown_end_times[acc_name]


    def check_cooldown(self, acc_name):
        if self.get_status(acc_name) == "cooldown":
            cooldown_end_time = self._cooldown_end_times.get(acc_name)
            if cooldown_end_time:
                if time.time() >= cooldown_end_time:
                    print(f"AccountManager (Placeholder): Cooldown for {acc_name} expired.")
                    self.set_status(acc_name, "active") # Reset status
                    return False # No longer in cooldown
                return True # Still in cooldown
            else: # Was set to cooldown but no timer, reset
                print(f"AccountManager (Placeholder): {acc_name} was in cooldown but no timer. Resetting.")
                self.set_status(acc_name, "active")
                return False
        return False

    def set_cooldown(self, acc_name, duration_seconds):
        print(f"AccountManager (Placeholder): Setting {acc_name} to cooldown for {duration_seconds}s")
        self.set_status(acc_name, "cooldown")
        self._cooldown_end_times[acc_name] = time.time() + duration_seconds

class TGTGClientWrapper: # Placeholder
    def __init__(self, creds): 
        self.creds = creds
        self.user_id = creds.get("user_id", "unknown_user")
        print(f"TGTGClientWrapper (Placeholder) initialized for user: {self.user_id}")
        if not creds.get("access_token"):
            raise ValueError("Missing access_token in TGTGClientWrapper init")


    def get_favorites(self):
        print(f"TGTGClient (Placeholder): Getting favorites for {self.user_id}")
        if self.user_id == "user_captcha": # Simulate CAPTCHA for this user
            print(f"TGTGClient (Placeholder): CAPTCHA triggered for {self.user_id} during get_favorites")
            return {"captcha_detected": True, "error": "CAPTCHA challenge"}
        
        # Simulate some items
        return [
            {"item_id": "123", "item": {"item_id": "123"}, "display_name": "Magic Bag Alpha", "items_available": random.choice([0,0,1,2]), "store": {"store_name": "Alpha Store", "store_id": "s1"}},
            {"item_id": "456", "item": {"item_id": "456"}, "display_name": "Surprise Box Beta", "items_available": random.choice([0,1]), "store": {"store_name": "Beta Store", "store_id": "s2"}},
            {"item_id": "789", "item": {"item_id": "789"}, "display_name": "Eataly Special", "items_available": random.choice([0,0,0,1]), "store": {"store_name": "Eataly NYC Downtown", "store_id": "953570"}, "sold_out_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()) if random.choice([True, False]) else None}
        ]

    def create_order(self, item_id, quantity=1):
        print(f"TGTGClient (Placeholder): Attempting to create order for item {item_id} for user {self.user_id}")
        if self.user_id == "user_captcha": # Simulate CAPTCHA during order
            print(f"TGTGClient (Placeholder): CAPTCHA triggered for {self.user_id} during create_order")
            return {"captcha_detected": True, "error": "CAPTCHA challenge during order"}
        
        if item_id == "123" and random.random() < 0.3: # Simulate "item sold out" for item 123 sometimes
            print(f"TGTGClient (Placeholder): Order failed for {item_id} - item sold out")
            return {"error": "API_ITEM_SOLD_OUT: The item just sold out."} # Common TGTG error format
        
        if random.random() < 0.1: # Simulate some other random error
            return {"error": "Some random server error"}

        print(f"TGTGClient (Placeholder): Successfully created order for item {item_id}")
        return {"id": f"dummy_order_{item_id}_{random.randint(1000,9999)}", "state": "RESERVED"}


class Notifier: # Placeholder
    def __init__(self, phone_numbers): 
        self.phone_numbers = phone_numbers
        print(f"Notifier (Placeholder) initialized with numbers: {phone_numbers}")
    def send_notification(self, message): 
        print(f"Notifier (Placeholder): Sending message - '{message}' to {self.phone_numbers}")

class SelloutTracker: # Placeholder
    def __init__(self, log_file_path, accounts_dir): 
        self.log_file_path = log_file_path
        self.accounts_dir = accounts_dir
        print(f"SelloutTracker (Placeholder) initialized. Log: {log_file_path}, Accounts: {accounts_dir}")

    def log_reservation(self, account_name, order_details, item_details): 
        order_id = order_details.get("id", order_details.get("order_id", "unknown_order"))
        item_name = item_details.get('display_name', 'Unknown Item')
        print(f"SelloutTracker (Placeholder): Logging RESERVATION for {account_name}, item '{item_name}', order {order_id}")

    def log_sellout(self, account_name, item_details): 
        item_name = item_details.get('display_name', 'Unknown Item')
        store_name = item_details.get('store',{}).get('store_name', 'Unknown Store')
        print(f"SelloutTracker (Placeholder): Logging SELLOUT for account {account_name}, item '{item_name}' from '{store_name}'")


class Scheduler:
    def __init__(self, account_manager, notifier, sellout_tracker, config):
        """
        Initializes the Scheduler.
        Args:
            account_manager (AccountManager): Instance of AccountManager.
            notifier (Notifier): Instance of Notifier.
            sellout_tracker (SelloutTracker): Instance of SelloutTracker.
            config (dict): Global configuration dictionary. Expected keys:
                             "base_poll_interval_seconds" (e.g., 70)
                             "poll_interval_jitter_seconds" (e.g., 10)
                             "captcha_cooldown_hours" (e.g., 1)
                             "max_reservation_attempts" (e.g., 3)
        """
        self.account_manager = account_manager
        self.notifier = notifier
        self.sellout_tracker = sellout_tracker
        self.config = config
        self.running = False
        self.thread = None # For running the scheduler loop in a background thread
        
        print("Scheduler initialized.")

    def _get_poll_interval(self):
        base = self.config.get("base_poll_interval_seconds", 70)
        jitter = self.config.get("poll_interval_jitter_seconds", 10)
        interval = base + random.uniform(-jitter, jitter)
        # print(f"Scheduler: Calculated poll interval: {interval:.2f}s")
        return interval

    def _process_account(self, account_name):
        """
        Processes a single account: checks status, fetches favorites, reserves if available.
        """
        print(f"Scheduler: Processing account: {account_name}")

        # 1. Check account status and cooldown
        current_status = self.account_manager.get_status(account_name)
        if current_status == "cooldown":
            if not self.account_manager.check_cooldown(account_name): 
                print(f"Scheduler: Account {account_name} cooldown finished.")
            else:
                print(f"Scheduler: Account {account_name} is on cooldown. Skipping.")
                return

        if current_status == "captcha":
            print(f"Scheduler: Account {account_name} is flagged for CAPTCHA. Manual intervention likely needed or long cooldown active.")
            # check_cooldown might be relevant if CAPTCHA status also uses the standard cooldown mechanism
            self.account_manager.check_cooldown(account_name) # Check if its CAPTCHA cooldown expired
            if self.account_manager.get_status(account_name) == "captcha": # Still captcha after check
                 print(f"Scheduler: Account {account_name} remains in CAPTCHA status. Skipping.")
                 return


        # 2. Get credentials and initialize TGTGClientWrapper
        credentials = self.account_manager.get_credentials(account_name)
        if not credentials:
            print(f"Scheduler: Could not get credentials for {account_name}. Skipping.")
            return
        
        try:
            tgtg_client = TGTGClientWrapper(credentials)
        except ValueError as e:
            print(f"Scheduler: Error initializing TGTGClient for {account_name}: {e}. Skipping.")
            # This account might have invalid/incomplete credentials in its JSON
            self.account_manager.set_status(account_name, "error_creds") # Custom status
            return

        # 3. Fetch favorites
        print(f"Scheduler: Fetching favorites for {account_name}...")
        favorites_response = tgtg_client.get_favorites()

        if isinstance(favorites_response, dict) and favorites_response.get("captcha_detected"):
            print(f"Scheduler: CAPTCHA detected for {account_name} while fetching favorites.")
            self.account_manager.set_status(account_name, "captcha")
            captcha_cooldown_seconds = self.config.get("captcha_cooldown_hours", 1) * 3600
            self.account_manager.set_cooldown(account_name, captcha_cooldown_seconds)
            return
        elif isinstance(favorites_response, dict) and favorites_response.get("error"):
            print(f"Scheduler: Error fetching favorites for {account_name}: {favorites_response['error']}. Skipping.")
            # Optional: set a short generic error cooldown
            self.account_manager.set_cooldown(account_name, 60 * 5) # 5 min cooldown for generic API errors
            return
        
        if not favorites_response or not isinstance(favorites_response, list): 
            print(f"Scheduler: No favorite items found or unexpected response format for {account_name}.")
            return

        # 4. Process available items
        for item in favorites_response:
            # Robustly extract item details, accounting for potential variations in structure
            item_data = item.get("item", {}) # TGTG API often nests item details
            item_id = item_data.get("item_id") or item.get("item_id")
            display_name = item.get("display_name") or item_data.get("display_name", "Unknown Item")
            items_available = item.get("items_available", 0)
            
            store_info = item.get("store", {})
            store_name = store_info.get("store_name", "Unknown Store")
            store_id = store_info.get("store_id")

            print(f"Scheduler: Checking item '{display_name}' (ID: {item_id}) from '{store_name}' (ID: {store_id}) for {account_name}. Available: {items_available}")

            if items_available > 0:
                print(f"Scheduler: Found {items_available} bag(s) of '{display_name}' available for {account_name}!")
                
                reservation_successful = False
                for attempt in range(self.config.get("max_reservation_attempts", 3)):
                    print(f"Scheduler: Attempting to reserve item {item_id} (Attempt {attempt + 1}/{self.config.get('max_reservation_attempts', 3)})...")
                    order_response = tgtg_client.create_order(item_id)

                    if isinstance(order_response, dict) and order_response.get("captcha_detected"):
                        print(f"Scheduler: CAPTCHA detected for {account_name} during reservation attempt for item {item_id}.")
                        self.account_manager.set_status(account_name, "captcha")
                        captcha_cooldown_seconds = self.config.get("captcha_cooldown_hours", 1) * 3600
                        self.account_manager.set_cooldown(account_name, captcha_cooldown_seconds)
                        break 
                    elif isinstance(order_response, dict) and order_response.get("error"):
                        error_msg = order_response['error'].lower()
                        print(f"Scheduler: Error creating order for item {item_id} on account {account_name}: {order_response['error']}")
                        if "sold out" in error_msg or "items_available=0" in error_msg or "api_item_sold_out" in error_msg:
                           print(f"Scheduler: Item {item_id} ('{display_name}') sold out during reservation attempt.")
                           self.sellout_tracker.log_sellout(account_name, item) 
                           break 
                        time.sleep(random.uniform(1, 3)) 
                    elif isinstance(order_response, dict) and (order_response.get("state") == "RESERVED" or order_response.get("id")): 
                        order_id = order_response.get("id") or order_response.get("order_id", "N/A")
                        print(f"Scheduler: Successfully reserved item {item_id} ('{display_name}') for {account_name}! Order ID: {order_id}")
                        
                        self.sellout_tracker.log_reservation(account_name, order_response, item)
                        
                        message = f"✅ Reserved {display_name} from {store_name} on account {account_name}!" \
                                  f" Complete payment in TGTG app ASAP. Order ID: {order_id}"
                        self.notifier.send_notification(message)
                        reservation_successful = True
                        break 
                    else: 
                        print(f"Scheduler: Unexpected response when creating order for item {item_id}: {order_response}")
                        time.sleep(random.uniform(1,3))

                if not reservation_successful:
                    print(f"Scheduler: Failed to reserve item {item_id} ('{display_name}') for {account_name} after {self.config.get('max_reservation_attempts', 3)} attempts.")
            
            tracked_store_id = self.config.get("tracked_store_id_for_sellout")
            # Ensure tracked_store_id is string if store_id from API is string
            if tracked_store_id and str(store_id) == str(tracked_store_id) and items_available == 0:
                # Check if it has a 'sold_out_at' timestamp to confirm it's a recent sellout.
                # This part of the logic might need refinement based on how SelloutTracker determines "new" sellouts.
                # For now, if it's the tracked store and sold out, we log it.
                # The placeholder item has 'sold_out_at' sometimes.
                sold_out_at_ts = item.get("sold_out_at")
                if sold_out_at_ts: # Only log if we have a timestamp indicating when it sold out
                     print(f"Scheduler: Tracked item {display_name} from store {store_name} (ID: {store_id}) sold out at {sold_out_at_ts}")
                     self.sellout_tracker.log_sellout(account_name, item) # Pass full item details

    def _run_loop(self):
        """
        The main polling loop.
        """
        print("Scheduler: _run_loop started.")
        self.account_manager.load_accounts() 
        
        while self.running:
            account_names = self.account_manager.get_all_account_names()
            if not account_names:
                print("Scheduler: No accounts loaded. Waiting...")
                time.sleep(self._get_poll_interval()) # Wait before trying to load accounts again
                self.account_manager.load_accounts() # Try reloading
                continue

            print(f"Scheduler: Starting new polling cycle for accounts: {account_names}")
            
            random.shuffle(account_names) # Process accounts in a random order each cycle

            for account_name in account_names:
                if not self.running: 
                    print("Scheduler: self.running is false, breaking from account loop.")
                    break 
                try:
                    self._process_account(account_name)
                except Exception as e: 
                    print(f"Scheduler: UNEXPECTED CRITICAL ERROR processing account {account_name}: {e}")
                    import traceback
                    traceback.print_exc()
                    self.account_manager.set_status(account_name, "error_critical") 
                    self.account_manager.set_cooldown(account_name, 60 * 15) # 15 min cooldown for critical errors
                
                # Short delay between processing individual accounts, regardless of threading for _process_account
                # This can help distribute network load slightly.
                # If _process_account itself becomes async/threaded, this might be less critical.
                # For now, it ensures accounts are not hammered back-to-back in the same second.
                # This is NOT the main polling interval.
                if self.running: # Check flag again before sleep
                    time.sleep(random.uniform(1, 3)) # Small stagger between accounts in a cycle
            
            if not self.running:
                print("Scheduler: self.running is false, breaking from main loop before sleep.")
                break

            sleep_duration = self._get_poll_interval()
            print(f"Scheduler: All accounts processed in this cycle. Sleeping for {sleep_duration:.2f} seconds...")
            
            # Accurate sleep that can be interrupted by self.running changing
            # This is important for responsive stop()
            sleep_start_time = time.time()
            while self.running and (time.time() - sleep_start_time) < sleep_duration:
                time.sleep(0.5) # Check self.running every 0.5s

        print("Scheduler: _run_loop finished.")


    def start(self):
        """
        Starts the scheduler loop in a new thread.
        """
        if self.running:
            print("Scheduler is already running.")
            return

        print("Scheduler: Starting...")
        self.running = True
        
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.name = "SchedulerThread"
        self.thread.start()
        print("Scheduler: Background thread started.")

    def stop(self):
        """
        Stops the scheduler loop.
        """
        print("Scheduler: Stopping...")
        self.running = False
        if self.thread and self.thread.is_alive():
            print("Scheduler: Waiting for background thread to finish...")
            self.thread.join(timeout=15) # Increased timeout slightly
            if self.thread.is_alive():
                print("Scheduler: Background thread did not finish in time.")
            else:
                print("Scheduler: Background thread finished.")
        else:
            print("Scheduler: No active background thread to stop or already stopped.")
        print("Scheduler: Stopped.")

# Example Usage (for testing purposes)
if __name__ == '__main__':
    print("Scheduler Test Script")
    
    mock_config = {
        "base_poll_interval_seconds": 15, # Short for testing, original was 5
        "poll_interval_jitter_seconds": 2,  # Original was 1
        "captcha_cooldown_hours": 0.005, # ~18 seconds for testing
        "max_reservation_attempts": 2,
        "tracked_store_id_for_sellout": "953570" 
    }
    # Ensure this path is relative to where the script might be run from, or use absolute paths.
    # For the subtask environment, it's usually /app
    mock_accounts_dir = "/app/tgtg-bot/accounts/" 
    
    import os
    # Create dummy account dirs for testing if AccountManager placeholder doesn't fully mock loading
    # The placeholder AccountManager now creates some in-memory accounts, so filesystem setup is less critical for it.
    # However, if real AccountManager was used, this would be important.
    # For consistency, let's assume AccountManager might try to list dirs.
    os.makedirs(os.path.join(mock_accounts_dir, "acc1"), exist_ok=True)
    os.makedirs(os.path.join(mock_accounts_dir, "acc2"), exist_ok=True)
    os.makedirs(os.path.join(mock_accounts_dir, "acc_captcha"), exist_ok=True)
    os.makedirs(os.path.join(mock_accounts_dir, "acc_cooldown"), exist_ok=True)
    # Dummy credentials files (optional, as placeholder AccountManager creates them in memory for now)
    # with open(os.path.join(mock_accounts_dir, "acc1", "credentials.json"), "w") as f:
    #     json.dump({"user_id": "user1", "access_token": "at1", "refresh_token": "rt1", "cookie": "ck1"}, f)


    am = AccountManager(accounts_dir=mock_accounts_dir)
    # am.load_accounts() # Called in scheduler's run loop
     
    notifier_instance = Notifier(phone_numbers=["+1234567890"]) # Example with country code
    sellout_tracker_instance = SelloutTracker(
        log_file_path="/app/tgtg-bot/sellout_log.csv", 
        accounts_dir=mock_accounts_dir
    )

    scheduler = Scheduler(
        account_manager=am,
        notifier=notifier_instance,
        sellout_tracker=sellout_tracker_instance,
        config=mock_config
    )

    print("Starting scheduler for testing...")
    scheduler.start()

    try:
        # Keep main thread alive to observe scheduler's print statements
        # Run for a limited time for automated testing, e.g., 60 seconds
        main_run_time = 45 # seconds
        print(f"Main thread will keep alive for {main_run_time} seconds to observe scheduler.")
        for i in range(main_run_time):
            if not scheduler.running:
                print("Main: Scheduler stopped unexpectedly.")
                break
            time.sleep(1)
        print(f"Main: {main_run_time} seconds elapsed.")

    except KeyboardInterrupt:
        print("Main: Keyboard interrupt received.")
    finally:
        print("Main: Initiating scheduler stop sequence...")
        scheduler.stop()
        print("Main: Test finished.")
        # Add a small delay to ensure all print statements from threads are flushed if running in some environments
        time.sleep(1)
        print("Exiting test script.")
