import unittest
from unittest.mock import patch, MagicMock, call
import subprocess # For subprocess.TimeoutExpired and other constants if needed

# Adjust import path as needed
from core.notifier import Notifier

class TestNotifier(unittest.TestCase):

    def test_init_valid_phone_numbers(self):
        """Test initialization with a valid list of phone numbers."""
        numbers = ["+11234567890", "test@example.com"]
        notifier = Notifier(phone_numbers=numbers)
        self.assertEqual(notifier.phone_numbers, numbers)

    def test_init_empty_phone_numbers_list(self):
        """Test initialization with an empty list of phone numbers."""
        notifier = Notifier(phone_numbers=[])
        self.assertEqual(notifier.phone_numbers, [])

    def test_init_invalid_phone_numbers_type(self):
        """Test initialization with invalid phone_numbers argument types."""
        with self.assertRaisesRegex(ValueError, "phone_numbers must be a list of strings"):
            Notifier(phone_numbers="not_a_list")
        with self.assertRaisesRegex(ValueError, "phone_numbers must be a list of strings"):
            Notifier(phone_numbers=[123, "+11234567890"]) # Contains non-string

    @patch('core.notifier.subprocess.run')
    def test_send_notification_success_single_recipient(self, mock_subprocess_run):
        """Test sending a notification successfully to a single recipient."""
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = "osascript output"
        mock_process.stderr = ""
        mock_subprocess_run.return_value = mock_process
        
        notifier = Notifier(phone_numbers=["+1111111111"])
        message = "Test message!"
        result = notifier.send_notification(message)
        
        self.assertTrue(result)
        expected_script = f'''
                tell application "Messages"
                    set targetService to 1st service whose service type = iMessage
                    set targetBuddy to buddy "{"+1111111111"}" of targetService
                    send "{message}" to targetBuddy
                end tell
                '''
        mock_subprocess_run.assert_called_once_with(
            ["osascript", "-e", expected_script],
            capture_output=True, text=True, check=False, timeout=10
        )

    @patch('core.notifier.subprocess.run')
    def test_send_notification_success_multiple_recipients(self, mock_subprocess_run):
        """Test sending a notification successfully to multiple recipients."""
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_subprocess_run.return_value = mock_process
        
        recipients = ["+111", "test@example.com"]
        notifier = Notifier(phone_numbers=recipients)
        message = "Hello there"
        escaped_message = "Hello there" # No quotes in this message
        
        result = notifier.send_notification(message)
        self.assertTrue(result)
        
        calls = []
        for r in recipients:
            expected_script = f'''
                tell application "Messages"
                    set targetService to 1st service whose service type = iMessage
                    set targetBuddy to buddy "{r}" of targetService
                    send "{escaped_message}" to targetBuddy
                end tell
                '''
            calls.append(call(["osascript", "-e", expected_script], capture_output=True, text=True, check=False, timeout=10))
        
        mock_subprocess_run.assert_has_calls(calls, any_order=False) # Order matters here
        self.assertEqual(mock_subprocess_run.call_count, len(recipients))

    @patch('core.notifier.subprocess.run')
    def test_send_notification_osascript_error(self, mock_subprocess_run):
        """Test handling an error from osascript (non-zero return code)."""
        mock_process = MagicMock()
        mock_process.returncode = 1 # Error
        mock_process.stderr = "AppleScript error: Buddy not found."
        mock_subprocess_run.return_value = mock_process
        
        notifier = Notifier(phone_numbers=["invalid_contact"])
        result = notifier.send_notification("Test")
        
        self.assertFalse(result)
        # Check that it was called once
        self.assertEqual(mock_subprocess_run.call_count, 1)

    @patch('core.notifier.subprocess.run')
    def test_send_notification_osascript_not_found(self, mock_subprocess_run):
        """Test handling FileNotFoundError if osascript is not installed/found."""
        mock_subprocess_run.side_effect = FileNotFoundError("osascript not found")
        
        notifier = Notifier(phone_numbers=["+123"])
        result = notifier.send_notification("Test")
        
        self.assertFalse(result)

    @patch('core.notifier.subprocess.run')
    def test_send_notification_timeout(self, mock_subprocess_run):
        """Test handling TimeoutExpired if osascript hangs."""
        mock_subprocess_run.side_effect = subprocess.TimeoutExpired(cmd="osascript", timeout=10)
        
        notifier = Notifier(phone_numbers=["+123"])
        result = notifier.send_notification("Test")
        
        self.assertFalse(result)

    def test_send_notification_no_recipients(self):
        """Test behavior when no phone numbers are configured."""
        notifier = Notifier(phone_numbers=[])
        # No need to mock subprocess.run as it shouldn't be called
        result = notifier.send_notification("Test")
        self.assertFalse(result)

    @patch('core.notifier.subprocess.run')
    def test_send_notification_message_escaping(self, mock_subprocess_run):
        """Test that double quotes in messages are escaped for AppleScript."""
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_subprocess_run.return_value = mock_process
        
        notifier = Notifier(phone_numbers=["+123"])
        message_with_quotes = 'This is a "test" message.'
        escaped_apple_script_message = "This is a 'test' message." # " replaced by '
        
        notifier.send_notification(message_with_quotes)
        
        expected_script = f'''
                tell application "Messages"
                    set targetService to 1st service whose service type = iMessage
                    set targetBuddy to buddy "{"+123"}" of targetService
                    send "{escaped_apple_script_message}" to targetBuddy
                end tell
                '''
        mock_subprocess_run.assert_called_once_with(
            ["osascript", "-e", expected_script],
            capture_output=True, text=True, check=False, timeout=10
        )
        
    @patch('core.notifier.subprocess.run')
    def test_send_notification_partial_failure(self, mock_subprocess_run):
        """Test when sending to multiple recipients and one fails."""
        success_process = MagicMock()
        success_process.returncode = 0
        
        error_process = MagicMock()
        error_process.returncode = 1
        error_process.stderr = "Error for second recipient"
        
        # First call success, second call error
        mock_subprocess_run.side_effect = [success_process, error_process]
        
        recipients = ["+111", "fail@example.com"]
        notifier = Notifier(phone_numbers=recipients)
        message = "Multi-test"
        
        result = notifier.send_notification(message)
        self.assertFalse(result, "Should return False if any recipient fails")
        self.assertEqual(mock_subprocess_run.call_count, 2)


if __name__ == '__main__':
    unittest.main()
