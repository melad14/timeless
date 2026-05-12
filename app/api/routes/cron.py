from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from pymongo.database import Database
import os

from app.database import get_db
from app.utils.email import send_capsule_opened_email

router = APIRouter()

@router.post("/check-capsules")
async def check_capsules(request: Request, background_tasks: BackgroundTasks, db: Database = Depends(get_db)):
    """
    Cron job endpoint to check for capsules that should be opened and notify recipients.
    Securely checks for Vercel Cron Secret.
    """
    # Simple security check for Vercel Cron Jobs
    cron_secret = os.environ.get("CRON_SECRET")
    auth_header = request.headers.get("Authorization")
    
    if cron_secret and auth_header != f"Bearer {cron_secret}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    now = datetime.utcnow()
    
    # Find capsules that reached their open date and haven't been notified yet
    pending_capsules = list(db.time_capsules.find({
        "open_date": {"$lte": now},
        "is_notified": {"$ne": True}
    }))
    
    notified_count = 0
    for capsule in pending_capsules:
        capsule_id = str(capsule["_id"])
        recipients = capsule.get("recipients", [])
        title = capsule.get("title", "A Timeless Message")
        
        if recipients:
            # Send emails in the background
            background_tasks.add_task(
                send_capsule_opened_email,
                recipients,
                title,
                capsule_id
            )
            
            # Update capsule as notified
            db.time_capsules.update_one(
                {"_id": capsule["_id"]},
                {"$set": {"is_notified": True, "updated_at": datetime.utcnow()}}
            )
            notified_count += 1
            
    return {
        "status": "success",
        "processed_capsules": len(pending_capsules),
        "notifications_sent": notified_count
    }
