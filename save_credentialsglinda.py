import json

# Glinda account credentials
credentials = {
    'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDY5NzU0MTAsImlhdCI6MTc0NjgwMjYxMCwiaXNzIjoidGd0Z19zb3RlcmlhIiwidCI6InRFZXV3QlZJUmhtNE1RWUZuWFVHN1E6MToxIiwic3ViIjoiMTMyMTcyMjYzODIzMzI1MDU3In0.6T62WMJmhMp6rLyy6kIIewEzmzYmQ3md24cDbKw35eo',
    'refresh_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NzgzMzg2MTAsImlhdCI6MTc0NjgwMjYxMCwiaXNzIjoidGd0Z19zb3RlcmlhIiwidCI6IjFkRGdPWTZhUzZDaUpMNWNMZXg3UEE6MTowIiwic3ViIjoiMTMyMTcyMjYzODIzMzI1MDU3In0.XBcp_jjq7Z9yuYUm7ECr8oMAshWA2IpIuj4f09Cgtxs',
    'cookie': 'datadome=c_na7QciYUBijlJ4xTiEZVMYz3r0FWxWH0LgtCVi1ESR7qP~MfRrVp3pGjqkC6bP11bXjnQtTptSMyFJ~vm9aSZYeroz9qjhbX9efBfTBFWEs~vlC0nf~Vn_FREXvvV5; Max-Age=5184000; Domain=.apptoogoodtogo.com; Path=/; Secure; SameSite=Lax'
}

# Save credentials to a JSON file
with open("glinda_credentials.json", "w") as f:
    json.dump(credentials, f)

print("Credentials saved to glinda_credentials.json")