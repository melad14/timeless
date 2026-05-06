import requests
import random
import time
from datetime import datetime, timedelta

base_url = "http://localhost:8000/api/v1"

def test_flow():
    # 1. Signup/Login
    email_suffix = random.randint(1000, 9999)
    signup_data = {
        "email": f"test{email_suffix}@example.com",
        "username": f"testuser{email_suffix}",
        "password": "Password123!", # password validation requires uppercase, digit, etc.
        "phone_number": "123456789"
    }

    print("--- Testing Signup ---")
    response = requests.post(f"{base_url}/auth/signup", json=signup_data)
    if response.status_code != 200:
        print(f"Signup failed: {response.text}")
        return

    print("Signup successful!")
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Time Capsule with recipients
    print("\n--- Testing Create Time Capsule with Recipients ---")
    # Set open_date to 5 seconds from now for testing
    open_date = (datetime.utcnow() + timedelta(seconds=5)).isoformat() + "Z"
    capsule_data = {
        "title": "Future Message for Children",
        "content": "This is a message from the past. I love you!",
        "content_type": "text",
        "open_date": open_date,
        "recipients": ["child1@example.com", "child2@example.com"]
    }
    
    response = requests.post(f"{base_url}/time-capsules", json=capsule_data, headers=headers)
    if response.status_code != 200:
        print(f"Create capsule failed: {response.text}")
        return
    
    capsule = response.json()
    capsule_id = capsule["id"]
    print(f"Capsule created with ID: {capsule_id}")
    print(f"Recipients: {capsule.get('recipients')}")

    # 3. Try to view via shared link (should fail before open date)
    print("\n--- Testing Shared Link (Before Open Date) ---")
    response = requests.get(f"{base_url}/shared-capsules/{capsule_id}")
    print(f"Status (Expected 403): {response.status_code}")
    if response.status_code == 403:
        print("Successfully blocked access before open date.")
    else:
        print(f"ERROR: Access should have been blocked, but got {response.status_code}")

    # 4. Wait for open date and trigger check-ready
    print(f"\nWaiting 6 seconds for open date ({open_date})...")
    time.sleep(6)

    print("\n--- Triggering check-ready ---")
    response = requests.post(f"{base_url}/time-capsules/check-ready")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

    # 5. Try to view via shared link (should succeed now)
    print("\n--- Testing Shared Link (After Open Date & Check-Ready) ---")
    response = requests.get(f"{base_url}/shared-capsules/{capsule_id}")
    print(f"Status (Expected 200): {response.status_code}")
    if response.status_code == 200:
        shared_capsule = response.json()
        print("Successfully accessed shared capsule!")
        print(f"Decrypted Content: {shared_capsule['content']}")
        if shared_capsule['content'] == capsule_data['content']:
            print("Content matches correctly!")
        else:
            print("ERROR: Content mismatch!")
    else:
        print(f"ERROR: Failed to access shared capsule: {response.text}")

    # 6. Test Sent folder optimized endpoint
    print("\n--- Testing Sent Folder Endpoint ---")
    response = requests.get(f"{base_url}/messages/user/sent", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        sent_messages = response.json()
        print(f"Found {len(sent_messages)} sent messages.")
    else:
        print(f"ERROR: Failed to fetch sent messages: {response.text}")

if __name__ == "__main__":
    try:
        test_flow()
    except Exception as e:
        print(f"Test failed with error: {e}")
