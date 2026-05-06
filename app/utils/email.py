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
    
    subject = f"✨ A Timeless Message for You | رسالة من الماضي"
    
    body = f"""
    <html>
    <body style="margin: 0; padding: 0; background-color: #f9f6f2; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="table-layout: fixed; background-color: #f9f6f2;">
            <tr>
                <td align="center" style="padding: 40px 0;">
                    <table border="0" cellpadding="0" cellspacing="0" width="600" style="background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08);">
                        <!-- Header -->
                        <tr>
                            <td align="center" style="background: linear-gradient(135deg, #7a0000 0%, #4a0000 100%); padding: 40px 20px;">
                                <h1 style="color: #ffffff; margin: 0; font-size: 28px; letter-spacing: 2px;">TIMELESS</h1>
                                <p style="color: #ffcccc; margin: 10px 0 0 0; font-size: 14px; text-transform: uppercase;">Preserving Moments Forever</p>
                            </td>
                        </tr>
                        
                        <!-- Content -->
                        <tr>
                            <td style="padding: 40px; text-align: center;">
                                <div style="margin-bottom: 30px;">
                                    <span style="font-size: 50px;">⏳</span>
                                </div>
                                
                                <h2 style="color: #333; margin-bottom: 20px; font-size: 24px;">The Time Has Come</h2>
                                <p style="color: #555; line-height: 1.8; font-size: 16px; margin-bottom: 30px;">
                                    A special message has been waiting for you in our time capsule. 
                                    The date set for its release has finally arrived.
                                </p>
                                
                                <div style="background-color: #fdf2f2; border-radius: 12px; padding: 25px; margin-bottom: 35px; border: 1px dashed #7a0000;">
                                    <p style="margin: 0; color: #7a0000; font-weight: bold; font-size: 18px;">
                                        "{capsule_title}"
                                    </p>
                                </div>

                                <!-- Arabic Version -->
                                <div dir="rtl" style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee;">
                                    <h2 style="color: #333; margin-bottom: 20px; font-size: 24px;">لقد حان الوقت</h2>
                                    <p style="color: #555; line-height: 1.8; font-size: 16px; margin-bottom: 30px;">
                                        هناك رسالة خاصة كانت بانتظارك في كبسولتنا الزمنية.
                                        لقد وصل أخيراً الموعد المحدد لفتحها.
                                    </p>
                                </div>
                                
                                <!-- CTA Button -->
                                <div style="margin-top: 20px;">
                                    <a href="{view_link}" style="background-color: #7a0000; color: #ffffff; padding: 18px 40px; text-decoration: none; border-radius: 30px; font-weight: bold; font-size: 16px; display: inline-block; box-shadow: 0 4px 12px rgba(122,0,0,0.3);">
                                        Open Your Message | افتح رسالتك
                                    </a>
                                </div>
                                
                                <p style="color: #999; font-size: 13px; margin-top: 40px;">
                                    If the button doesn't work, copy and paste this link:<br>
                                    <a href="{view_link}" style="color: #7a0000; text-decoration: underline;">{view_link}</a>
                                </p>
                            </td>
                        </tr>
                        
                        <!-- Footer -->
                        <tr>
                            <td align="center" style="background-color: #f4f4f4; padding: 20px; font-size: 12px; color: #777;">
                                <p style="margin: 5px 0;">© 2026 Timeless Messaging Platform</p>
                                <p style="margin: 5px 0;">This is an automated delivery. Please do not reply to this email.</p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
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
