import unittest
from unittest.mock import patch, MagicMock

# Adjust import path as needed
from core.tgtg_client import TGTGClientWrapper
# from tgtg import TgtgClient # Not directly used in tests, but TGTGClientWrapper uses it

# Sample valid credentials for testing
VALID_CREDS = {
    "access_token": "test_at",
    "refresh_token": "test_rt",
    "cookie": "test_cookie",
    "user_id": "test_user"
}

class TestTGTGClientWrapper(unittest.TestCase):

    @patch('core.tgtg_client.TgtgClient') # Patch where TgtgClient is looked up
    def test_init_valid_credentials(self, MockTgtgClient):
        """Test initialization with valid credentials."""
        mock_client_instance = MockTgtgClient.return_value
        wrapper = TGTGClientWrapper(VALID_CREDS)
        
        MockTgtgClient.assert_called_once_with(
            access_token="test_at",
            refresh_token="test_rt",
            cookie="test_cookie"
        )
        self.assertIsNotNone(wrapper.client)
        self.assertEqual(wrapper.client, mock_client_instance)

    def test_init_missing_credentials(self):
        """Test initialization with missing essential credentials."""
        with self.assertRaisesRegex(ValueError, "Missing one or more credentials"):
            TGTGClientWrapper({"access_token": "at"}) # Missing refresh_token and cookie
        with self.assertRaisesRegex(ValueError, "Missing one or more credentials"):
            TGTGClientWrapper({})

    @patch('core.tgtg_client.TgtgClient')
    def test_get_favorites_success(self, MockTgtgClient):
        """Test get_favorites successful response."""
        mock_tgtg_instance = MockTgtgClient.return_value
        mock_tgtg_instance.get_items.return_value = [{"item_id": "1", "name": "Favorite Bag"}]
        
        wrapper = TGTGClientWrapper(VALID_CREDS)
        response = wrapper.get_favorites()
        
        mock_tgtg_instance.get_items.assert_called_once_with()
        self.assertEqual(response, [{"item_id": "1", "name": "Favorite Bag"}])
        # Ensure it's not mistakenly returning the error dict structure on success
        if isinstance(response, dict):
            self.assertNotIn("captcha_detected", response) 
            self.assertNotIn("error", response) 


    @patch('core.tgtg_client.TgtgClient')
    def test_get_favorites_api_error(self, MockTgtgClient):
        """Test get_favorites handling a generic API error."""
        mock_tgtg_instance = MockTgtgClient.return_value
        mock_tgtg_instance.get_items.side_effect = Exception("API unavailable")
        
        wrapper = TGTGClientWrapper(VALID_CREDS)
        response = wrapper.get_favorites()
        
        self.assertIn("error", response)
        self.assertEqual(response["error"], "API unavailable")
        self.assertFalse(response.get("captcha_detected", False))

    @patch('core.tgtg_client.TgtgClient')
    def test_get_favorites_captcha_error(self, MockTgtgClient):
        """Test get_favorites handling a CAPTCHA error."""
        mock_tgtg_instance = MockTgtgClient.return_value
        # Simulate error message that _is_captcha_error would catch
        mock_tgtg_instance.get_items.side_effect = Exception("CAPTCHA required by server. Forbidden access.") 
        
        wrapper = TGTGClientWrapper(VALID_CREDS)
        response = wrapper.get_favorites()
        
        self.assertTrue(response.get("captcha_detected"))
        self.assertIn("error", response)
        self.assertIn("CAPTCHA required", response["error"]) # Check if original error message is preserved

    @patch('core.tgtg_client.TgtgClient')
    def test_create_order_success(self, MockTgtgClient):
        """Test create_order successful response."""
        mock_tgtg_instance = MockTgtgClient.return_value
        mock_tgtg_instance.create_order.return_value = {"order_id": "order123", "status": "RESERVED"}
        
        wrapper = TGTGClientWrapper(VALID_CREDS)
        response = wrapper.create_order(item_id="item_1", quantity=1)
        
        mock_tgtg_instance.create_order.assert_called_once_with(item_id="item_1", quantity=1)
        self.assertEqual(response, {"order_id": "order123", "status": "RESERVED"})

    @patch('core.tgtg_client.TgtgClient')
    def test_create_order_api_error(self, MockTgtgClient):
        """Test create_order handling a generic API error."""
        mock_tgtg_instance = MockTgtgClient.return_value
        mock_tgtg_instance.create_order.side_effect = Exception("Order failed: Out of stock")
        
        wrapper = TGTGClientWrapper(VALID_CREDS)
        response = wrapper.create_order(item_id="item_2")
        
        self.assertIn("error", response)
        self.assertEqual(response["error"], "Order failed: Out of stock")
        self.assertFalse(response.get("captcha_detected", False))

    @patch('core.tgtg_client.TgtgClient')
    def test_create_order_captcha_error(self, MockTgtgClient):
        """Test create_order handling a CAPTCHA error."""
        mock_tgtg_instance = MockTgtgClient.return_value
        mock_tgtg_instance.create_order.side_effect = Exception("Forbidden: CAPTCHA challenge")
        
        wrapper = TGTGClientWrapper(VALID_CREDS)
        response = wrapper.create_order(item_id="item_3")
        
        self.assertTrue(response.get("captcha_detected"))
        self.assertIn("error", response)
        self.assertIn("Forbidden: CAPTCHA challenge", response["error"])

    @patch('core.tgtg_client.TgtgClient') # Need to patch TgtgClient even if not directly used by the method itself,
                                     # because the constructor of TGTGClientWrapper uses it.
    def test_is_captcha_error(self, MockTgtgClient):
        """Test the internal _is_captcha_error logic with various messages."""
        # MockTgtgClient is patched to allow instantiation of TGTGClientWrapper
        wrapper = TGTGClientWrapper(VALID_CREDS) 
        
        self.assertTrue(wrapper._is_captcha_error("Error: CAPTCHA required."))
        self.assertTrue(wrapper._is_captcha_error("A challenge is required to proceed."))
        self.assertTrue(wrapper._is_captcha_error("Human verification needed."))
        self.assertTrue(wrapper._is_captcha_error("Access denied due to security policy: captcha_IDENTIFIED"))
        self.assertTrue(wrapper._is_captcha_error("403 Forbidden - please solve CAPTCHA")) # Based on added keyword
        
        self.assertFalse(wrapper._is_captcha_error("Item not available."))
        self.assertFalse(wrapper._is_captcha_error("Network error."))
        self.assertFalse(wrapper._is_captcha_error("500 Internal Server Error"))

    @patch('core.tgtg_client.TgtgClient')
    def test_refresh_access_token_success(self, MockTgtgClient):
        """Test refresh_access_token when underlying library handles it (simulated by no error)."""
        mock_tgtg_instance = MockTgtgClient.return_value
        
        original_access_token = VALID_CREDS["access_token"]
        new_access_token = "new_test_at"
        new_cookie = "new_test_cookie"

        # Set initial token values on the mock client instance
        mock_tgtg_instance.access_token = original_access_token 
        mock_tgtg_instance.cookie = VALID_CREDS["cookie"]

        wrapper = TGTGClientWrapper(VALID_CREDS) # Initialized with old token

        # Configure the mock client to update its attributes when get_items is called,
        # as if an internal refresh happened and updated these.
        def side_effect_get_items(*args, **kwargs):
            mock_tgtg_instance.access_token = new_access_token
            mock_tgtg_instance.cookie = new_cookie
            return [{"item_id": "light_call_item"}] # Return value for get_items
        
        mock_tgtg_instance.get_items.side_effect = side_effect_get_items
        
        result = wrapper.refresh_access_token()

        self.assertTrue(result)
        mock_tgtg_instance.get_items.assert_called_once_with(favorites_only=True, page_size=1)
        # Check if the wrapper's stored tokens were updated
        self.assertEqual(wrapper.access_token, new_access_token)
        self.assertEqual(wrapper.cookie, new_cookie)


    @patch('core.tgtg_client.TgtgClient')
    def test_refresh_access_token_failure(self, MockTgtgClient):
        """Test refresh_access_token when the light API call fails (not CAPTCHA)."""
        mock_tgtg_instance = MockTgtgClient.return_value
        mock_tgtg_instance.get_items.side_effect = Exception("Authentication failed persistently")
        
        wrapper = TGTGClientWrapper(VALID_CREDS)
        result = wrapper.refresh_access_token()
        
        self.assertFalse(result) # Expect False for non-CAPTCHA errors

    @patch('core.tgtg_client.TgtgClient')
    def test_refresh_access_token_captcha(self, MockTgtgClient):
        """Test refresh_access_token when the light API call hits a CAPTCHA."""
        mock_tgtg_instance = MockTgtgClient.return_value
        mock_tgtg_instance.get_items.side_effect = Exception("CAPTCHA challenge during refresh check")
        
        wrapper = TGTGClientWrapper(VALID_CREDS)
        result = wrapper.refresh_access_token()
        
        self.assertIsInstance(result, dict)
        self.assertTrue(result.get("captcha_detected"))
        self.assertIn("CAPTCHA challenge", result.get("error", ""))

if __name__ == '__main__':
    unittest.main()
