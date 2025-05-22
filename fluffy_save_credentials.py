import json

# Your credentials
credentials = {
    'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDY4Mjg0MDQsImlhdCI6MTc0NjY1NTYwNCwiaXNzIjoidGd0Z19zb3RlcmlhIiwidCI6Ijg2QW1LSlp0U1RPTDM5ZGRwLUVUQnc6MToxIiwic3ViIjoiMTMxNjc4Nzc0ODQ2NTIwNTEzIn0.-eMPbpO7Ca7rNY7HxF8K3pIsMcbYgYTiJ3kE2sqqllQ',
    'refresh_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NzgxOTE2MDQsImlhdCI6MTc0NjY1NTYwNCwiaXNzIjoidGd0Z19zb3RlcmlhIiwidCI6IkkzYTh5VmNMVFJDSzlEWEE3aC1lVEE6MTowIiwic3ViIjoiMTMxNjc4Nzc0ODQ2NTIwNTEzIn0.1HcqpCpNplXsnGM3a7RW8pZlAz8RBGlT629iEgU1Rig',
    'cookie': 'datadome=zAGg1flLoAo0GJT6I~9ow2KE~UKLLmoAJDpoRVRWDdKfH_n66~A1GGGcJgr~T_ZNmIojyWM6kw0hc1syKQV63VgbaNprrkKodfi1KDhW0VOzMuSBz3sUNzuSQT6Cg9AC; Max-Age=5184000; Domain=.apptoogoodtogo.com; Path=/; Secure; SameSite=Lax'
}

# Save credentials to a JSON file
with open("fluffy_credentials.json", "w") as f:
    json.dump(credentials, f)

print("Credentials saved to fluffy_credentials.json")