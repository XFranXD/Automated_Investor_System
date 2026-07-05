import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email_alert(subject, body):
    """
    Sends a secure SMTP email alert using Gmail servers.
    Reads credentials from:
    - EMAIL_SENDER
    - EMAIL_RECEIVER
    - EMAIL_APP_PASSWORD
    """
    sender = os.getenv("EMAIL_SENDER")
    receiver = os.getenv("EMAIL_RECEIVER")
    password = os.getenv("EMAIL_APP_PASSWORD")
    
    if not sender or not receiver or not password:
        print("Warning: Notification credentials missing (EMAIL_SENDER, EMAIL_RECEIVER, EMAIL_APP_PASSWORD).")
        print("Skipping email delivery. Printing alert to console:")
        print(f"\n[ALERT SUBJECT] {subject}\n[ALERT BODY]\n{body}\n")
        return False
        
    try:
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = receiver
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Connect via SSL to Gmail's SMTP server
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as server:
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())
            
        print(f"Alert email successfully delivered to {receiver}.")
        return True
    except Exception as e:
        print(f"Failed to deliver SMTP alert: {e}")
        return False
