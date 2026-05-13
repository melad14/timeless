import requests
from datetime import datetime, timezone, timedelta

base_url = "https://timeless-lemon.vercel.app/api/v1"

def create_email_test():
    signup_data = {
        "email": "email_tester_live@example.com",
        "username": "email_tester_live",
        "password": "Password123!",
        "phone_number": "123456789"
    }

    print("--- Getting Token ---")
    response = requests.post(f"{base_url}/auth/login", json={"email": signup_data["email"], "password": signup_data["password"]})
    if response.status_code != 200:
        requests.post(f"{base_url}/auth/signup", json=signup_data)
        response = requests.post(f"{base_url}/auth/login", json={"email": signup_data["email"], "password": signup_data["password"]})
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Target: 04:39:00 local -> 01:39:00 UTC (approx 5 mins from now)
    open_date = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat().replace("+00:00", "Z")
    
    capsule_data = {
        "title": "اختبار البريد الإلكتروني - Email Delivery Test",
        "content": "هذا اختبار حي لنظام البريد الإلكتروني. المجدول الآلي يعمل الآن كل 5 دقائق!",
        "content_type": "text",
        "open_date": open_date,
        "recipients": ["miladshehata513@gmail.com"]
    }
    
    print(f"\n--- Creating Email Test Capsule for {open_date} ---")
    response = requests.post(f"{base_url}/time-capsules", json=capsule_data, headers=headers)
    if response.status_code == 200:
        print(f"Email test capsule created! ID: {response.json()['id']}")
    else:
        print(f"Failed to create capsule: {response.text}")

if __name__ == "__main__":
    create_email_test()
