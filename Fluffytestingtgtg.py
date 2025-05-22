# Fluffytestingtgtg.py
from tgtg import TgtgClient

client = TgtgClient(email="Masonharvill2016@gmail.com")
credentials = client.get_credentials()
print(credentials)