import json

# Your credentials
credentials = {
    'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDY2NDc4OTEsImlhdCI6MTc0NjQ3NTA5MSwiaXNzIjoidGd0Z19zb3RlcmlhIiwidCI6ImtyWE42ZFR6UzlPZWJoc1J4N25LMXc6MToxIiwic3ViIjoiOTYyNDYxNjQyNjI4NzA0NjUifQ.SqDDGq4NSq-xjmAylv-huhS7dhZeDqGcCswNMsjJUuI',
    'refresh_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NzgwMTEwOTEsImlhdCI6MTc0NjQ3NTA5MSwiaXNzIjoidGd0Z19zb3RlcmlhIiwidCI6Im9TM0EzZlJyUVI2MDliRlQydlRSMkE6MTowIiwic3ViIjoiOTYyNDYxNjQyNjI4NzA0NjUifQ.hCqWyx2tiHF9rqi6_15SmSuWZceKVldLV7aOcNBFEso',
    'cookie': 'datadome=d1nn~Sno6TUyo8JbS~PvFlMYBANyC5rh6zG3YMuyPeMFOdRkiap8mgblWpLLq8R7Us2FC0LYf21W1QlYSRRh_gr_5Ryl~aNPX6~RgoLLcBKPf7rZnJf3C2cDx_z6d9c6; Max-Age=5184000; Domain=.apptoogoodtogo.com; Path=/; Secure; SameSite=Lax'
}

# Save credentials to a JSON file
with open("credentials.json", "w") as f:
    json.dump(credentials, f)

print("Credentials saved to credentials.json")