from app.database import get_database
from app.utils.email import send_capsule_opened_email
import sys

sys.stdout.reconfigure(encoding='utf-8')

def retry_notifications():
    db = get_database()
    capsules = list(db.time_capsules.find({"is_opened": True, "is_notified": {"$ne": True}}))
    print(f"Found {len(capsules)} capsules needing notification.")
    
    for c in capsules:
        recipients = c.get("recipients", [])
        if recipients:
            print(f"Processing capsule: {c['_id']} to {recipients}")
            success = send_capsule_opened_email(recipients, c.get("title", "No Title"), str(c["_id"]))
            if success:
                db.time_capsules.update_one({"_id": c["_id"]}, {"$set": {"is_notified": True}})
                print("Email sent and marked as notified.")
            else:
                print("Failed to send email.")
        else:
            # Mark as notified if no recipients to avoid checking again
            db.time_capsules.update_one({"_id": c["_id"]}, {"$set": {"is_notified": True}})
            print(f"Capsule {c['_id']} has no recipients. Marked as notified.")

if __name__ == "__main__":
    retry_notifications()
