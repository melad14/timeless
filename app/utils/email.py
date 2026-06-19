import resend
import logging
from app.config import get_settings

logger = logging.getLogger(__name__)


def send_capsule_opened_email(recipients: list[str], capsule_title: str, capsule_id: str) -> bool:
    """Send an email to recipients when a time capsule is opened - using Resend API."""
    settings = get_settings()

    if not settings.resend_api_key:
        logger.warning("Resend API key not configured. Email not sent.")
        return False

    resend.api_key = settings.resend_api_key

    view_link = f"{settings.frontend_url}/view-capsule/{capsule_id}"

    subject = "A Timeless Message for You | رسالة من الماضي"

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
                                    <span style="font-size: 50px;">&#x23F3;</span>
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
                                    <h2 style="color: #333; margin-bottom: 20px; font-size: 24px;">&#x644;&#x642;&#x62F; &#x62D;&#x627;&#x646; &#x627;&#x644;&#x648;&#x642;&#x62A;</h2>
                                    <p style="color: #555; line-height: 1.8; font-size: 16px; margin-bottom: 30px;">
                                        &#x647;&#x646;&#x627;&#x643; &#x631;&#x633;&#x627;&#x644;&#x629; &#x62E;&#x627;&#x635;&#x629; &#x643;&#x627;&#x646;&#x62A; &#x628;&#x627;&#x646;&#x62A;&#x638;&#x627;&#x631;&#x643; &#x641;&#x64A; &#x643;&#x628;&#x633;&#x648;&#x644;&#x62A;&#x646;&#x627; &#x627;&#x644;&#x632;&#x645;&#x646;&#x64A;&#x629;.
                                    </p>
                                </div>

                                <!-- CTA Button -->
                                <div style="margin-top: 20px;">
                                    <a href="{view_link}" style="background-color: #7a0000; color: #ffffff; padding: 18px 40px; text-decoration: none; border-radius: 30px; font-weight: bold; font-size: 16px; display: inline-block; box-shadow: 0 4px 12px rgba(122,0,0,0.3);">
                                        Open Your Message | &#x627;&#x641;&#x62A;&#x62D; &#x631;&#x633;&#x627;&#x644;&#x62A;&#x643;
                                    </a>
                                </div>

                                <p style="color: #999; font-size: 13px; margin-top: 40px;">
                                    If the button does not work, copy and paste this link:<br>
                                    <a href="{view_link}" style="color: #7a0000; text-decoration: underline;">{view_link}</a>
                                </p>
                            </td>
                        </tr>

                        <!-- Footer -->
                        <tr>
                            <td align="center" style="background-color: #f4f4f4; padding: 20px; font-size: 12px; color: #777;">
                                <p style="margin: 5px 0;">2026 Timeless Messaging Platform</p>
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
        email = resend.Emails.send({
            "from": "Timeless <noreply@outlookds.com>",
            "to": recipients,
            "subject": subject,
            "html": body,
        })
        logger.info(f"Email sent via Resend to {len(recipients)} recipients. ID: {email.get('id')}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email via Resend: {str(e)}")
        return False
