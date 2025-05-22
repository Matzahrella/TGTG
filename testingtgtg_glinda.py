# testingtgtg_glinda.py
from tgtg import TgtgClient

client = TgtgClient(email="GlindaMoscowitz@proton.me")
credentials = client.get_credentials()
print(credentials)