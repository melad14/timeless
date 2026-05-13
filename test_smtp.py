import smtplib
from email.mime.text import MIMEText
from app.config import get_settings

def test_smtp():
    settings = get_settings()
    print(f"Testing SMTP with user: {settings.smtp_user}")
    
    msg = MIMEText("This is a test email from Timeless Backend.")
    msg['Subject'] = "Timeless SMTP Test"
    msg['From'] = settings.smtp_from_email
    msg['To'] = "miladshehata513@gmail.com"
    
    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)
        print("SMTP Test: SUCCESS")
    except Exception as e:
        print(f"SMTP Test: FAILED - {e}")

if __name__ == "__main__":
    test_smtp()
