import unittest
import os
import json
import time
import shutil # For cleaning up test directories

# Adjust import path based on how tests will be run.
# If running 'python -m unittest discover tgtg-bot/tests' from project root:
from core.account_manager import AccountManager 
# If tests directory is added to PYTHONPATH or using a test runner that handles it:
# from tgtg_bot.core.account_manager import AccountManager 

class TestAccountManager(unittest.TestCase):

    def setUp(self):
        """Set up a temporary accounts directory for each test."""
        self.test_accounts_dir = "test_temp_accounts_dir"
        # Ensure it's clean before each test
        if os.path.exists(self.test_accounts_dir):
            shutil.rmtree(self.test_accounts_dir)
        os.makedirs(self.test_accounts_dir, exist_ok=True)
        
        self.account_manager = AccountManager(accounts_dir=self.test_accounts_dir)

    def tearDown(self):
        """Clean up the temporary accounts directory after each test."""
        if os.path.exists(self.test_accounts_dir):
            shutil.rmtree(self.test_accounts_dir)

    def _create_account_creds(self, account_name, credentials):
        """Helper to create a credentials.json file for a test account."""
        account_path = os.path.join(self.test_accounts_dir, account_name)
        os.makedirs(account_path, exist_ok=True)
        with open(os.path.join(account_path, "credentials.json"), 'w') as f:
            json.dump(credentials, f)

    def test_load_accounts_valid(self):
        """Test loading valid account credentials."""
        creds1 = {"user_id": "user1", "access_token": "at1", "refresh_token": "rt1", "cookie": "c1"}
        creds2 = {"user_id": "user2", "access_token": "at2", "refresh_token": "rt2", "cookie": "c2"}
        self._create_account_creds("acc1", creds1)
        self._create_account_creds("acc2", creds2)
        
        self.account_manager.load_accounts()
        
        self.assertEqual(len(self.account_manager.get_all_account_names()), 2)
        self.assertEqual(self.account_manager.get_credentials("acc1"), creds1)
        self.assertEqual(self.account_manager.get_status("acc1"), "active")
        self.assertEqual(self.account_manager.get_credentials("acc2"), creds2)
        self.assertEqual(self.account_manager.get_status("acc2"), "active")

    def test_load_accounts_missing_credentials_file(self):
        """Test behavior when an account folder is present but credentials.json is missing."""
        os.makedirs(os.path.join(self.test_accounts_dir, "acc_no_creds"), exist_ok=True)
        
        creds_valid = {"user_id": "user_valid", "access_token": "atv", "refresh_token": "rtv", "cookie": "cv"}
        self._create_account_creds("acc_valid", creds_valid)

        self.account_manager.load_accounts()
        
        # Only the account with credentials should be loaded
        self.assertEqual(len(self.account_manager.get_all_account_names()), 1)
        self.assertIsNotNone(self.account_manager.get_credentials("acc_valid"))
        self.assertIsNone(self.account_manager.get_credentials("acc_no_creds")) # Or check it's not in all_account_names

    def test_load_accounts_corrupted_credentials_file(self):
        """Test behavior with a corrupted (invalid JSON) credentials.json."""
        account_path = os.path.join(self.test_accounts_dir, "acc_corrupted")
        os.makedirs(account_path, exist_ok=True)
        with open(os.path.join(account_path, "credentials.json"), 'w') as f:
            f.write("this is not json")
            
        creds_valid = {"user_id": "user_valid", "access_token": "atv", "refresh_token": "rtv", "cookie": "cv"}
        self._create_account_creds("acc_valid", creds_valid)

        self.account_manager.load_accounts()
        
        self.assertEqual(len(self.account_manager.get_all_account_names()), 1)
        self.assertIsNotNone(self.account_manager.get_credentials("acc_valid"))
        # Account with corrupted JSON should be skipped

    def test_load_accounts_empty_accounts_dir(self):
        """Test loading when the accounts directory is empty."""
        self.account_manager.load_accounts()
        self.assertEqual(len(self.account_manager.get_all_account_names()), 0)

    def test_load_accounts_non_dict_credentials(self):
        """Test credentials.json that contains a list instead of a dict."""
        account_path = os.path.join(self.test_accounts_dir, "acc_list_creds")
        os.makedirs(account_path, exist_ok=True)
        with open(os.path.join(account_path, "credentials.json"), 'w') as f:
            json.dump([1, 2, 3], f) # JSON is a list

        self.account_manager.load_accounts()
        self.assertNotIn("acc_list_creds", self.account_manager.get_all_account_names())


    def test_status_management(self):
        """Test setting and getting account status."""
        creds = {"user_id": "user_status", "access_token": "ats", "refresh_token": "rts", "cookie": "cs"}
        self._create_account_creds("status_test_acc", creds)
        self.account_manager.load_accounts()
        
        self.assertEqual(self.account_manager.get_status("status_test_acc"), "active")
        
        self.account_manager.set_status("status_test_acc", "cooldown")
        self.assertEqual(self.account_manager.get_status("status_test_acc"), "cooldown")
        
        self.account_manager.set_status("status_test_acc", "captcha")
        self.assertEqual(self.account_manager.get_status("status_test_acc"), "captcha")

        self.account_manager.set_status("status_test_acc", "active")
        self.assertEqual(self.account_manager.get_status("status_test_acc"), "active")

    def test_cooldown_logic(self):
        """Test account cooldown functionality."""
        creds = {"user_id": "user_cooldown", "access_token": "atc", "refresh_token": "rtc", "cookie": "cc"}
        account_name = "cooldown_acc"
        self._create_account_creds(account_name, creds)
        self.account_manager.load_accounts()

        # Set cooldown for 0.1 seconds for quick testing
        cooldown_duration_seconds = 0.1
        self.account_manager.set_cooldown(account_name, cooldown_duration_seconds)
        
        self.assertEqual(self.account_manager.get_status(account_name), "cooldown")
        self.assertTrue(self.account_manager.check_cooldown(account_name), "Account should be in cooldown immediately after setting")

        # Wait for cooldown to expire
        time.sleep(cooldown_duration_seconds + 0.05) # Add a small buffer

        self.assertFalse(self.account_manager.check_cooldown(account_name), "Cooldown should have expired")
        self.assertEqual(self.account_manager.get_status(account_name), "active", "Status should reset to active after cooldown expires")
        self.assertNotIn(account_name, self.account_manager.cooldown_timers, "Cooldown timer should be cleared")

    def test_check_cooldown_on_active_account(self):
        """Test check_cooldown on an account that is not in cooldown."""
        creds = {"user_id": "user_active", "access_token": "ata", "refresh_token": "rta", "cookie": "ca"}
        account_name = "active_acc"
        self._create_account_creds(account_name, creds)
        self.account_manager.load_accounts()

        self.assertEqual(self.account_manager.get_status(account_name), "active")
        self.assertFalse(self.account_manager.check_cooldown(account_name))
        self.assertEqual(self.account_manager.get_status(account_name), "active") # Status should remain active

    def test_get_non_existent_account_status(self):
        """Test getting status for an account that doesn't exist."""
        self.assertIsNone(self.account_manager.get_status("non_existent_acc"))
        
    def test_get_non_existent_account_credentials(self):
        """Test getting credentials for an account that doesn't exist."""
        self.assertIsNone(self.account_manager.get_credentials("non_existent_acc"))

    def test_set_status_on_non_existent_account(self):
        """Test setting status for an account that doesn't exist (should ideally not error, maybe log)."""
        # The current implementation would create a new entry in account_status.
        # This might be desired or not. For now, test current behavior.
        self.account_manager.set_status("non_existent_status_acc", "active")
        self.assertEqual(self.account_manager.get_status("non_existent_status_acc"), "active")


if __name__ == '__main__':
    unittest.main()
