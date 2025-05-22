import json
from tgtg import TgtgClient

# Load credentials from the GlindaJR credentials file
with open("glindajr_credentials.json", "r") as f:
    credentials = json.load(f)

# Initialize the client with the loaded credentials
client = TgtgClient(
    access_token=credentials['access_token'],
    refresh_token=credentials['refresh_token'],
    cookie=credentials['cookie']
)

# Fetch and display favorite stores
favorites = client.get_favorites()

print("Your Favorite Stores (GlindaJR Account):")
for store in favorites:
    # Debug: Print the full store object to inspect its structure
    print("DEBUG: Store object:", store)

    # Safely access keys with .get() to avoid KeyError
    display_name = store.get('display_name', 'Unknown Store')
    store_id = store.get('store_id', 'Unknown ID')

    print(f"- {display_name} (Store ID: {store_id})")