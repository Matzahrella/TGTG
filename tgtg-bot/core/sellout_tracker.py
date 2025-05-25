import csv
import json
import os
import datetime # For timestamps

class SelloutTracker:
    def __init__(self, sellout_log_csv_path, accounts_base_dir):
        """
        Initializes the SelloutTracker.
        Args:
            sellout_log_csv_path (str): Path to the CSV file for logging sellouts (e.g., "tgtg-bot/sellout_log.csv").
            accounts_base_dir (str): Path to the base directory where account folders are located (e.g., "tgtg-bot/accounts/").
        """
        self.sellout_log_csv_path = sellout_log_csv_path
        self.accounts_base_dir = accounts_base_dir
        self._ensure_csv_header()

    def _ensure_csv_header(self):
        """
        Ensures the CSV file exists and has the correct header.
        """
        # Check if file exists and is not empty to avoid writing header multiple times
        file_exists = os.path.isfile(self.sellout_log_csv_path)
        is_empty = file_exists and os.path.getsize(self.sellout_log_csv_path) == 0

        if not file_exists or is_empty:
            try:
                # Ensure directory for CSV log exists
                csv_dir = os.path.dirname(self.sellout_log_csv_path)
                if csv_dir: # Check if csv_dir is not an empty string (i.e., path is not just a filename)
                    os.makedirs(csv_dir, exist_ok=True)
                
                with open(self.sellout_log_csv_path, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(["timestamp", "store_id", "store_name", "item_id", "item_name", "account_name", "event_type", "sold_out_at_api"])
                print(f"SelloutTracker: Initialized CSV log with header at {self.sellout_log_csv_path}")
            except IOError as e:
                print(f"SelloutTracker: Error initializing CSV log at {self.sellout_log_csv_path}: {e}")
            except Exception as e: # Catch other potential errors like permission issues
                print(f"SelloutTracker: Unexpected error initializing CSV log: {e}")


    def log_reservation(self, account_name, order_response, item_details):
        """
        Logs a successful reservation.
        - Appends order details to the account's orders.json.
        - Logs a 'reservation' event to the sellout_log.csv.
        Args:
            account_name (str): The name of the account that made the reservation.
            order_response (dict): The API response from create_order(). Expected to have an "id" or "order_id".
            item_details (dict): Dictionary containing details of the item, including
                                 "item_id", "display_name", "store": {"store_id", "store_name"}.
                                 Structure might vary based on TGTG API (e.g. item_details.get("item", {}).get("item_id"))
        """
        # 1. Log to account's orders.json
        account_orders_path = os.path.join(self.accounts_base_dir, account_name, "orders.json")
        try:
            os.makedirs(os.path.dirname(account_orders_path), exist_ok=True)
            
            existing_orders = []
            if os.path.exists(account_orders_path): # Check if file exists
                try:
                    with open(account_orders_path, 'r') as f:
                        content = f.read()
                        if content.strip(): # Check if file is not empty (prevents error with json.loads on empty string)
                             existing_orders = json.loads(content)
                             if not isinstance(existing_orders, list): # Ensure it's a list
                                 print(f"SelloutTracker: Warning - orders.json for {account_name} was not a list. Re-initializing.")
                                 existing_orders = []
                        # If file is empty, existing_orders remains an empty list, which is correct.
                except json.JSONDecodeError:
                    print(f"SelloutTracker: Warning - orders.json for {account_name} is corrupted. Re-initializing.")
                    existing_orders = [] # Reset if corrupted
            
            log_entry = {
                "timestamp_utc": datetime.datetime.utcnow().isoformat() + "Z",
                "reservation_details": order_response,
                "item_details_at_reservation": item_details
            }
            existing_orders.append(log_entry)
            
            with open(account_orders_path, 'w') as f:
                json.dump(existing_orders, f, indent=4)
            print(f"SelloutTracker: Logged reservation to {account_orders_path}")

        except IOError as e:
            print(f"SelloutTracker: Error writing to {account_orders_path}: {e}")
        except Exception as e:
            print(f"SelloutTracker: Unexpected error logging reservation to JSON for {account_name}: {e}")


        # 2. Log to central sellout_log.csv
        try:
            # Ensure header exists (in case file was deleted after init, or for robustness)
            if not os.path.isfile(self.sellout_log_csv_path) or os.path.getsize(self.sellout_log_csv_path) == 0:
                self._ensure_csv_header() 

            with open(self.sellout_log_csv_path, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                
                item_data = item_details.get("item", {}) 
                item_id = item_data.get("item_id") or item_details.get("item_id", "N/A")
                item_name = item_details.get("display_name") or item_data.get("name", "N/A") 
                
                store_info = item_details.get("store", {})
                store_id = store_info.get("store_id", "N/A")
                store_name = store_info.get("store_name", "N/A")
                
                writer.writerow([
                    datetime.datetime.utcnow().isoformat() + "Z",
                    store_id,
                    store_name,
                    item_id,
                    item_name,
                    account_name,
                    "RESERVED",
                    item_details.get("sold_out_at", "N/A") 
                ])
            print(f"SelloutTracker: Logged reservation event to {self.sellout_log_csv_path}")
        except IOError as e:
            print(f"SelloutTracker: Error writing reservation event to CSV log: {e}")
        except Exception as e:
            print(f"SelloutTracker: Unexpected error logging reservation to CSV for {account_name}: {e}")


    def log_sellout(self, account_name, item_details, event_type="SOLD_OUT_API"):
        """
        Logs an item sellout event.
        Args:
            account_name (str): The name of the account that observed the sellout.
            item_details (dict): Dictionary containing details of the item.
            event_type (str): Description of the sellout event.
        """
        try:
            # Ensure header exists
            if not os.path.isfile(self.sellout_log_csv_path) or os.path.getsize(self.sellout_log_csv_path) == 0:
                self._ensure_csv_header()

            with open(self.sellout_log_csv_path, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                
                item_data = item_details.get("item", {})
                item_id = item_data.get("item_id") or item_details.get("item_id", "N/A")
                item_name = item_details.get("display_name") or item_data.get("name", "N/A")
                
                store_info = item_details.get("store", {})
                store_id = store_info.get("store_id", "N/A")
                store_name = store_info.get("store_name", "N/A")
                
                api_sold_out_time = item_details.get("sold_out_at", "N/A")

                writer.writerow([
                    datetime.datetime.utcnow().isoformat() + "Z",
                    store_id,
                    store_name,
                    item_id,
                    item_name,
                    account_name,
                    event_type,
                    api_sold_out_time 
                ])
            print(f"SelloutTracker: Logged '{event_type}' event for item {item_name} ({item_id}) to {self.sellout_log_csv_path}")
        except IOError as e:
            print(f"SelloutTracker: Error writing sellout event to CSV log: {e}")
        except Exception as e:
            print(f"SelloutTracker: Unexpected error logging sellout to CSV: {e}")


# Example Usage (for testing purposes)
# if __name__ == '__main__':
#     print("SelloutTracker Test Script")
#     
#     # Define paths for testing - use a subdirectory to keep test outputs organized
#     test_output_dir = "test_tracker_output" # Changed from root to subdir
#     if not os.path.exists(test_output_dir):
#         os.makedirs(test_output_dir)
# 
#     test_csv_path = os.path.join(test_output_dir, "test_sellout_log.csv")
#     test_accounts_dir = os.path.join(test_output_dir, "test_accounts_data/") 
#     
#     # Clean up previous test files if they exist
#     if os.path.exists(test_csv_path):
#         os.remove(test_csv_path)
#     
#     # shutil.rmtree can fail if dir doesn't exist, check first
#     if os.path.exists(test_accounts_dir):
#         import shutil
#         shutil.rmtree(test_accounts_dir) 
#         
#     # No need to pre-create test_accounts_dir, log_reservation should create subdirs
# 
#     tracker = SelloutTracker(sellout_log_csv_path=test_csv_path, accounts_base_dir=test_accounts_dir)
# 
#     mock_account_name = "test_user_1"
# 
#     mock_order_response = {"id": "order123", "state": "RESERVED", "item_id": "item789"}
#     mock_item_details_eataly = {
#         "item_id": "item789", 
#         "display_name": "Eataly Surprise Bag",
#         "items_available": 0, 
#         "store": {
#             "store_id": "953570", 
#             "store_name": "Eataly NYC Downtown"
#         },
#         "sold_out_at": datetime.datetime.utcnow().isoformat() + "Z" 
#     }
#     
#     mock_item_details_other = {
#         "item": { 
#             "item_id": "itemABC",
#             "name": "Other Bag" 
#         },
#         "display_name": "Other Bag Display Name", 
#         "items_available": 1,
#         "store": {
#             "store_id": "12345",
#             "store_name": "Some Other Store"
#         }
#     }
# 
#     print("\n--- Testing log_reservation (Eataly) ---")
#     tracker.log_reservation(mock_account_name, mock_order_response, mock_item_details_eataly)
#     
#     dummy_orders_file = os.path.join(test_accounts_dir, mock_account_name, "orders.json")
#     if os.path.exists(dummy_orders_file):
#         with open(dummy_orders_file, 'r') as f:
#             print(f"Contents of {dummy_orders_file} after first Eataly reservation:\n{f.read()}")
#     else:
#         print(f"{dummy_orders_file} was not created.")
# 
#     print("\n--- Testing log_reservation (Other Bag, same account) ---")
#     mock_order_response_2 = {"id": "order124", "state": "RESERVED", "item_id": "itemABC"}
#     tracker.log_reservation(mock_account_name, mock_order_response_2, mock_item_details_other)
#     if os.path.exists(dummy_orders_file):
#         with open(dummy_orders_file, 'r') as f:
#             print(f"Contents of {dummy_orders_file} after second (Other Bag) reservation:\n{f.read()}")
# 
#     print("\n--- Testing log_sellout (Eataly, e.g., from poll) ---")
#     tracker.log_sellout(mock_account_name, mock_item_details_eataly, event_type="SOLD_OUT_POLL")
# 
#     print("\n--- Testing log_sellout (Other Bag, e.g., API error during reservation by another account) ---")
#     mock_item_details_other_sold_out = mock_item_details_other.copy() 
#     mock_item_details_other_sold_out["items_available"] = 0
#     mock_item_details_other_sold_out["sold_out_at"] = (datetime.datetime.utcnow() - datetime.timedelta(minutes=5)).isoformat() + "Z" 
#     tracker.log_sellout("another_account", mock_item_details_other_sold_out, event_type="SOLD_OUT_API_FAIL")
#     
#     print("\n--- Testing log_reservation with corrupted orders.json ---")
#     corrupted_account_name = "corrupted_user"
#     corrupted_orders_file = os.path.join(test_accounts_dir, corrupted_account_name, "orders.json")
#     os.makedirs(os.path.dirname(corrupted_orders_file), exist_ok=True)
#     with open(corrupted_orders_file, 'w') as f:
#         f.write("this is not valid json")
#     tracker.log_reservation(corrupted_account_name, mock_order_response, mock_item_details_eataly)
#     if os.path.exists(corrupted_orders_file):
#         with open(corrupted_orders_file, 'r') as f:
#             print(f"Contents of {corrupted_orders_file} after trying to log to corrupted file:\n{f.read()}")
# 
#     print("\n--- Testing log_reservation with empty orders.json ---")
#     empty_account_name = "empty_user"
#     empty_orders_file = os.path.join(test_accounts_dir, empty_account_name, "orders.json")
#     os.makedirs(os.path.dirname(empty_orders_file), exist_ok=True)
#     with open(empty_orders_file, 'w') as f:
#         pass 
#     tracker.log_reservation(empty_account_name, mock_order_response, mock_item_details_eataly)
#     if os.path.exists(empty_orders_file):
#         with open(empty_orders_file, 'r') as f:
#             print(f"Contents of {empty_orders_file} after trying to log to empty file:\n{f.read()}")
# 
# 
#     print(f"\n--- Final Check ---")
#     print(f"Check {test_csv_path} and {test_accounts_dir} for logs.")
#     if os.path.exists(test_csv_path):
#         with open(test_csv_path, 'r') as f:
#             print(f"Contents of {test_csv_path}:\n{f.read()}")
#     else:
#         print(f"{test_csv_path} was not created.")
