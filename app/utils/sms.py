import requests
import logging
from app.config import get_settings

logger = logging.getLogger(__name__)


def send_capsule_opened_sms(recipients_phones: list[str], capsule_title: str, capsule_id: str) -> bool:
    """Send an SMS notification to recipients when a time capsule is opened - using httpSMS API."""
    settings = get_settings()

    if not settings.httpsms_api_key or not settings.httpsms_from_phone:
        logger.warning("httpSMS API key or sender phone number not configured. SMS not sent.")
        return False

    url = "https://api.httpsms.com/v1/messages/send"
    
    # We construct a completely link-free message to ensure 100% carrier delivery
    message_content = f"Your Time Capsule '{capsule_title}' is ready! Log in to your Timeless account to view it."
    
    headers = {
        "x-api-key": settings.httpsms_api_key,
        "Content-Type": "application/json"
    }

    success = True
    for phone in recipients_phones:
        # Standardize phone format and handle common typos (like +012... instead of +2012...)
        phone = "".join(c for c in phone if c.isdigit() or c == "+").strip()
        
        if phone.startswith("+"):
            if phone.startswith("+0"):
                # Typo: e.g. +0120... -> +20120...
                phone = "+20" + phone[2:]
        else:
            if phone.startswith("0"):
                # E.g. Egyptian numbers 012... -> +2012...
                phone = "+20" + phone[1:]
            elif phone.startswith("20"):
                phone = "+" + phone
            elif phone.startswith("1") and len(phone) == 10:
                # E.g. 1204... -> +201204...
                phone = "+20" + phone
            else:
                phone = "+" + phone
        
        payload = {
            "from": settings.httpsms_from_phone,
            "to": phone,
            "content": message_content
        }

        try:
            logger.info(f"Sending SMS to {phone} using httpSMS...")
            response = requests.post(url, json=payload, headers=headers)
            res_data = response.json()
            
            if response.status_code in [200, 201] and (res_data.get("status") == "success" or res_data.get("ok") is True):
                logger.info(f"SMS successfully sent to {phone}. Message ID: {res_data.get('data', {}).get('id')}")
            else:
                logger.error(f"Failed to send SMS to {phone}. Response: {res_data}")
                success = False
        except Exception as e:
            logger.error(f"Failed to send SMS to {phone} due to exception: {str(e)}")
            success = False

    return success
