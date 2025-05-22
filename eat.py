import json
import os
from tgtg import TgtgClient

# Load credentials for the account from the credentials file
with open("credentials.json", "r") as f:
    credentials = json.load(f)

# Initialize the client with the loaded credentials
client = TgtgClient(
    access_token=credentials['access_token'],
    refresh_token=credentials['refresh_token'],
    cookie=credentials['cookie']
)

# Reservation details for the bag
reservation_details = {
    "order_id": "y00mq1avh0ab1",  # Order ID from the reservation details
    "item_id": "1025230",         # Item ID for the Eataly - NYC Downtown (Mixed Grocery Bag)
    "reserved_at": "2025-05-17T20:17:10.879986652"  # Reservation timestamp
}

# Attempt to abort the reservation
try:
    print(f"🚨 Attempting to abort reservation with Order ID: {reservation_details['order_id']}")
    response = client.abort_order(order_id=reservation_details["order_id"])
    print("✅ Successfully aborted the reservation!")
    print("Cancellation details:", response)

    # Optionally, delete the reservation details file if it exists
    file_path = "run_eataly_last_order_id.json"
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"🗑️ File {file_path} deleted.")
except Exception as e:
    print("❌ Failed to abort the reservation:", str(e))