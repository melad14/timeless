import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)

def send_capsule_opened_email(recipients: list[str], capsule_title: str, capsule_id: str):
    """Send an email to recipients when a time capsule is opened."""
    settings = get_settings()
    
    if not settings.smtp_user or not settings.smtp_password:
        logger.warning("SMTP credentials not configured. Email not sent.")
        return False

    view_link = f"{settings.frontend_url}/view-capsule/{capsule_id}"
    
    subject = f"A Timeless Message for You: {capsule_title}"
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
            <h2 style="color: #6a11cb;">Timeless Message</h2>
            <p>Hello,</p>
            <p>Someone has left a special message for you in a <strong>Timeless Time Capsule</strong>.</p>
            <p>The time has come to open it: <strong>"{capsule_title}"</strong></p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{view_link}" style="background-color: #6a11cb; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold;">View Your Message</a>
            </div>
            <p>If the button above doesn't work, copy and paste this link into your browser:</p>
            <p><a href="{view_link}">{view_link}</a></p>
            <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
            <p style="font-size: 0.8em; color: #777;">This is an automated message from Timeless App. Please do not reply.</p>
        </div>
    </body>
    </html>
    """

    try:
        msg = MIMEMultipart()
        msg['From'] = settings.smtp_from_email
        msg['To'] = ", ".join(recipients)
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'html'))
        
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)
            
        logger.info(f"Email sent successfully to {len(recipients)} recipients.")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False
