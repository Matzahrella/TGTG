# testingtgtggideon2.py
from tgtg import TgtgClient

client = TgtgClient(email="masongreyharvill@gmail.com")
credentials = client.get_credentials()
print(credentials)