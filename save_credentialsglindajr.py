import json

# GlindaJR account credentials
credentials = {
    'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDY5NzgyNzIsImlhdCI6MTc0NjgwNTQ3MiwiaXNzIjoidGd0Z19zb3RlcmlhIiwidCI6ImIydXZPcUNhUTlhRnRMQzdHdkpWZ1E6MToxIiwic3ViIjoiMTMyMTc0MzExOTg1ODY1NTM3In0.E_zCIFVHHZAxE68gvOgIZi2mHFnUIUmegz5DCzTh3ic',
    'refresh_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NzgzNDE0NzIsImlhdCI6MTc0NjgwNTQ3MiwiaXNzIjoidGd0Z19zb3RlcmlhIiwidCI6ImdjOEV6RmV0UjNpQldxd1RNVHZVR3c6MTowIiwic3ViIjoiMTMyMTc0MzExOTg1ODY1NTM3In0.sK3PjniYt3k3tdAB82MXx9bI0ZILUEReBJ3pOZhFgTs',
    'cookie': 'datadome=8nrcPUd~Uui_1tXfYvg1S6nuH0_iBXnfJ_q6gKNmCgyU0u7LaLK_NnwP5wqpNnaRfw9jUdEgZYHryN0mGuP21apn89yHLPTD9WFvNQz~D25PjwA9Mws~TE_P1QCKkvWG; Max-Age=5184000; Domain=.apptoogoodtogo.com; Path=/; Secure; SameSite=Lax'
}

# Save credentials to a JSON file
with open("glindajr_credentials.json", "w") as f:
    json.dump(credentials, f)

print("Credentials saved to glindajr_credentials.json")