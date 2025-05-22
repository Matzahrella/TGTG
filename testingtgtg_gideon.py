# test_tgtg_gideon.py
from tgtg import TgtgClient

try:
    client = TgtgClient(email="GideonMoscowitz@gmail.com")
    credentials = client.get_credentials()
    if credentials:
        print("✅ Credentials retrieved successfully:")
        print(credentials)
    else:
        print("❌ No credentials returned.")
except Exception as e:
    print(f"❌ An error occurred: {e}")