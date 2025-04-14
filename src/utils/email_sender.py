"""
Email Sender Module for SmartBrew Email Automation System
Handles sending of individual and bulk emails
"""

import smtplib
import os
import uuid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import pandas as pd
from typing import List, Dict, Optional, Union
from pathlib import Path
import streamlit as st
import time
from streamlit.runtime.uploaded_file_manager import UploadedFile

def send_email(
    sender_email: str,
    sender_password: str,
    recipient: Dict[str, str],
    subject: str,
    body: str,
    cc_email: Optional[str] = None,
    attachment_path: Optional[str] = None,
    executive_name: Optional[str] = None,
    executive_number: Optional[str] = None
) -> str:
    """
    Sends an email using SMTP with optional attachment.
    
    Args:
        sender_email: Sender's email address
        sender_password: Sender's app password
        recipient: Dictionary containing recipient details (Email, Name)
        subject: Email subject
        body: Email body
        cc_email: Optional CC email address
        attachment_path: Optional path to attachment file
        executive_name: Optional sender's name for signature
        executive_number: Optional sender's contact number
    
    Returns:
        str: Success or error message
    """
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        
        # Set basic headers
        msg["From"] = f"{executive_name} <{sender_email}>" if executive_name else sender_email
        msg["To"] = f"{recipient.get('Name', '')} <{recipient['Email']}>" if recipient.get('Name') else recipient['Email']
        msg["Subject"] = subject
        
        # Add essential email headers
        msg.add_header('Message-ID', f"<{uuid.uuid4()}@smartbrew.in>")
        msg.add_header('Date', datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0530"))
        
        if cc_email:
            msg["Cc"] = cc_email
        
        # Add physical address and unsubscribe link to reduce spam score
        footer = """

--
About KHUSHII:
KHUSHII (Kinship for Humanitarian Social and Holistic Intervention in India) is an independent, not-for-profit organization founded in 2003 by a group of dedicated philanthropists. With 21 years of on-ground experience, KHUSHII operates across 13 states in India, committed to driving positive change and ensuring that no child is left behind.

Kindly have a look at our website at www.khushii.org, we will be more than happy to assist you or provide any further information if required.

Registration Number: S/47900/20034  
Unique Registration Number: AAATK6911AF20210  
FCRA Registration Number: 231660833  
Recognized by: Central Government, State Governments, Regulatory Bodies

This email was sent to {recipient_email}. 
To unsubscribe, please reply with "Unsubscribe" in the subject line.
""".format(recipient_email=recipient['Email'])

        # Format message with recipient name
        formatted_message = body
        if '{name}' in formatted_message:
            if recipient.get('Name') and recipient['Name'].lower() != 'unknown':
                formatted_message = formatted_message.replace('{name}', recipient['Name'])
            else:
                formatted_message = formatted_message.replace('Dear {name},', 'Dear Ma\'am,')
        
        # Replace executive name placeholder
        if '{Executive Name}' in formatted_message and executive_name:
            formatted_message = formatted_message.replace('{Executive Name}', executive_name)
        
        # Replace executive number placeholder
        if '{Executive Number}' in formatted_message and executive_number:
            formatted_message = formatted_message.replace('{Executive Number}', executive_number)
        
        # Add footer to message
        formatted_message += footer
        
        # Add plain text version
        part1 = MIMEText(formatted_message, 'plain')
        msg.attach(part1)
        
        # Create HTML version for better deliverability
        html_body = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{subject}</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto;">
    <div style="padding: 20px;">
        {formatted_message.replace('{', '{{').replace('}', '}}').replace('{{recipient_email}}', recipient['Email']).replace('\n', '<br>')}
    </div>
    <div style="padding: 15px; border-top: 1px solid #ddd; font-size: 12px; color: #777;">
        <p>If you're seeing this email for the first time, please add {sender_email} to your contacts to ensure future communications don't go to spam.</p>
    </div>
</body>
</html>"""
        
        # Add HTML version
        part2 = MIMEText(html_body, 'html')
        msg.attach(part2)
        
        # Add attachment if provided
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(attachment_path)}")
                msg.attach(part)
        
        # Send email
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        
        # Get all recipients (including CC)
        all_recipients = [recipient['Email']]
        if cc_email:
            all_recipients.append(cc_email)
        
        server.sendmail(sender_email, all_recipients, msg.as_string())
        server.quit()
        
        return f"✅ Email sent to {recipient['Email']}"
    
    except Exception as e:
        return f"❌ Error sending email to {recipient['Email']}: {str(e)}"

def send_bulk_emails(
    sender_email: str,
    app_password: str,
    recipients_file: UploadedFile,
    subject: str,
    message: str,
    cc_email: str = None,
    attachment_path: str = None,
    executive_name: str = None,
    executive_number: str = None
) -> dict:
    """
    Send bulk emails to recipients from a CSV file.
    
    Args:
        sender_email (str): Sender's email address
        app_password (str): App-specific password
        recipients_file (UploadedFile): Streamlit uploaded file object containing recipient details
        subject (str): Email subject
        message (str): Email message body
        cc_email (str, optional): CC email address
        attachment_path (str, optional): Path to attachment file
        executive_name (str, optional): Executive name for signature
        executive_number (str, optional): Executive contact number
        
    Returns:
        dict: Dictionary containing success count, failed count, and last email sent
    """
    try:
        # Read the CSV file from the uploaded file object
        df = pd.read_csv(recipients_file)
        
        # Validate required columns
        required_columns = ['Email', 'Name']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns in CSV: {', '.join(missing_columns)}")
        
        # Initialize counters
        success_count = 0
        failed_count = 0
        last_email = None
        
        # Process each recipient
        for _, row in df.iterrows():
            try:
                # Create recipient dictionary
                recipient = {
                    'Email': row['Email'],
                    'Name': row['Name']
                }
                
                # Send email to current recipient using keyword arguments
                result = send_email(
                    sender_email=sender_email,
                    sender_password=app_password,
                    recipient=recipient,
                    subject=subject,
                    body=message,
                    cc_email=cc_email,
                    attachment_path=attachment_path,
                    executive_name=executive_name,
                    executive_number=executive_number
                )
                
                if result.startswith('✅'):
                    success_count += 1
                    last_email = recipient['Email']
                else:
                    failed_count += 1
                    print(result)  # Print error message
                
                # Add delay between emails to avoid rate limiting
                time.sleep(2)
                
            except Exception as e:
                print(f"Error sending email to {row['Email']}: {str(e)}")
                failed_count += 1
        
        return {
            'success_count': success_count,
            'failed_count': failed_count,
            'last_email': last_email
        }
        
    except Exception as e:
        raise Exception(f"Error processing bulk emails: {str(e)}") 