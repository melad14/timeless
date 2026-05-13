import requests
from datetime import datetime, timedelta
import time

base_url = "http://localhost:8000/api/v1"

def create_test_capsule():
    # 1. Login/Signup
    signup_data = {
        "email": "test_tester@example.com",
        "username": "tester_official",
        "password": "Password123!",
        "phone_number": "123456789"
    }

    print("--- Getting Token ---")
    response = requests.post(f"{base_url}/auth/login", json={"email": signup_data["email"], "password": signup_data["password"]})
    if response.status_code != 200:
        print("Login failed, trying signup...")
        response = requests.post(f"{base_url}/auth/signup", json=signup_data)
        if response.status_code != 200:
            print(f"Auth failed: {response.text}")
            return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Capsule for user
    # target time: 04:17 local (GMT+3) -> 01:17 UTC
    open_date = "2026-05-13T01:17:00Z"
    
    capsule_data = {
        "title": "اختبار نظام التوقيت - Timeless Test",
        "content": "هذه رسالة اختبار مبرمجة لتصلك في الموعد المحدد. إذا وصلتك فهذا يعني أن النظام يعمل بكفاءة عالية!",
        "content_type": "text",
        "open_date": open_date,
        "recipients": ["miladshehata513@gmail.com"]
    }
    
    print(f"\n--- Creating Test Capsule for {open_date} ---")
    response = requests.post(f"{base_url}/time-capsules", json=capsule_data, headers=headers)
    if response.status_code == 200:
        print("Test capsule created successfully!")
        print(f"Capsule ID: {response.json()['id']}")
    else:
        print(f"Failed to create capsule: {response.text}")

if __name__ == "__main__":
    create_test_capsule()
