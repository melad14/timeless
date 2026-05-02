import requests

# Test API endpoints
base_url = "http://localhost:8000/api/v1"

# Test signup
import random
email_suffix = random.randint(1000, 9999)
signup_data = {
    "email": f"test{email_suffix}@example.com",
    "username": f"testuser{email_suffix}",
    "password": "password123"
}

print("Testing signup...")
response = requests.post(f"{base_url}/auth/signup", json=signup_data)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    signup_result = response.json()
    token = signup_result["access_token"]
    print("Signup successful!")

    # Test login
    login_data = {
        "email": signup_data["email"],
        "password": "password123"
    }

    print("\nTesting login...")
    response = requests.post(f"{base_url}/auth/login", json=login_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        login_result = response.json()
        token = login_result["access_token"]
        print("Login successful!")

        headers = {"Authorization": f"Bearer {token}"}

        # Test get current user
        print("\nTesting get current user...")
        response = requests.get(f"{base_url}/users/me", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")

        # Test create time capsule
        print("\nTesting create time capsule...")
        capsule_data = {
            "title": "Test Time Capsule",
            "content": "This is a secret message that will be opened later!",
            "content_type": "text",
            "open_date": "2026-12-25T00:00:00Z"
        }
        response = requests.post(f"{base_url}/time-capsules/", json=capsule_data, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 200:
            capsule = response.json()
            capsule_id = capsule["id"]

            # Test get time capsules
            print("\nTesting get time capsules...")
            response = requests.get(f"{base_url}/time-capsules/", headers=headers)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")

else:
    print(f"Signup failed: {response.text}")