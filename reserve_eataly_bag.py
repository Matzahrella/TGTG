import json
from tgtg import TgtgClient

# Load credentials from the saved file
with open("credentials.json", "r") as f:
    credentials = json.load(f)

# Initialize the client with the loaded credentials
client = TgtgClient(
    access_token=credentials['access_token'],
    refresh_token=credentials['refresh_token'],
    cookie=credentials['cookie']
)

# The item_id for the Eataly - NYC Downtown (Mixed Grocery Bag)
item_id = "1025230"

# Attempt to reserve the bag
try:
    # Call create_order with the correct arguments
    response = client.create_order(item_id=item_id, item_count=1)
    print("✅ Successfully reserved the bag!")
    print("Reservation details:", response)
    # Print the full response for debugging
    print("Reservation details (raw):", response)
except Exception as e:
    print("❌ Failed to reserve the bag:", str(e))