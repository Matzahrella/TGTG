import os
# Ensure the script can find the core modules.
# This assumes the script is run from a context where 'core' is discoverable.
# If running from tgtg-bot/ directory as CWD, this should work.
from core.account_manager import AccountManager

# Path to the accounts directory within the tgtg-bot structure
accounts_dir = "tgtg-bot/accounts/"

print(f"Attempting to load accounts from: {os.path.abspath(accounts_dir)}")

if not os.path.isdir(accounts_dir):
    print(f"Error: Accounts directory '{accounts_dir}' does not exist or is not a directory.")
else:
    # List contents of accounts_dir for debugging
    print(f"Contents of '{accounts_dir}': {os.listdir(accounts_dir)}")
    
    # List contents of one specific new account dir for debugging
    example_account_path = os.path.join(accounts_dir, "gideon") # or any other created account
    if os.path.isdir(example_account_path):
        print(f"Contents of '{example_account_path}': {os.listdir(example_account_path)}")
    else:
        print(f"Warning: Example account directory '{example_account_path}' not found for detailed listing.")


    try:
        account_manager = AccountManager(accounts_dir=accounts_dir)
        account_manager.load_accounts() # This method now also creates accounts_dir if missing.
        
        loaded_accounts = account_manager.get_all_account_names()
        
        print("\n--- Verification Results ---")
        if loaded_accounts:
            print(f"Successfully loaded the following {len(loaded_accounts)} accounts:")
            for acc_name in loaded_accounts:
                creds = account_manager.get_credentials(acc_name)
                status = account_manager.get_status(acc_name)
                # Basic check for credential content
                if creds and 'access_token' in creds:
                    print(f"  - {acc_name} (Status: {status}, Credentials Loaded: Yes)")
                else:
                    print(f"  - {acc_name} (Status: {status}, Credentials Loaded: No/Invalid)")
        else:
            # Check if the accounts_dir itself was empty or if loading failed for all
            if not os.listdir(accounts_dir) or all(f == 'example_account' for f in os.listdir(accounts_dir)): # Exclude the default example
                 print("No account subdirectories found in the accounts directory (excluding 'example_account').")
            else:
                 print("Failed to load any accounts. Check AccountManager logs or issues with credentials.json files.")
                 
        # Specific check for one or two expected accounts
        expected_accounts_to_check = ["gideon", "fluffy"]
        for acc in expected_accounts_to_check:
            if acc in loaded_accounts:
                print(f"Verified: Account '{acc}' is loaded.")
            else:
                print(f"Verification Warning: Expected account '{acc}' was NOT loaded.")

    except ImportError as e:
        print(f"ImportError: Could not import AccountManager or its dependencies. Ensure PYTHONPATH is correct or run from project root. {e}")
    except Exception as e:
        print(f"An error occurred during account loading verification: {e}")
