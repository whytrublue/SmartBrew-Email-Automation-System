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
from typing import List, Dict, Optional, Union, Tuple
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
    attachment_paths: Optional[List[Union[str, Tuple[str, str]]]] = None,
    executive_name: Optional[str] = None,
    executive_number: Optional[str] = None,
    executive_gender: Optional[str] = None
) -> str:
    """
    Sends an email using SMTP with optional attachments.

    Args:
        sender_email: Sender's email address
        sender_password: Sender's app password
        recipient: Dictionary containing recipient details (Email, Name)
        subject: Email subject
        body: Email body
        cc_email: Optional CC email address
        attachment_paths: Optional list of attachment paths. Each item can be either:
                            - A string (path)
                            - A tuple (path, original_filename)
        executive_name: Optional sender's name for signature
        executive_number: Optional sender's contact number
        executive_gender: Optional sender's gender ('male' or 'female')

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

        # Format message with recipient name and gender-based salutation
        formatted_message = body
        if '{name}' in formatted_message:
            if recipient.get('Name') and recipient['Name'].lower() != 'unknown':
                # If name exists and not unknown, use name with gender-based suffix
                if executive_gender:
                    suffix = " sir" if executive_gender.lower() == 'male' else " ma'am"
                    formatted_message = formatted_message.replace('{name}', recipient['Name'] + suffix)
                else:
                    # If no gender selected, just use the name
                    formatted_message = formatted_message.replace('{name}', recipient['Name'])
            else:
                # If name is unknown or empty, use gender-based salutation
                if executive_gender:
                    salutation = "Dear sir" if executive_gender.lower() == 'male' else "Dear Ma'am"
                else:
                    salutation = "Dear ma'am"  # Default when no gender selected
                formatted_message = formatted_message.replace('Dear {name},', f'{salutation},')

        # Replace executive name placeholder
        if '{Executive Name}' in formatted_message and executive_name:
            formatted_message = formatted_message.replace('{Executive Name}', executive_name)

        # Replace executive number placeholder
        if '{Executive Number}' in formatted_message and executive_number:
            formatted_message = formatted_message.replace('{Executive Number}', executive_number)

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
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #000000;">
    <div style="max-width: 680px; margin: 0 auto; padding: 20px;">
        <div style="color: #000000;">
        {formatted_message.replace('{', '{{').replace('}', '}}')
                            .replace('{{recipient_email}}', recipient['Email'])
                            .replace('\n\n', '</p><p style="margin: 16px 0;">')
                            .replace('\n', '<br>')
                            .replace('●', '•')
                            .replace('○', '•')
                            .replace('________________________________________', '<hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">')
                            .replace('💜', '<span style="font-size: 16px;">💜</span>')
                            .replace('✨', '<span style="font-size: 16px;">✨</span>')
                            .replace('🌿', '<span style="font-size: 16px;">🌿</span>')
                            .replace('💬', '<span style="font-size: 16px;">💬</span>')
                            .replace('📚', '<span style="font-size: 16px;">📚</span>')}
    </div>
    </div>
</body>
</html>"""

        # Add HTML version
        part2 = MIMEText(html_body, 'html')
        msg.attach(part2)

        # Add attachments if provided
        if attachment_paths:
            for attachment_path in attachment_paths:
                # Handle both string and tuple formats
                if isinstance(attachment_path, tuple):
                    file_path, original_filename = attachment_path
                else:
                    file_path = attachment_path
                    original_filename = os.path.basename(file_path)

                if os.path.exists(file_path):
                    with open(file_path, "rb") as attachment:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(attachment.read())
                        encoders.encode_base64(part)
                        # Use the original filename for the attachment
                        part.add_header("Content-Disposition", f"attachment; filename={original_filename}")
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
    attachment_paths: Optional[List[Union[str, Tuple[str, str]]]] = None,
    executive_name: str = None,
    executive_number: str = None,
    executive_gender: str = None
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
        attachment_paths (List[Union[str, Tuple[str, str]]], optional): List of attachment paths
        executive_name (str, optional): Executive name for signature
        executive_number (str, optional): Executive contact number
        executive_gender (str, optional): Executive gender ('male' or 'female')

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

        # Create SMTP connection once for all emails
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, app_password)

        # Pre-process attachments once
        attachment_parts = []
        if attachment_paths:
            for attachment_path in attachment_paths:
                # Handle both string and tuple formats
                if isinstance(attachment_path, tuple):
                    file_path, original_filename = attachment_path
                else:
                    file_path = attachment_path
                    original_filename = os.path.basename(file_path)

                if os.path.exists(file_path):
                    with open(file_path, "rb") as attachment:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(attachment.read())
                        encoders.encode_base64(part)
                        part.add_header("Content-Disposition", f"attachment; filename={original_filename}")
                        attachment_parts.append(part)

        # Process each recipient
        total_recipients = len(df)
        for index, row in df.iterrows():
            try:
                # Create recipient dictionary
                recipient = {
                    'Email': row['Email'],
                    'Name': row['Name']
                }

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

                # Format message with recipient name and gender-based salutation
                formatted_message = message
                if '{name}' in formatted_message:
                    if recipient.get('Name') and recipient['Name'].lower() != 'unknown':
                        # If name exists and not unknown, use name with gender-based suffix
                        if executive_gender:
                            suffix = " sir" if executive_gender.lower() == 'male' else " ma'am"
                            formatted_message = formatted_message.replace('{name}', recipient['Name'] + suffix)
                        else:
                            # If no gender selected, just use the name
                            formatted_message = formatted_message.replace('{name}', recipient['Name'])
                    else:
                        # If name is unknown or empty, use gender-based salutation
                        if executive_gender:
                            salutation = "Dear sir" if executive_gender.lower() == 'male' else "Dear ma'am"
                        else:
                            salutation = "Dear ma'am"  # Default when no gender selected
                        formatted_message = formatted_message.replace('Dear {name},', f'{salutation},')

                # Replace executive placeholders
                if '{Executive Name}' in formatted_message and executive_name:
                    formatted_message = formatted_message.replace('{Executive Name}', executive_name)
                if '{Executive Number}' in formatted_message and executive_number:
                    formatted_message = formatted_message.replace('{Executive Number}', executive_number)

                # Add plain text version
                part1 = MIMEText(formatted_message, 'plain')
                msg.attach(part1)

                # Add HTML version
                html_body = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{subject}</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #000000;">
    <div style="max-width: 680px; margin: 0 auto; padding: 20px;">
        <div style="color: #000000;">
        {formatted_message.replace('{', '{{').replace('}', '}}')
                            .replace('{{recipient_email}}', recipient['Email'])
                            .replace('\n\n', '</p><p style="margin: 16px 0;">')
                            .replace('\n', '<br>')
                            .replace('●', '•')
                            .replace('○', '•')
                            .replace('________________________________________', '<hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">')
                            .replace('💜', '<span style="font-size: 16px;">💜</span>')
                            .replace('✨', '<span style="font-size: 16px;">✨</span>')
                            .replace('🌿', '<span style="font-size: 16px;">🌿</span>')
                            .replace('💬', '<span style="font-size: 16px;">💬</span>')
                            .replace('📚', '<span style="font-size: 16px;">📚</span>')}
        </div>
    </div>
</body>
</html>"""
                part2 = MIMEText(html_body, 'html')
                msg.attach(part2)

                # Add pre-processed attachments
                for part in attachment_parts:
                    msg.attach(part)

                # Get all recipients (including CC)
                all_recipients = [recipient['Email']]
                if cc_email:
                    all_recipients.append(cc_email)

                # Send email
                server.sendmail(sender_email, all_recipients, msg.as_string())

                success_count += 1
                last_email = recipient['Email']

                # Add smaller delay for fewer recipients
                if total_recipients <= 30:
                    time.sleep(90)  # 90 second delay for small batches
                else:
                    time.sleep(60)  # 60 second delay for larger batches

            except Exception as e:
                print(f"Error sending email to {row['Email']}: {str(e)}")
                failed_count += 1

        # Close SMTP connection
        server.quit()

        return {
            'success_count': success_count,
            'failed_count': failed_count,
            'last_email': last_email
        }

    except Exception as e:
        raise Exception(f"Error processing bulk emails: {str(e)}")
