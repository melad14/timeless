import os
import sys
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from bson import ObjectId

# Add the current directory to sys.path to import app
sys.path.append(os.getcwd())

# Load environment variables
load_dotenv()

from app.database import get_database
from app.security.encryption import encrypt_message

def create_future_capsule():
    db = get_database()
    
    # User ID for Alice (or anyone)
    user_id = "69f7e79d7c6bd6294829f3a2"
    recipient_email = "miladshehata513@gmail.com"
    title = "5-Minute Test | اختبار الـ 5 دقائق"
    raw_content = "This message was automatically sent by the new Timeless Scheduler! It works perfectly. 🎉"
    
    # ENCRYPT the content
    encrypted_content = encrypt_message(raw_content)
    
    # Set open_date to 5 minutes from NOW
    # Use UTC to match the server/scheduler logic
    open_date = datetime.now(timezone.utc) + timedelta(minutes=5)
    
    capsule_doc = {
        "user_id": ObjectId(user_id),
        "title": title,
        "content": encrypted_content,
        "content_type": "text",
        "open_date": open_date, # IN THE FUTURE
        "recipients": [recipient_email],
        "is_opened": False,
        "is_notified": False, # IMPORTANT: The scheduler looks for False
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    
    result = db.time_capsules.insert_one(capsule_doc)
    capsule_id = str(result.inserted_id)
    
    print(f"Created future capsule {capsule_id}")
    print(f"Scheduled for: {open_date} UTC")
    print(f"Recipient: {recipient_email}")
    print(f"The scheduler will check this in its next cycle after {open_date}.")

if __name__ == "__main__":
    create_future_capsule()
