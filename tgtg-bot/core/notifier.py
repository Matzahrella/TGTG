import subprocess
import shlex # Not strictly needed with the current subprocess.run approach but good for other contexts.

class Notifier:
    def __init__(self, phone_numbers):
        """
        Initializes the Notifier with a list of target phone numbers.
        Args:
            phone_numbers (list): A list of strings, where each string is a phone number or iMessage email.
        """
        if not isinstance(phone_numbers, list) or not all(isinstance(pn, str) for pn in phone_numbers):
            raise ValueError("phone_numbers must be a list of strings.")
        self.phone_numbers = phone_numbers

    def send_notification(self, message):
        """
        Sends a message to all configured phone numbers/emails via iMessage.
        Args:
            message (str): The message string to send.
        Returns:
            bool: True if all messages were attempted successfully (osascript return code 0), False otherwise.
        """
        if not self.phone_numbers:
            print("Notifier: No phone numbers configured. Cannot send notification.")
            return False

        # Basic sanitization for the message to prevent breaking AppleScript syntax.
        # Replace double quotes with single quotes for the message content within AppleScript.
        # More robust escaping might be needed for complex messages.
        escaped_message = message.replace('"', "'") # Simple quote swap

        all_successful = True
        for target_contact in self.phone_numbers:
            # Sanitize contact - AppleScript is sensitive. For now, assume valid format.
            escaped_target_contact = target_contact.replace('"', "'")

            try:
                applescript_command = f'''
                tell application "Messages"
                    set targetService to 1st service whose service type = iMessage
                    set targetBuddy to buddy "{escaped_target_contact}" of targetService
                    send "{escaped_message}" to targetBuddy
                end tell
                '''
                
                cmd = ["osascript", "-e", applescript_command]
                
                print(f"Notifier: Attempting to send message to {target_contact}: '{message}'")
                result = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=10) # Added timeout

                if result.returncode != 0:
                    print(f"Notifier: Error sending iMessage to {target_contact}. Return code: {result.returncode}")
                    print(f"Notifier: STDOUT: {result.stdout.strip()}")
                    print(f"Notifier: STDERR: {result.stderr.strip()}")
                    all_successful = False
                else:
                    # osascript returning 0 doesn't guarantee message delivery or that the contact was valid,
                    # but that the script itself executed without error.
                    print(f"Notifier: osascript command executed successfully for {target_contact}.")
                    
            except FileNotFoundError:
                print("Notifier: Error: 'osascript' command not found. Ensure you are on macOS with Messages app configured.")
                all_successful = False
                break 
            except subprocess.TimeoutExpired:
                print(f"Notifier: Timeout expired while trying to send message to {target_contact}.")
                all_successful = False
            except Exception as e:
                print(f"Notifier: An unexpected error occurred while sending iMessage to {target_contact}: {e}")
                all_successful = False
        
        return all_successful

# Example Usage (for testing purposes, will only work on macOS)
# if __name__ == '__main__':
#     print("Notifier Test Script (macOS only)")
#     
#     # IMPORTANT: Replace with actual phone numbers or iMessage emails for testing.
#     # Be careful not to spam! Use your own number for testing.
#     test_contacts = ["your_imessage_email@example.com"] # Replace with your valid iMessage-enabled contact
#     
#     if test_contacts[0] == "your_imessage_email@example.com" and len(test_contacts) == 1:
#         print("Notifier: Please replace placeholder contacts in the test script to actually send messages.")
#         print("Notifier: To test, add your own iMessage email or phone number to the 'test_contacts' list.")
#     else:
#         try:
#             notifier = Notifier(phone_numbers=test_contacts) # phone_numbers can be emails too for iMessage
#             test_message = "🚨 Test TGTG Notification from Bot: Item Reserved! (Test)"
#             
#             print(f"Notifier: Attempting to send: '{test_message}' to {test_contacts}")
#             success = notifier.send_notification(test_message)
#             
#             if success:
#                 print("Notifier: Test message command(s) executed. Check Messages app on macOS and recipient device(s).")
#             else:
#                 print("Notifier: Failed to execute osascript command for one or more contacts.")
#
#         except ValueError as ve:
#             print(f"Notifier Test Error: {ve}")
#         except Exception as e:
#             print(f"Notifier Test: An unexpected error occurred: {e}")
