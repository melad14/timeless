import requests
from datetime import datetime, timezone, timedelta

# Production URL
base_url = "https://timeless-lemon.vercel.app/api/v1"

def create_live_test():
    # 1. Login/Signup (on live)
    signup_data = {
        "email": "live_tester_final@example.com",
        "username": "live_tester_final",
        "password": "Password123!",
        "phone_number": "123456789"
    }

    print("--- Getting Token from Live Backend ---")
    try:
        response = requests.post(f"{base_url}/auth/login", json={"email": signup_data["email"], "password": signup_data["password"]})
        if response.status_code != 200:
            print("Login failed, trying signup...")
            response = requests.post(f"{base_url}/auth/signup", json=signup_data)
    except Exception as e:
        print(f"Connection error: {e}")
        return

    if response.status_code != 200:
        print(f"Auth failed: {response.text}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Capsule (Live)
    # Target: 04:36:30 local -> 01:36:30 UTC
    open_date = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat().replace("+00:00", "Z")
    
    capsule_data = {
        "title": "اختبار مباشر - Live Production Test",
        "content": "هذا اختبار حي للنظام بعد الرفع على Vercel وربط GitHub Actions. النظام يعمل بكفاءة 100%!",
        "content_type": "text",
        "open_date": open_date,
        "recipients": ["miladshehata513@gmail.com"]
    }
    
    print(f"\n--- Creating Live Capsule for {open_date} ---")
    response = requests.post(f"{base_url}/time-capsules", json=capsule_data, headers=headers)
    if response.status_code == 200:
        capsule_id = response.json()['id']
        print(f"Live capsule created! ID: {capsule_id}")
        return capsule_id
    else:
        print(f"Failed to create capsule: {response.text}")
        return None

if __name__ == "__main__":
    create_live_test()
