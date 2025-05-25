import os
import json
import time

class AccountManager:
    """Manages multiple TGTG accounts, their credentials, and statuses."""

    def __init__(self, accounts_dir="tgtg-bot/accounts/"):
        """
        Initializes the AccountManager.

        Args:
            accounts_dir (str): Path to the directory containing account subdirectories.
        """
        self.accounts_dir = accounts_dir
        self.accounts = {}
        self.account_status = {}
        self.cooldown_timers = {}
        self.load_accounts()

    def load_accounts(self):
        """
        Scans the accounts directory and loads credentials for each account.
        """
        if not os.path.exists(self.accounts_dir):
            print(f"Error: Accounts directory not found at {self.accounts_dir}")
            # Create the directory if it doesn't exist, so the program can continue.
            os.makedirs(self.accounts_dir)
            print(f"Info: Created accounts directory at {self.accounts_dir}")
            return

        for account_name in os.listdir(self.accounts_dir):
            account_path = os.path.join(self.accounts_dir, account_name)
            if os.path.isdir(account_path):
                credentials_path = os.path.join(account_path, "credentials.json")
                if os.path.exists(credentials_path):
                    try:
                        with open(credentials_path, 'r') as f:
                            self.accounts[account_name] = json.load(f)
                            self.account_status[account_name] = "active"
                            print(f"Successfully loaded credentials for account: {account_name}")
                    except json.JSONDecodeError:
                        print(f"Error: Invalid JSON format in {credentials_path} for account {account_name}. Skipping.")
                    except Exception as e:
                        print(f"Error loading credentials for account {account_name}: {e}. Skipping.")
                else:
                    print(f"Warning: credentials.json not found in {account_path} for account {account_name}. Skipping.")

    def get_credentials(self, account_name):
        """
        Retrieves credentials for a specific account.

        Args:
            account_name (str): The name of the account.

        Returns:
            dict: The credentials for the account, or None if not found.
        """
        return self.accounts.get(account_name)

    def set_status(self, account_name, status):
        """
        Sets the status for a specific account.

        Args:
            account_name (str): The name of the account.
            status (str): The new status (e.g., "active", "cooldown", "captcha").
        """
        if account_name in self.account_status:
            self.account_status[account_name] = status
            print(f"Status for account {account_name} set to: {status}")
        else:
            print(f"Warning: Account {account_name} not found. Cannot set status.")

    def get_status(self, account_name):
        """
        Gets the current status of a specific account.

        Args:
            account_name (str): The name of the account.

        Returns:
            str: The current status of the account, or None if not found.
        """
        return self.account_status.get(account_name)

    def set_cooldown(self, account_name, duration_seconds):
        """
        Sets an account to "cooldown" status for a specified duration.

        Args:
            account_name (str): The name of the account.
            duration_seconds (int): The duration of the cooldown in seconds.
        """
        if account_name in self.account_status:
            self.set_status(account_name, "cooldown")
            self.cooldown_timers[account_name] = time.time() + duration_seconds
            print(f"Account {account_name} is now in cooldown for {duration_seconds} seconds.")
        else:
            print(f"Warning: Account {account_name} not found. Cannot set cooldown.")

    def check_cooldown(self, account_name):
        """
        Checks if an account's cooldown has expired. If so, resets its status.

        Args:
            account_name (str): The name of the account.

        Returns:
            bool: True if the account is still in cooldown, False otherwise.
        """
        if self.get_status(account_name) == "cooldown":
            if account_name in self.cooldown_timers:
                if time.time() >= self.cooldown_timers[account_name]:
                    self.set_status(account_name, "active")
                    del self.cooldown_timers[account_name]
                    print(f"Cooldown for account {account_name} has ended.")
                    return False  # Cooldown ended
                return True  # Still in cooldown
            else:
                # Account is in cooldown status but no timer found, reset to active
                self.set_status(account_name, "active")
                print(f"Warning: Cooldown timer not found for account {account_name} but was in cooldown status. Reset to active.")
                return False
        return False # Not in cooldown

    def get_all_account_names(self):
        """
        Returns a list of all loaded account names.

        Returns:
            list: A list of strings, where each string is an account name.
        """
        return list(self.accounts.keys())

if __name__ == '__main__':
    # Example Usage (for testing purposes)
    # Create a dummy accounts directory structure for testing
    if not os.path.exists("tgtg-bot/accounts/example_account_active"):
        os.makedirs("tgtg-bot/accounts/example_account_active")
    if not os.path.exists("tgtg-bot/accounts/example_account_cooldown"):
        os.makedirs("tgtg-bot/accounts/example_account_cooldown")
    if not os.path.exists("tgtg-bot/accounts/example_account_missing_creds"):
        os.makedirs("tgtg-bot/accounts/example_account_missing_creds")

    dummy_creds = {
        "access_token": "dummy_access",
        "refresh_token": "dummy_refresh",
        "cookie": "dummy_cookie",
        "user_id": "dummy_user"
    }
    with open("tgtg-bot/accounts/example_account_active/credentials.json", 'w') as f:
        json.dump(dummy_creds, f)
    with open("tgtg-bot/accounts/example_account_cooldown/credentials.json", 'w') as f:
        json.dump(dummy_creds, f)
    
    # Test with a non-existent directory (it should be created)
    # print("\\n--- Test with non-existent accounts directory ---")
    # non_existent_manager = AccountManager(accounts_dir="tgtg-bot/non_existent_accounts/")
    # print(f"Accounts loaded: {non_existent_manager.get_all_account_names()}")


    print("\\n--- Test with existing accounts directory ---")
    # Initialize AccountManager (it will call load_accounts)
    manager = AccountManager(accounts_dir="tgtg-bot/accounts/")
    
    print("\\n--- Initial Account States ---")
    all_accounts = manager.get_all_account_names()
    print(f"All loaded accounts: {all_accounts}")
    for acc in all_accounts:
        print(f"Account: {acc}, Status: {manager.get_status(acc)}, Credentials: {manager.get_credentials(acc)}")

    print("\\n--- Test Status Management ---")
    if "example_account_active" in all_accounts:
        manager.set_status("example_account_active", "captcha_required")
        print(f"Status of example_account_active: {manager.get_status('example_account_active')}")
        manager.set_status("example_account_active", "active") # Reset for other tests
        print(f"Status of example_account_active (reset): {manager.get_status('example_account_active')}")

    print("\\n--- Test Cooldown Management ---")
    if "example_account_cooldown" in all_accounts:
        print(f"Checking cooldown for example_account_cooldown (should be False): {manager.check_cooldown('example_account_cooldown')}")
        manager.set_cooldown("example_account_cooldown", 5) # 5 seconds cooldown
        print(f"Status of example_account_cooldown: {manager.get_status('example_account_cooldown')}")
        print(f"Checking cooldown for example_account_cooldown (should be True): {manager.check_cooldown('example_account_cooldown')}")
        print("Waiting for 6 seconds...")
        time.sleep(6)
        print(f"Checking cooldown for example_account_cooldown (should be False now): {manager.check_cooldown('example_account_cooldown')}")
        print(f"Status of example_account_cooldown after cooldown: {manager.get_status('example_account_cooldown')}")

    print("\\n--- Test Non-existent Account ---")
    print(f"Credentials for non_existent_account: {manager.get_credentials('non_existent_account')}")
    print(f"Status for non_existent_account: {manager.get_status('non_existent_account')}")
    manager.set_status('non_existent_account', 'active')
    manager.set_cooldown('non_existent_account', 10)

    # Clean up dummy directories and files
    # import shutil
    # shutil.rmtree("tgtg-bot/accounts/example_account_active", ignore_errors=True)
    # shutil.rmtree("tgtg-bot/accounts/example_account_cooldown", ignore_errors=True)
    # shutil.rmtree("tgtg-bot/accounts/example_account_missing_creds", ignore_errors=True)
    # if os.path.exists("tgtg-bot/non_existent_accounts"):
        # shutil.rmtree("tgtg-bot/non_existent_accounts")
    print("\\n--- Tests Complete ---")
