import sys
from app import app
from services.db import fetch_one

print("Testing App Initialization...")

client = app.test_client()

routes_to_test = [
    ('/', 200),
    ('/login', 200),
    ('/register', 200),
    ('/eligibility', 200),
]

for route, expected_status in routes_to_test:
    try:
        response = client.get(route)
        print(f"GET {route} -> Status Code: {response.status_code}")
        if response.status_code != expected_status:
            print(f"ERROR on {route}: Expected {expected_status}, got {response.status_code}")
    except Exception as e:
        print(f"EXCEPTION on {route}: {e}")
