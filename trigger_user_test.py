import requests
import time
from datetime import datetime, timezone

# Target time: 2026-05-13 01:17:00 UTC (04:17 Local)
TARGET_TIME_UTC = datetime(2026, 5, 13, 1, 17, 0, tzinfo=timezone.utc)

def run_scheduler():
    print(f"Scheduler started. Waiting for {TARGET_TIME_UTC}...")
    
    while True:
        now = datetime.now(timezone.utc)
        if now >= TARGET_TIME_UTC:
            print(f"Time reached! ({now}) Triggering check-ready...")
            try:
                response = requests.post("http://localhost:8000/api/v1/time-capsules/check-ready")
                print(f"Trigger Status: {response.status_code}")
                print(f"Response: {response.json()}")
                break
            except Exception as e:
                print(f"Error triggering: {e}")
                time.sleep(5) # Retry in 5 seconds
        else:
            diff = (TARGET_TIME_UTC - now).total_seconds()
            if diff > 60:
                print(f"Still waiting... {int(diff)} seconds remaining.")
                time.sleep(60)
            else:
                print(f"Getting close! {int(diff)} seconds remaining.")
                time.sleep(1)

if __name__ == "__main__":
    run_scheduler()
