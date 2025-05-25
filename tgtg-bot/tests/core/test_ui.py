import unittest
from unittest.mock import MagicMock, patch
import time

# Adjust import path as needed
from core.ui import CLI_UI
# from rich.panel import Panel # To check instance types
# from rich.table import Table
# from rich.text import Text

# Import placeholder classes for mocking if CLI_UI imports them directly
# from core.account_manager import AccountManager (already mocked)
# from core.scheduler import Scheduler (already mocked)

# Mock TGTGClientWrapper if it were used directly by UI (it's used via placeholder in CLI_UI for now)
# This is to ensure the test file is self-contained if CLI_UI's placeholders are used.
class MockTGTGClientWrapper:
    def __init__(self, creds): self.creds = creds
    def get_favorites(self):
        user_id = self.creds.get("user_id")
        if user_id == "User1_UI":
            return [{"item_id": "ui1", "display_name": "UI Eataly", "items_available": 1, "store": {"store_name": "UI Eataly Store"}, "sold_out_at": None}]
        elif user_id == "User2_UI": # This will be called if the test expects it
            return [{"item_id": "ui2", "display_name": "UI Pizza", "items_available": 0, "store": {"store_name": "UI Pizza Store"}, "sold_out_at": "2023-02-01T10:00:00Z"}]
        return []

class TestCLI_UI(unittest.TestCase):

    def setUp(self):
        """Set up mocks for AccountManager and Scheduler."""
        self.mock_account_manager = MagicMock()
        self.mock_scheduler = MagicMock()

        # Configure common return values for the mocks
        self.mock_account_manager.get_all_account_names.return_value = ["acc1_ui", "acc2_ui"]
        self.mock_account_manager.get_credentials.side_effect = lambda name:             {"user_id": "User1_UI"} if name == "acc1_ui" else             ({"user_id": "User2_UI"} if name == "acc2_ui" else {})
        # Status for User2_UI is "cooldown". The _get_favorites_panel in core.ui.CLI_UI
        # is written to skip fetching for non-active accounts.
        # If the test 'test_get_favorites_panel' now asserts a call for User2_UI,
        # it implies either the CLI_UI logic changed, or the test's expectation is different
        # from CLI_UI's current _get_favorites_panel implementation.
        # For this subtask, I will follow the test code as provided.
        self.mock_account_manager.get_status.side_effect = lambda name:             "active" if name == "acc1_ui" else             ("cooldown" if name == "acc2_ui" else "unknown")
        
        self.mock_scheduler.get_stats.return_value = {"successful_reservations": 5, "active_cooldowns": 1}
        self.mock_scheduler.get_next_poll_time.return_value = time.time() + 120

        self.tgtg_client_patcher = patch('core.ui.TGTGClientWrapper', MockTGTGClientWrapper)
        self.MockTGTGClientClass = self.tgtg_client_patcher.start()


        self.cli_ui = CLI_UI(
            account_manager=self.mock_account_manager,
            scheduler=self.mock_scheduler
        )

    def tearDown(self):
        self.tgtg_client_patcher.stop()


    def test_get_header_panel(self):
        panel = self.cli_ui._get_header_panel()
        self.assertIsNotNone(panel)

    def test_get_account_status_panel(self):
        panel = self.cli_ui._get_account_status_panel()
        self.assertIsNotNone(panel)
        self.mock_account_manager.get_all_account_names.assert_called()
        self.mock_account_manager.get_credentials.assert_any_call("acc1_ui")
        self.mock_account_manager.get_status.assert_any_call("acc2_ui")
        
        if hasattr(self.mock_scheduler, 'active_cooldowns'):
             self.assertEqual(self.mock_scheduler.active_cooldowns, 1)

    def test_get_favorites_panel(self):
        panel = self.cli_ui._get_favorites_panel()
        self.assertIsNotNone(panel)
        self.mock_account_manager.get_all_account_names.assert_called()
        self.MockTGTGClientClass.assert_any_call({'user_id': 'User1_UI'})
        # The CLI_UI._get_favorites_panel as implemented in a previous step
        # only calls TGTGClientWrapper for 'active' accounts.
        # acc2_ui has status 'cooldown'. So, this next assertion might fail
        # if CLI_UI's logic hasn't changed to fetch for non-active users.
        # However, I am implementing the test as provided.
        self.MockTGTGClientClass.assert_any_call({'user_id': 'User2_UI'})
        

    def test_get_footer_panel(self):
        panel = self.cli_ui._get_footer_panel()
        self.assertIsNotNone(panel)
        self.mock_scheduler.get_stats.assert_called_once()
        self.mock_scheduler.get_next_poll_time.assert_called_once()

    def test_update_layout_runs_without_error(self):
        try:
            self.cli_ui._update_layout()
        except Exception as e:
            self.fail(f"_update_layout raised an exception unexpectedly: {e}")
        

if __name__ == '__main__':
    unittest.main()
