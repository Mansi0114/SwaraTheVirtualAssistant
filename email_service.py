"""
Email sending module for Swara.
Supports SMTP-based secure email sending with app-specific passwords.
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(recipient, subject, body, sender_email=None, sender_password=None):
    """
    Send an email via SMTP.
    
    Args:
        recipient: Email address of recipient
        subject: Email subject
        body: Email body
        sender_email: Sender's email (defaults to EMAIL_ADDRESS from .env)
        sender_password: Sender's app password (defaults to EMAIL_PASSWORD from .env)
    
    Returns:
        str: Status message
    """
    try:
        # Load credentials from environment if not provided
        if not sender_email:
            sender_email = os.getenv('EMAIL_ADDRESS')
        if not sender_password:
            sender_password = os.getenv('EMAIL_PASSWORD')
        
        if not sender_email or not sender_password:
            return "Email credentials not configured. Set EMAIL_ADDRESS and EMAIL_PASSWORD in .env"
        
        # Get SMTP settings from environment
        smtp_server = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('EMAIL_SMTP_PORT', 587))
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()
            return f"Email sent successfully to {recipient}."
        except smtplib.SMTPAuthenticationError:
            return "Email authentication failed. Check your credentials."
        except smtplib.SMTPException as e:
            return f"SMTP error: {e}"
    except Exception as e:
        return f"Error sending email: {e}"


def compose_email_draft(recipient, subject="", body=""):
    """
    Opens default mail client for composing an email.
    
    Args:
        recipient: Email address of recipient
        subject: Email subject
        body: Email body
    """
    import webbrowser
    try:
        # URL-encode the body and subject for safe URL passing
        from urllib.parse import quote
        subject_encoded = quote(subject)
        body_encoded = quote(body)
        mailto_link = f"mailto:{recipient}?subject={subject_encoded}&body={body_encoded}"
        webbrowser.open(mailto_link)
        return "Opened mail client to compose email."
    except Exception as e:
        return f"Unable to open mail client: {e}"
