"""WhatsApp sending routes using Selenium (unofficial, for local use only)."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.api.dependencies import get_current_active_user
from app.models import User
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])


class WhatsAppMessage(BaseModel):
    phone: str  # Phone number with country code, e.g. +966500000000
    message: str


def send_whatsapp_message(phone: str, message: str) -> bool:
    """Send WhatsApp message using Selenium (unofficial method)."""
    try:
        # Setup Chrome driver
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # Run in background
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        # Open WhatsApp Web
        driver.get("https://web.whatsapp.com/")

        # Wait for QR code scan (manual step - user needs to scan QR in browser)
        print("Please scan the QR code in the browser to log in to WhatsApp Web.")
        WebDriverWait(driver, 300).until(
            EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='10']"))
        )

        # Construct WhatsApp URL for the number
        whatsapp_url = f"https://web.whatsapp.com/send?phone={phone}&text={message.replace(' ', '%20')}"
        driver.get(whatsapp_url)

        # Wait for the chat to load
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='10']"))
        )

        # Click send button
        send_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='compose-btn-send']"))
        )
        send_button.click()

        # Wait a bit for sending
        time.sleep(2)

        driver.quit()
        return True

    except Exception as e:
        print(f"Error sending WhatsApp: {e}")
        return False


@router.post("/send", status_code=status.HTTP_200_OK)
def send_whatsapp(
    whatsapp_data: WhatsAppMessage,
    current_user: User = Depends(get_current_active_user),
):
    """Send WhatsApp message (unofficial, local use only)."""
    success = send_whatsapp_message(whatsapp_data.phone, whatsapp_data.message)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send WhatsApp message"
        )
    return {"message": "WhatsApp sent successfully"}