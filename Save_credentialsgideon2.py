import json

# Gideon2 account credentials
credentials = {
    'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDY5NzM0NjYsImlhdCI6MTc0NjgwMDY2NiwiaXNzIjoidGd0Z19zb3RlcmlhIiwidCI6IjZnLVU5M25hUXN1OGFGTm1qS3pSdGc6MToxIiwic3ViIjoiMTMyMTY1ODk1NzY0MjY4NDgxIn0.6K1Tn4SSnBWvgz2zQ769DYkv7ZgzDNeBQOVQdCoCAI0',
    'refresh_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NzgzMzY2NjYsImlhdCI6MTc0NjgwMDY2NiwiaXNzIjoidGd0Z19zb3RlcmlhIiwidCI6ImZaR2ZjZnJzUWVxVU1EVGJKdnZVdEE6MTowIiwic3ViIjoiMTMyMTY1ODk1NzY0MjY4NDgxIn0.sHpV0o0clxwFkwKWp5sWUvZ2OLqWuNpl3m6_mtWkOUo',
    'cookie': 'datadome=tzcCDy2yTcTnvMYrFuCZIa5IZm8jc5hIUP7aQ_i5fTKl0dS_HZ~zH9oa2HEmF5~RTqvcpXf4_ac8ueol8wgH15oS63CNsrZkUq93HhpEf6i8sXdqdLvl991KGMlr6PTB; Max-Age=5184000; Domain=.apptoogoodtogo.com; Path=/; Secure; SameSite=Lax'
}

# Save credentials to a JSON file
with open("gideon2_credentials.json", "w") as f:
    json.dump(credentials, f)

print("Credentials saved to gideon2_credentials.json")