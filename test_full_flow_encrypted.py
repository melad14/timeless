import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
from bson import ObjectId

# Add the current directory to sys.path to import app
sys.path.append(os.getcwd())

# Load environment variables
load_dotenv()

from app.database import get_database
from app.utils.email import send_capsule_opened_email
from app.security.encryption import encrypt_message

def create_and_notify():
    db = get_database()
    
    # Capsule Details
    user_id = "69f7e79d7c6bd6294829f3a2"
    recipient_email = "miladshehata513@gmail.com"
    title = "Secure Message from the Past | رسالة مشفرة من الماضي"
    raw_content = "This is a SECURE message. It was encrypted and now it is decrypted correctly! 🎉"
    
    # ENCRYPT the content
    encrypted_content = encrypt_message(raw_content)
    
    # Create Capsule in DB with PAST open_date
    past_date = datetime.utcnow() - timedelta(days=1)
    
    capsule_doc = {
        "user_id": ObjectId(user_id),
        "title": title,
        "content": encrypted_content, # SAVE ENCRYPTED CONTENT
        "content_type": "text",
        "open_date": past_date,
        "recipients": [recipient_email],
        "is_opened": True,
        "created_at": datetime.utcnow() - timedelta(days=30),
        "updated_at": datetime.utcnow()
    }
    
    result = db.time_capsules.insert_one(capsule_doc)
    capsule_id = str(result.inserted_id)
    
    print(f"Created encrypted capsule {capsule_id}")
    
    # Send Notification
    success = send_capsule_opened_email([recipient_email], title, capsule_id)
    
    if success:
        print(f"Success! Notification sent to {recipient_email}")
        print(f"ID: {capsule_id}")
    else:
        print("Failed to send email.")

if __name__ == "__main__":
    create_and_notify()
