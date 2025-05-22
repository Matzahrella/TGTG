import json

# Your new credentials
credentials = {
    'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDY4MTYyMDksImlhdCI6MTc0NjY0MzQwOSwiaXNzIjoidGd0Z19zb3RlcmlhIiwidCI6IlZxRlRnWFlIUTRpWHAzak44dFEtNEE6MToxIiwic3ViIjoiMTMxNjM4MjAyOTcyNzA0MzUzIn0.NbdmbgsfVk-WuR_g_mgoqMrmcbzetuiHVbLd89Fgg8c',
    'refresh_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NzgxNzk0MDksImlhdCI6MTc0NjY0MzQwOSwiaXNzIjoidGd0Z19zb3RlcmlhIiwidCI6IlRHWHlnMnBJU3RDb003MHJCVnZWOXc6MTowIiwic3ViIjoiMTMxNjM4MjAyOTcyNzA0MzUzIn0.5eExig52TWHEWnesnM6zuWAa1YBC7ZJUyUFPA4j0UTA',
    'cookie': 'datadome=SZqxG3nsCE906~OzxbiNFF9n5P_ZRuNgV9ZyaAfXbKjCllts0gBNIrXWy4Va8SsZ1~b1ZlXAm3vwRFiNzWQcZ8vtuRhGl~xyMZPNe1TebEclr8JrBVUC0nS5tzC6GvbV; Max-Age=5184000; Domain=.apptoogoodtogo.com; Path=/; Secure; SameSite=Lax'
}

# Save credentials to a JSON file
with open("new_credentials.json", "w") as f:
    json.dump(credentials, f)

print("Credentials saved to new_credentials.json")