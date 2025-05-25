from tgtg import TgtgClient

class TGTGClientWrapper:
    def __init__(self, account_credentials):
        """
        Initializes the TGTG client with account credentials.
        account_credentials should be a dictionary like the one loaded from credentials.json.
        """
        self.access_token = account_credentials.get("access_token")
        self.refresh_token = account_credentials.get("refresh_token")
        self.cookie = account_credentials.get("cookie")
        self.user_id = account_credentials.get("user_id") # Not directly used by TgtgClient constructor but good to have
        
        if not all([self.access_token, self.refresh_token, self.cookie]):
            raise ValueError("Missing one or more credentials (access_token, refresh_token, cookie)")
            
        self.client = TgtgClient(
            access_token=self.access_token,
            refresh_token=self.refresh_token,
            cookie=self.cookie
            # The TgtgClient might also take user_agent, language, etc.
            # For now, we stick to the core credentials.
        )

    def get_favorites(self):
        """
        Fetches the favorite items for the account.
        Returns a list of favorite items or an error/CAPTCHA dictionary.
        Handles potential API errors and CAPTCHA detection.
        """
        try:
            # get_items() by default gets favorites if no item_ids list is provided
            items = self.client.get_items() 
            return items
        except Exception as e:
            error_message = str(e)
            print(f"Error fetching favorites: {error_message}")
            if self._is_captcha_error(error_message):
                return {"captcha_detected": True, "error": error_message}
            return {"error": error_message}

    def create_order(self, item_id, quantity=1):
        """
        Attempts to create an order for a given item_id.
        Returns the order response dictionary or an error/CAPTCHA dictionary.
        Handles potential API errors and CAPTCHA detection.
        """
        try:
            # Ensure item_id is a string as per TgtgClient expectations (if any, good practice)
            order_response = self.client.create_order(item_id=str(item_id), quantity=quantity)
            return order_response
        except Exception as e:
            error_message = str(e)
            print(f"Error creating order for item {item_id}: {error_message}")
            if self._is_captcha_error(error_message):
                return {"captcha_detected": True, "error": error_message}
            return {"error": error_message}

    def _is_captcha_error(self, error_message):
        """
        Checks if the error message indicates a CAPTCHA challenge.
        This needs to be refined based on actual TGTG API responses for CAPTCHAs.
        """
        captcha_keywords = ["captcha", "challenge required", "human verification", "forbidden", "403"] # Added "forbidden" and "403" as common indicators
        error_message_lower = error_message.lower()
        for keyword in captcha_keywords:
            if keyword in error_message_lower:
                return True
        return False

    def refresh_access_token(self):
        """
        Refreshes the access token using the refresh_token.
        The tgtg-python library aims to handle this automatically.
        This method primarily serves to check token validity by making a light API call.
        It updates the client's and instance's access_token and cookie upon success if new ones are issued.
        Returns True if successful/valid, False for persistent auth errors, 
        or a dict for CAPTCHA.
        """
        try:
            # Making a light API call to check token validity and trigger auto-refresh if needed.
            # The library should update self.client.access_token and self.client.cookie internally if refreshed.
            current_access_token = self.client.access_token # Store before call
            
            self.client.get_items(favorites_only=True, page_size=1) # Light API call
            
            # If the token was refreshed by the library, update our instance variables
            if self.client.access_token != current_access_token:
                self.access_token = self.client.access_token
                self.cookie = self.client.cookie # Cookie might also change with token refresh
                print("Access token and cookie were refreshed by the library.")
            
            return True # If it doesn't throw an auth error, tokens are likely fine or refreshed.
        except Exception as e:
            error_message = str(e)
            print(f"Error during token refresh or validity check: {error_message}")
            if self._is_captcha_error(error_message):
                return {"captcha_detected": True, "error": error_message}
            # Consider specific exceptions for authentication failure if distinguishable
            return False

# Example Usage (for testing purposes, can be in a separate test file or under if __name__ == '__main__')
# if __name__ == '__main__':
#     # This requires a valid credentials.json in a known location or mocked data
#     # For demonstration, let's assume you have placeholder credentials
#     placeholder_creds = {
#       "access_token": "test_access_token", # Replace with a real one for actual testing
#       "refresh_token": "test_refresh_token", # Replace with a real one
#       "cookie": "test_cookie", # Replace with a real one
#       "user_id": "test_user_id"
#     }
#     
#     # Test case 1: Initialization
#     print("--- Test Case 1: Initialization ---")
#     try:
#         client_wrapper = TGTGClientWrapper(placeholder_creds)
#         print("Client wrapper initialized successfully.")
#     except ValueError as ve:
#         print(f"Initialization error: {ve}")
#         # Exit if initialization fails, as other tests depend on it
#         exit()
#     except Exception as e:
#         print(f"An unexpected error occurred during initialization: {e}")
#         exit()
#
#     # Test case 1.1: Initialization with missing credentials
#     print("\\n--- Test Case 1.1: Initialization with missing credentials ---")
#     missing_creds = {"access_token": "test"}
#     try:
#         client_wrapper_fail = TGTGClientWrapper(missing_creds)
#         print("Client wrapper initialized with missing creds (should have failed).")
#     except ValueError as ve:
#         print(f"Successfully caught initialization error for missing creds: {ve}")
#     
#     # Note: The following calls would fail or not work as expected without actual 
#     # valid credentials and potentially mocking the TgtgClient calls.
#     # These are placeholders for how one might structure tests.
#
#     # print("\\n--- Test Case 2: Get Favorites ---")
#     # print("Attempting to get favorites...")
#     # favorites = client_wrapper.get_favorites()
#     # if isinstance(favorites, dict) and favorites.get("captcha_detected"):
#     #     print(f"CAPTCHA detected while fetching favorites: {favorites.get('error')}")
#     # elif isinstance(favorites, dict) and "error" in favorites:
#     #     print(f"Error getting favorites: {favorites['error']}")
#     # else:
#     #     print(f"Favorites: {favorites if favorites else 'No favorites found or empty list.'}")
#
#     # print("\\n--- Test Case 3: Create Order (Bogus Item) ---")
#     # print("Attempting to create an order for a bogus item...")
#     # order_response = client_wrapper.create_order("00000") # Bogus item_id
#     # if isinstance(order_response, dict) and order_response.get("captcha_detected"):
#     #     print(f"CAPTCHA detected while creating order: {order_response.get('error')}")
#     # elif isinstance(order_response, dict) and "error" in order_response:
#     #     print(f"Error creating order: {order_response['error']}")
#     # else:
#     #     print(f"Order response: {order_response}")
#
#     print("\\n--- Test Case 4: CAPTCHA Error Simulation ---")
#     print("Simulating CAPTCHA error string check:")
#     captcha_messages = [
#         "Forbidden: CAPTCHA required.",
#         "Access denied due to human verification challenge.",
#         "Error 403: Suspicious activity detected.",
#         "This is a normal application error."
#     ]
#     for msg in captcha_messages:
#         is_captcha = client_wrapper._is_captcha_error(msg)
#         print(f"Message: '{msg}' -> Is CAPTCHA? {is_captcha}")
#
#     # print("\\n--- Test Case 5: Refresh Access Token ---")
#     # print("Attempting to refresh access token (simulated by light API call)...")
#     # refresh_status = client_wrapper.refresh_access_token()
#     # if isinstance(refresh_status, dict) and refresh_status.get("captcha_detected"):
#     #     print(f"CAPTCHA detected during token refresh attempt: {refresh_status.get('error')}")
#     # elif refresh_status:
#     #     print("Token refresh/check successful (or library handled it).")
#     #     print(f"  New access token (first 10 chars): {client_wrapper.access_token[:10]}...")
#     #     print(f"  New cookie (first 10 chars): {client_wrapper.cookie[:10]}...")
#     # else:
#     #     print("Token refresh/check failed (persistent auth error).")
#
#     print("\\n--- All placeholder tests complete ---")
