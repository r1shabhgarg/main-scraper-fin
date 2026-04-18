import requests
import json
import time

url = "http://localhost:8000/events/search"
payload = {"query": "hackathons in Bangalore"}

print(f"Testing {url}...")
start = time.time()
try:
    resp = requests.post(url, json=payload)
    print(f"Status: {resp.status_code}")
    print(json.dumps(resp.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
print(f"Time taken: {time.time() - start:.2f} seconds")
