import json
import os
import threading
from tgtg import TgtgClient

# Load credentials from the JR credentials file
with open("credentialsjr.json", "r") as f:
    credentials = json.load(f)

# Debug: Print loaded credentials
print("Loaded credentials:", credentials)

# Initialize the client with the loaded credentials
client = TgtgClient(
    access_token=credentials['access_token'],
    refresh_token=credentials['refresh_token'],
    cookie=credentials['cookie']
)

# The item_id for the Eataly - NYC Downtown (Mixed Grocery Bag)
item_id = "1025230"

# Debug: Print the item_id
print(f"Attempting to reserve item with ID: {item_id}")

# Function to delete the file after 5 minutes
def delete_file_after_delay(file_path, delay):
    def delete_file():
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑️ File {file_path} deleted after {delay} seconds.")
    timer = threading.Timer(delay, delete_file)
    timer.start()

# Attempt to reserve the bag
try:
    # Call create_order with the correct arguments
    response = client.create_order(item_id=item_id, item_count=1)
    print("✅ Successfully reserved the bag!")
    print("Reservation details:", response)

    # Save the order_id to a file
    order_id = response.get("id")
    if order_id:
        file_path = "last_order_id.json"
        with open(file_path, "w") as f:
            json.dump({"order_id": order_id}, f)
        print(f"Order ID saved: {order_id}")

        # Schedule the file for deletion after 5 minutes (300 seconds)
        delete_file_after_delay(file_path, 300)
    else:
        print("❌ Failed to retrieve order ID from the response.")
except Exception as e:
    print("❌ Failed to reserve the bag. Error details:")
    print(str(e))