import json
import os
from tgtg import TgtgClient

# Load credentials from the new session file
with open("new_credentials.json", "r") as f:
    credentials = json.load(f)

# Initialize the client with the loaded credentials
client = TgtgClient(
    access_token=credentials['access_token'],
    refresh_token=credentials['refresh_token'],
    cookie=credentials['cookie']
)

# Load the order_id from the file
try:
    with open("last_order_id.json", "r") as f:
        data = json.load(f)
        order_id = data.get("order_id")
        if not order_id:
            raise ValueError("Order ID not found in the file.")
except FileNotFoundError:
    print("❌ No order ID file found. Please reserve a bag first.")
    exit(1)
except Exception as e:
    print(f"❌ Failed to load order ID: {e}")
    exit(1)

# Attempt to abort the reservation
try:
    # Call the abort_order method with the correct order_id
    response = client.abort_order(order_id=order_id)
    print("✅ Successfully aborted the reservation!")
    print("Cancellation details:", response)

    # Delete the file after successfully aborting the reservation
    os.remove("last_order_id.json")
    print("🗑️ Order ID file deleted.")
except Exception as e:
    print("❌ Failed to abort the reservation:", str(e))