# test_tgtg.py
from tgtg import TgtgClient

client = TgtgClient(email="hvcloudcam@gmail.com")
credentials = client.get_credentials()
print(credentials)