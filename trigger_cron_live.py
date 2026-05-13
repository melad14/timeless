import requests
import json

def trigger_cron():
    url = "https://timeless-lemon.vercel.app/api/v1/cron/check-capsules"
    print(f"Triggering cron at {url}...")
    
    try:
        response = requests.post(url)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    trigger_cron()
