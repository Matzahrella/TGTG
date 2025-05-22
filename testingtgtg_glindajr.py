# testingtgtg_glindajr.py
from tgtg import TgtgClient

client = TgtgClient(email="Glindajrmoscowitz@proton.me")
credentials = client.get_credentials()
print(credentials)