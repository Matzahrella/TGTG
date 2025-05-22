import json
from tgtg import TgtgClient

# Load credentials from the credentials file
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
    "order_id": "9hg389hb0gt11",  # Order ID from the reservation details
    "item_id": "1025230",         # Item ID for the Eataly - NYC Downtown (Mixed Grocery Bag)
    "reserved_at": "2025-05-20T20:17:10.72318863"  # Reservation timestamp
}

# Attempt to abort the reservation
try:
    print(f"🚨 Attempting to abort reservation with Order ID: {reservation_details['order_id']}")
    response = client.abort_order(order_id=reservation_details["order_id"])
    print("✅ Successfully aborted the reservation!")
    print("Cancellation details:", response)
except Exception as e:
    print("❌ Failed to abort the reservation:", str(e))