from tgtg import TgtgClient

# Initialize the TgtgClient with the new email
client = TgtgClient(email="JoshuaMoscowitz@proton.me")

# Retrieve and print credentials
credentials = client.get_credentials()
print(credentials)