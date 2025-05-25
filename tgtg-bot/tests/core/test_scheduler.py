import unittest
from unittest.mock import MagicMock, patch, call
import time # For time-related attributes if needed, though sleep will be mocked

# Adjust import path as needed
from core.scheduler import Scheduler
# Import placeholder/actual classes that Scheduler depends on, to be mocked
# from core.account_manager import AccountManager
# from core.tgtg_client import TGTGClientWrapper
# from core.notifier import Notifier
# from core.sellout_tracker import SelloutTracker

# Default config for scheduler tests
DEFAULT_SCHEDULER_CONFIG = {
    "base_poll_interval_seconds": 0.01, # Very short for testing if we were testing the loop
    "poll_interval_jitter_seconds": 0,
    "captcha_cooldown_hours": 0.001, # Short cooldown
    "max_reservation_attempts": 2,
    "tracked_store_ids_for_sellout": ["store123"], # Corrected from tracked_store_id_for_sellout
    "item_reservation_delay_seconds": [0.01, 0.02] # For retry delay if used
}

class TestSchedulerProcessAccount(unittest.TestCase):

    def setUp(self):
        """Set up mocks for all dependencies of Scheduler."""
        self.mock_account_manager = MagicMock()
        self.mock_notifier = MagicMock()
        self.mock_sellout_tracker = MagicMock()
        
        # Mock TGTGClientWrapper constructor to return a mock instance
        self.MockTGTGClientWrapperConstructor = MagicMock() # Renamed for clarity
        self.mock_tgtg_client_instance = MagicMock()
        self.MockTGTGClientWrapperConstructor.return_value = self.mock_tgtg_client_instance

        self.scheduler = Scheduler(
            account_manager=self.mock_account_manager,
            notifier=self.mock_notifier,
            sellout_tracker=self.mock_sellout_tracker,
            config=DEFAULT_SCHEDULER_CONFIG.copy()
        )
        # Patch TGTGClientWrapper where it's imported by the scheduler module
        self.patcher = patch('core.scheduler.TGTGClientWrapper', self.MockTGTGClientWrapperConstructor)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()


    def test_process_account_active_no_items_available(self):
        """Test _process_account for an active account with no items available."""
        account_name = "acc_active_no_items"
        self.mock_account_manager.get_status.return_value = "active"
        self.mock_account_manager.get_credentials.return_value = {"user_id": "test"}
        self.mock_tgtg_client_instance.get_favorites.return_value = [
            {"item_id": "1", "display_name": "TestBag", "items_available": 0, "store": {"store_name": "TestStore"}}
        ]
        
        self.scheduler._process_account(account_name)
        
        self.mock_account_manager.get_status.assert_called_with(account_name)
        self.mock_account_manager.get_credentials.assert_called_with(account_name)
        self.MockTGTGClientWrapperConstructor.assert_called_once_with({"user_id": "test"})
        self.mock_tgtg_client_instance.get_favorites.assert_called_once()
        self.mock_tgtg_client_instance.create_order.assert_not_called()
        self.mock_notifier.send_notification.assert_not_called()
        self.mock_sellout_tracker.log_reservation.assert_not_called()

    def test_process_account_cooldown_active(self):
        """Test _process_account when account is in active cooldown."""
        account_name = "acc_cooldown"
        self.mock_account_manager.get_status.return_value = "cooldown"
        self.mock_account_manager.check_cooldown.return_value = True # Still in cooldown
        
        self.scheduler._process_account(account_name)
        
        self.mock_account_manager.check_cooldown.assert_called_with(account_name)
        self.mock_account_manager.get_credentials.assert_not_called()
        self.mock_tgtg_client_instance.get_favorites.assert_not_called()

    def test_process_account_cooldown_expired(self):
        """Test _process_account when account cooldown has just expired."""
        account_name = "acc_cooldown_expired"
        # First get_status returns cooldown, then active after check_cooldown
        self.mock_account_manager.get_status.side_effect = ["cooldown", "active"] 
        self.mock_account_manager.check_cooldown.return_value = False # Cooldown finished
        self.mock_account_manager.get_credentials.return_value = {"user_id": "test"}
        self.mock_tgtg_client_instance.get_favorites.return_value = [] # No items for simplicity
        
        self.scheduler._process_account(account_name)
        
        self.mock_account_manager.check_cooldown.assert_called_with(account_name)
        self.mock_account_manager.get_credentials.assert_called_with(account_name)
        self.mock_tgtg_client_instance.get_favorites.assert_called_once()

    def test_process_account_captcha_status(self):
        """Test _process_account when account has CAPTCHA status."""
        account_name = "acc_captcha"
        self.mock_account_manager.get_status.return_value = "captcha"
        # If check_cooldown is called for captcha status and it's still captcha, it won't proceed
        self.mock_account_manager.check_cooldown.return_value = True 
        
        self.scheduler._process_account(account_name)
        
        self.mock_account_manager.get_status.assert_called_with(account_name)
        self.mock_account_manager.check_cooldown.assert_called_with(account_name) # Scheduler calls this
        self.mock_account_manager.get_credentials.assert_not_called()


    def test_process_account_get_favorites_captcha(self):
        """Test _process_account when get_favorites returns CAPTCHA."""
        account_name = "acc_fav_captcha"
        self.mock_account_manager.get_status.return_value = "active"
        self.mock_account_manager.get_credentials.return_value = {"user_id": "test"}
        self.mock_tgtg_client_instance.get_favorites.return_value = {"captcha_detected": True, "error": "captcha!"}
        
        self.scheduler._process_account(account_name)
        
        self.mock_account_manager.set_status.assert_called_with(account_name, "captcha")
        cooldown_seconds = DEFAULT_SCHEDULER_CONFIG["captcha_cooldown_hours"] * 3600
        self.mock_account_manager.set_cooldown.assert_called_with(account_name, cooldown_seconds)

    def test_process_account_item_available_reserve_success(self):
        """Test _process_account item available and reservation is successful."""
        account_name = "acc_reserve_ok"
        item_id_to_reserve = "item123"
        item_details = {
            "item_id": item_id_to_reserve, "display_name": "Super Bag", "items_available": 1,
            "store": {"store_id": "s1", "store_name": "Super Store"}
        }
        # Simulate the structure where item details are nested under "item" key
        api_item_details = {
            "item": {"item_id": item_id_to_reserve},
            "display_name": "Super Bag", "items_available": 1,
            "store": {"store_id": "s1", "store_name": "Super Store"}
        }

        self.mock_account_manager.get_status.return_value = "active"
        self.mock_account_manager.get_credentials.return_value = {"user_id": "test_user"}
        self.mock_tgtg_client_instance.get_favorites.return_value = [api_item_details] # Use API-like structure
        self.mock_tgtg_client_instance.create_order.return_value = {"id": "order_xyz", "state": "RESERVED"}
        
        self.scheduler._process_account(account_name)
        
        self.mock_tgtg_client_instance.create_order.assert_called_once_with(item_id=item_id_to_reserve)
        # Pass the same structure as get_favorites returned
        self.mock_sellout_tracker.log_reservation.assert_called_once_with(account_name, {"id": "order_xyz", "state": "RESERVED"}, api_item_details)
        self.mock_notifier.send_notification.assert_called_once()
        self.mock_notifier.send_notification.assert_called_with(
             f"✅ Reserved Super Bag from Super Store on account {account_name}! Complete payment in TGTG app ASAP. Order ID: order_xyz"
        )


    def test_process_account_item_available_reserve_fail_then_success(self):
        """Test reservation failing first attempt then succeeding."""
        account_name = "acc_reserve_retry"
        item_id_to_reserve = "item_retry"
        item_details = { # This is the structure scheduler will work with internally
            "item_id": item_id_to_reserve, "display_name": "Retry Bag", "items_available": 1,
            "store": {"store_id": "s_retry", "store_name": "Retry Store"}
        }
        api_item_details = { # This is what get_favorites would return
            "item": {"item_id": item_id_to_reserve},
            "display_name": "Retry Bag", "items_available": 1,
            "store": {"store_id": "s_retry", "store_name": "Retry Store"}
        }
        self.mock_account_manager.get_status.return_value = "active"
        self.mock_account_manager.get_credentials.return_value = {"user_id": "retry_user"}
        self.mock_tgtg_client_instance.get_favorites.return_value = [api_item_details]
        self.mock_tgtg_client_instance.create_order.side_effect = [
            {"error": "Temporary glitch"}, # Fails first
            {"id": "order_abc", "state": "RESERVED"} # Succeeds second
        ]
        
        with patch('time.sleep', MagicMock()) as mock_sleep: # Mock time.sleep during retries
            self.scheduler._process_account(account_name)
        
        self.assertEqual(self.mock_tgtg_client_instance.create_order.call_count, 2)
        self.mock_sellout_tracker.log_reservation.assert_called_once()
        self.mock_notifier.send_notification.assert_called_once()
        # Scheduler's internal retry delay is between 1-3s by default.
        # The config "item_reservation_delay_seconds" is not directly used in the current Scheduler code for sleep.
        # If it were, we could assert call with specific values.
        self.assertTrue(mock_sleep.called)


    def test_process_account_item_available_reserve_all_fail(self):
        """Test reservation failing all attempts."""
        account_name = "acc_reserve_fail_all"
        item_id_to_reserve = "item_fail"
        item_details = {
            "item_id": item_id_to_reserve, "display_name": "Fail Bag", "items_available": 1,
            "store": {"store_id": "s_fail", "store_name": "Fail Store"}
        }
        api_item_details = {
            "item": {"item_id": item_id_to_reserve},
            "display_name": "Fail Bag", "items_available": 1,
            "store": {"store_id": "s_fail", "store_name": "Fail Store"}
        }
        self.mock_account_manager.get_status.return_value = "active"
        self.mock_account_manager.get_credentials.return_value = {"user_id": "fail_user"}
        self.mock_tgtg_client_instance.get_favorites.return_value = [api_item_details]
        self.mock_tgtg_client_instance.create_order.return_value = {"error": "Persistent error"}
        
        with patch('time.sleep', MagicMock()):
            self.scheduler._process_account(account_name)
            
        max_attempts = DEFAULT_SCHEDULER_CONFIG["max_reservation_attempts"]
        self.assertEqual(self.mock_tgtg_client_instance.create_order.call_count, max_attempts)
        self.mock_sellout_tracker.log_reservation.assert_not_called()
        self.mock_notifier.send_notification.assert_not_called()
        # If "Persistent error" does not imply sold out, log_sellout might not be called.
        # Current scheduler only logs sellout on "SOLD_OUT" specific strings.
        self.mock_sellout_tracker.log_sellout.assert_not_called()


    def test_process_account_reserve_captcha(self):
        """Test CAPTCHA during reservation attempt."""
        account_name = "acc_reserve_captcha"
        item_id_to_reserve = "item_rc"
        item_details = {
            "item_id": item_id_to_reserve, "display_name": "Reserve CAPTCHA Bag", "items_available": 1,
            "store": {"store_id": "s_rc", "store_name": "RC Store"}
        }
        api_item_details = {
            "item": {"item_id": item_id_to_reserve},
            "display_name": "Reserve CAPTCHA Bag", "items_available": 1,
            "store": {"store_id": "s_rc", "store_name": "RC Store"}
        }
        self.mock_account_manager.get_status.return_value = "active"
        self.mock_account_manager.get_credentials.return_value = {"user_id": "rc_user"}
        self.mock_tgtg_client_instance.get_favorites.return_value = [api_item_details]
        self.mock_tgtg_client_instance.create_order.return_value = {"captcha_detected": True, "error": "captcha at order"}

        self.scheduler._process_account(account_name)
        
        self.mock_tgtg_client_instance.create_order.assert_called_once() 
        self.mock_account_manager.set_status.assert_called_with(account_name, "captcha")
        cooldown_seconds = DEFAULT_SCHEDULER_CONFIG["captcha_cooldown_hours"] * 3600
        self.mock_account_manager.set_cooldown.assert_called_with(account_name, cooldown_seconds)
        self.mock_notifier.send_notification.assert_not_called()


    def test_process_account_tracked_store_sells_out(self):
        """Test logging sellout for a specifically tracked store when items_available is 0."""
        account_name = "acc_tracked_sellout"
        tracked_store_id = DEFAULT_SCHEDULER_CONFIG["tracked_store_ids_for_sellout"][0]
        item_details_tracked_sold_out = {
            "item_id": "tracked_item", # This is the item_id from the item object itself
            "item": {"item_id": "tracked_item"}, # API might nest it
            "display_name": "Tracked Bag Sold Out", "items_available": 0,
            "store": {"store_id": tracked_store_id, "store_name": "Eataly Tracked"},
            "sold_out_at": "2023-01-01T00:00:00Z" 
        }
        self.mock_account_manager.get_status.return_value = "active"
        self.mock_account_manager.get_credentials.return_value = {"user_id": "tracked_user"}
        self.mock_tgtg_client_instance.get_favorites.return_value = [item_details_tracked_sold_out]
        
        self.scheduler._process_account(account_name)
        
        self.mock_sellout_tracker.log_sellout.assert_called_once_with(account_name, item_details_tracked_sold_out)


    def test_process_account_reserve_item_sells_out_during_attempt(self):
        """Test item sells out during reservation attempt (specific error message)."""
        account_name = "acc_sells_out_on_reserve"
        item_id = "item_ghost"
        item_details = { # Structure used by scheduler
            "item_id": item_id, "display_name": "Ghost Bag", "items_available": 1, 
            "store": {"store_id": "s_ghost", "store_name": "Ghost Store"}
        }
        api_item_details = { # Structure from get_favorites
            "item": {"item_id": item_id},
            "display_name": "Ghost Bag", "items_available": 1, 
            "store": {"store_id": "s_ghost", "store_name": "Ghost Store"}
        }
        self.mock_account_manager.get_status.return_value = "active"
        self.mock_account_manager.get_credentials.return_value = {"user_id": "ghost_user"}
        self.mock_tgtg_client_instance.get_favorites.return_value = [api_item_details]
        # First attempt fails with "item sold out"
        self.mock_tgtg_client_instance.create_order.return_value = {"error": "API_ITEM_SOLD_OUT: The item just sold out."} # Common TGTG error

        with patch('time.sleep', MagicMock()): 
            self.scheduler._process_account(account_name)

        self.mock_tgtg_client_instance.create_order.assert_called_once() 
        self.mock_sellout_tracker.log_sellout.assert_called_once_with(account_name, api_item_details)
        self.mock_notifier.send_notification.assert_not_called()


if __name__ == '__main__':
    unittest.main()
