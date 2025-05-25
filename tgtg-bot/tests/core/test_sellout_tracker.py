import unittest
import os
import csv
import json
import shutil # For managing temporary directories
import datetime

# Adjust import path as needed
from core.sellout_tracker import SelloutTracker

class TestSelloutTracker(unittest.TestCase):

    def setUp(self):
        """Set up temporary paths for logs for each test."""
        self.test_base_dir = "test_temp_tracker_data"
        self.test_csv_path = os.path.join(self.test_base_dir, "sellout_log.csv")
        self.test_accounts_base_dir = os.path.join(self.test_base_dir, "accounts")

        # Ensure clean environment for each test
        if os.path.exists(self.test_base_dir):
            shutil.rmtree(self.test_base_dir)
        os.makedirs(self.test_accounts_base_dir, exist_ok=True)
        
        self.tracker = SelloutTracker(
            sellout_log_csv_path=self.test_csv_path,
            accounts_base_dir=self.test_accounts_base_dir
        )

    def tearDown(self):
        """Clean up temporary log paths after each test."""
        if os.path.exists(self.test_base_dir):
            shutil.rmtree(self.test_base_dir)

    def test_init_and_ensure_csv_header(self):
        """Test that __init__ creates the CSV file with a header if it doesn't exist."""
        self.assertTrue(os.path.exists(self.test_csv_path), "CSV log file should be created.")
        with open(self.test_csv_path, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)
            self.assertEqual(header, ["timestamp", "store_id", "store_name", "item_id", "item_name", "account_name", "event_type", "sold_out_at_api"])
        
        # Test that calling init again doesn't rewrite header if file has content (implicitly tested by setUp creating new instance)
        # To be more explicit, we can check row count after creating another instance or calling _ensure_csv_header again
        self.tracker._ensure_csv_header() # Call again
        with open(self.test_csv_path, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            row_count = sum(1 for row in reader)
            self.assertEqual(row_count, 1, "Header should not be written multiple times to an existing file with header.")


    def test_log_reservation_new_files(self):
        """Test log_reservation creating new JSON and adding to new CSV."""
        account_name = "test_acc1"
        order_response = {"id": "order001", "state": "RESERVED"}
        item_details = {
            "item_id": "item001", "display_name": "Surprise Bag 1",
            "store": {"store_id": "store1", "store_name": "Store One"},
            "sold_out_at": "2023-01-01T12:00:00Z"
        }
        
        self.tracker.log_reservation(account_name, order_response, item_details)
        
        # Check JSON log
        expected_json_path = os.path.join(self.test_accounts_base_dir, account_name, "orders.json")
        self.assertTrue(os.path.exists(expected_json_path))
        with open(expected_json_path, 'r') as f:
            orders_data = json.load(f)
            self.assertEqual(len(orders_data), 1)
            self.assertEqual(orders_data[0]["reservation_details"], order_response)
            self.assertEqual(orders_data[0]["item_details_at_reservation"], item_details)
            self.assertTrue("timestamp_utc" in orders_data[0])

        # Check CSV log
        with open(self.test_csv_path, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader) # Skip header
            log_entry = next(reader)
            self.assertEqual(log_entry[1], "store1")
            self.assertEqual(log_entry[2], "Store One")
            self.assertEqual(log_entry[3], "item001")
            self.assertEqual(log_entry[4], "Surprise Bag 1")
            self.assertEqual(log_entry[5], account_name)
            self.assertEqual(log_entry[6], "RESERVED")
            self.assertEqual(log_entry[7], "2023-01-01T12:00:00Z")

    def test_log_reservation_append_to_existing_json(self):
        """Test log_reservation appending to an existing orders.json file."""
        account_name = "test_acc_append"
        
        # Initial reservation
        order1 = {"id": "orderA"}
        item1 = {"item_id": "itemA", "display_name": "Item A", "store": {"store_id": "sA", "store_name": "Store A"}}
        self.tracker.log_reservation(account_name, order1, item1)
        
        # Second reservation for the same account
        order2 = {"id": "orderB"}
        item2 = {"item_id": "itemB", "display_name": "Item B", "store": {"store_id": "sB", "store_name": "Store B"}}
        self.tracker.log_reservation(account_name, order2, item2)
        
        expected_json_path = os.path.join(self.test_accounts_base_dir, account_name, "orders.json")
        with open(expected_json_path, 'r') as f:
            orders_data = json.load(f)
            self.assertEqual(len(orders_data), 2)
            self.assertEqual(orders_data[0]["reservation_details"], order1)
            self.assertEqual(orders_data[1]["reservation_details"], order2)

    def test_log_reservation_handles_corrupted_json(self):
        """Test log_reservation correctly handles (overwrites/resets) a corrupted orders.json."""
        account_name = "test_acc_corrupt"
        account_json_path = os.path.join(self.test_accounts_base_dir, account_name, "orders.json")
        os.makedirs(os.path.dirname(account_json_path), exist_ok=True)
        with open(account_json_path, 'w') as f:
            f.write("this is not valid json {") # Corrupted content
            
        order_response = {"id": "order_after_corrupt", "state": "RESERVED"}
        item_details = {"item_id": "item_ac", "display_name": "Item After Corrupt", "store": {"store_id": "sAC", "store_name": "Store AC"}}
        
        self.tracker.log_reservation(account_name, order_response, item_details)
        
        # Should create a new list with the current order
        with open(account_json_path, 'r') as f:
            orders_data = json.load(f)
            self.assertEqual(len(orders_data), 1)
            self.assertEqual(orders_data[0]["reservation_details"], order_response)

    def test_log_reservation_handles_json_as_non_list(self):
        """Test log_reservation handles orders.json that is valid JSON but not a list."""
        account_name = "test_acc_non_list_json"
        account_json_path = os.path.join(self.test_accounts_base_dir, account_name, "orders.json")
        os.makedirs(os.path.dirname(account_json_path), exist_ok=True)
        with open(account_json_path, 'w') as f:
            json.dump({"key": "value"}, f) # Valid JSON, but a dict, not a list
            
        order_response = {"id": "order_after_dict", "state": "RESERVED"}
        item_details = {"item_id": "item_ad", "display_name": "Item After Dict", "store": {"store_id": "sAD", "store_name": "Store AD"}}
        
        self.tracker.log_reservation(account_name, order_response, item_details)
        
        with open(account_json_path, 'r') as f:
            orders_data = json.load(f)
            self.assertEqual(len(orders_data), 1) # Should have reset to a list with the new item
            self.assertEqual(orders_data[0]["reservation_details"], order_response)


    def test_log_sellout(self):
        """Test logging a sellout event to the CSV."""
        account_name = "observer_acc"
        item_details = {
            "item_id": "item_sold", "display_name": "Sold Out Item",
            "store": {"store_id": "store_X", "store_name": "Store X"},
            "sold_out_at": "2023-01-02T10:00:00Z" # API provided sellout time
        }
        event_type = "SOLD_OUT_POLL"
        
        self.tracker.log_sellout(account_name, item_details, event_type=event_type)
        
        with open(self.test_csv_path, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader) # Skip header
            log_entry = next(reader)
            self.assertEqual(log_entry[1], "store_X")
            self.assertEqual(log_entry[2], "Store X")
            self.assertEqual(log_entry[3], "item_sold")
            self.assertEqual(log_entry[4], "Sold Out Item")
            self.assertEqual(log_entry[5], account_name)
            self.assertEqual(log_entry[6], event_type)
            self.assertEqual(log_entry[7], "2023-01-02T10:00:00Z")

    def test_log_sellout_various_item_details_structure(self):
        """Test log_sellout with slightly different item_details structures."""
        item_details_v1 = { # Item details nested under "item"
            "item": {"item_id": "item_v1", "name": "Item V1 Name"}, # Sometimes "name"
            "display_name": "Item V1 Display Name", # Usually this is present
            "store": {"store_id": "store_v1", "store_name": "Store V1"},
            "sold_out_at": "N/A"
        }
        self.tracker.log_sellout("acc_v1", item_details_v1, "EVENT_V1")
        
        item_details_v2 = { # item_id at top level
            "item_id": "item_v2",
            "display_name": "Item V2",
            "store": {"store_id": "store_v2", "store_name": "Store V2"},
            # No sold_out_at key
        }
        self.tracker.log_sellout("acc_v2", item_details_v2, "EVENT_V2")

        with open(self.test_csv_path, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)
            entry_v1 = next(reader)
            entry_v2 = next(reader)
            
            self.assertEqual(entry_v1[3], "item_v1")
            self.assertEqual(entry_v1[4], "Item V1 Display Name") # display_name takes precedence
            self.assertEqual(entry_v1[7], "N/A")

            self.assertEqual(entry_v2[3], "item_v2")
            self.assertEqual(entry_v2[4], "Item V2")
            self.assertEqual(entry_v2[7], "N/A") # Default if key missing

if __name__ == '__main__':
    unittest.main()
