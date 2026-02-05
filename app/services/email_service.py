"""Email service for sending OTP verification emails via Gmail SMTP."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings


class EmailService:
    """Service for sending emails using Gmail SMTP."""

    @staticmethod
    def send_otp_email(email: str, otp: str) -> bool:
        """
        Send OTP verification email to user.

        Args:
            email: Recipient email address
            otp: 6-digit OTP code

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["From"] = f"{settings.APP_NAME} <{settings.SMTP_EMAIL}>"
            msg["To"] = email
            msg["Subject"] = f"Your {settings.APP_NAME} Verification Code"

            # Plain text version
            text_content = f"""
Hello!

Your verification code is: {otp}

This code will expire in 5 minutes.

If you didn't request this code, please ignore this email.

Best regards,
{settings.APP_NAME} Team
            """.strip()

            # HTML version
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
        .otp-box {{ background: white; border: 2px solid #667eea; border-radius: 10px; padding: 20px; text-align: center; margin: 20px 0; }}
        .otp-code {{ font-size: 32px; font-weight: bold; color: #667eea; letter-spacing: 8px; }}
        .footer {{ text-align: center; color: #888; font-size: 12px; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💬 {settings.APP_NAME}</h1>
            <p>Email Verification</p>
        </div>
        <div class="content">
            <p>Hello!</p>
            <p>Thank you for registering with {settings.APP_NAME}. Please use the verification code below to complete your registration:</p>
            <div class="otp-box">
                <div class="otp-code">{otp}</div>
            </div>
            <p><strong>This code will expire in 5 minutes.</strong></p>
            <p>If you didn't request this code, please ignore this email.</p>
            <div class="footer">
                <p>Best regards,<br>{settings.APP_NAME} Team</p>
            </div>
        </div>
    </div>
</body>
</html>
            """.strip()

            # Attach both versions
            part1 = MIMEText(text_content, "plain")
            part2 = MIMEText(html_content, "html")
            msg.attach(part1)
            msg.attach(part2)

            # Send email via Gmail SMTP
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(settings.SMTP_EMAIL, settings.SMTP_PASSWORD)
                server.send_message(msg)

            return True

        except Exception as e:
            print(f"Error sending email: {e}")
            return False


email_service = EmailService()
