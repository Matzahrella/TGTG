from tgtg import TgtgClient

client = TgtgClient(email="gideonjrmoscowitz@gmail.com")
credentials = client.get_credentials()
print(credentials)