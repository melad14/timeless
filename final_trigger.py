import requests
import time
from datetime import datetime, timezone

# Target times in UTC
TIME_1 = datetime(2026, 5, 13, 1, 36, 45, tzinfo=timezone.utc)
TIME_2 = datetime(2026, 5, 13, 1, 39, 15, tzinfo=timezone.utc)

def run_monitor():
    print("Final Monitor Started...")
    
    for target in [TIME_1, TIME_2]:
        while True:
            now = datetime.now(timezone.utc)
            if now >= target:
                print(f"Time {target} reached! Triggering...")
                try:
                    response = requests.post("https://timeless-lemon.vercel.app/api/v1/time-capsules/check-ready")
                    print(f"Trigger Status: {response.status_code}")
                except Exception as e:
                    print(f"Error: {e}")
                break
            else:
                time.sleep(1)

if __name__ == "__main__":
    run_monitor()
