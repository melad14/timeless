from app.database import get_database
from datetime import datetime
import sys

# Set output to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

def check_db():
    db = get_database()
    capsules = list(db.time_capsules.find().sort("created_at", -1).limit(5))
    print(f"Total capsules checked: {len(capsules)}")
    for c in capsules:
        print(f"ID: {c['_id']}")
        print(f"Title: {c.get('title', 'N/A')}")
        print(f"Recipients: {c.get('recipients', [])}")
        print(f"Open Date: {c.get('open_date')} (UTC)")
        print(f"Is Opened: {c.get('is_opened')}")
        print(f"Is Notified: {c.get('is_notified', False)}")
        print(f"Created At: {c.get('created_at')}")
        print("-" * 20)

if __name__ == "__main__":
    check_db()
