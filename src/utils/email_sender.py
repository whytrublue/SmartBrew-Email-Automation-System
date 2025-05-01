import smtplib
import os
import uuid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from typing import List, Dict, Optional, Union, Tuple

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
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg["From"] = f"{executive_name} <{sender_email}>" if executive_name else sender_email
        msg["To"] = f"{recipient.get('Name', '')} <{recipient['Email']}>" if recipient.get('Name') else recipient['Email']
        msg["Subject"] = subject
        msg.add_header('Message-ID', f"<{uuid.uuid4()}@smartbrew.in>")
        msg.add_header('Date', datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0530"))

        if cc_email:
            msg["Cc"] = cc_email

        # Format message with recipient name and gender-based salutation
        formatted_message = body

        if '{name}' in formatted_message:
            if recipient.get('Name') and recipient['Name'].lower() != 'unknown':
                if executive_gender:
                    suffix = " sir" if executive_gender.lower() == 'male' else " ma'am"
                    formatted_message = formatted_message.replace('{name}', recipient['Name'] + suffix)
                else:
                    formatted_message = formatted_message.replace('{name}', recipient['Name'])
            else:
                if executive_gender:
                    salutation = "Dear sir" if executive_gender.lower() == 'male' else "Dear Ma'am"
                else:
                    salutation = "Dear ma'am"
                formatted_message = formatted_message.replace('Dear {name},', f'{salutation},')

        if '{Executive Name}' in formatted_message and executive_name:
            formatted_message = formatted_message.replace('{Executive Name}', executive_name)

        if '{Executive Number}' in formatted_message and executive_number:
            formatted_message = formatted_message.replace('{Executive Number}', executive_number)

        # Plain text version
        part1 = MIMEText(formatted_message, 'plain')
        msg.attach(part1)

        # HTML version
        html_body = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{subject}</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #000000;">
    <div style="max-width: 680px; margin: 0 auto; padding: 20px;">
        <div style="color: #000000;">
            {formatted_message.replace('\n\n', '</p><p style="margin: 16px 0;">')
                               .replace('\n', '<br>')
                               .replace('●', '•')
                               .replace('○', '•')
                               .replace('💜', '<span style="font-size: 16px;">💜</span>')
                               .replace('✨', '<span style="font-size: 16px;">✨</span>')
                               .replace('🌿', '<span style="font-size: 16px;">🌿</span>')
                               .replace('💬', '<span style="font-size: 16px;">💬</span>')
                               .replace('📚', '<span style="font-size: 16px;">📚</span>')
            }
        </div>
    </div>
</body>
</html>"""
        part2 = MIMEText(html_body, 'html')
        msg.attach(part2)

        # Attachments
        if attachment_paths:
            for attachment_path in attachment_paths:
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
                        msg.attach(part)

        # Send
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)

        recipients = [recipient['Email']]
        if cc_email:
            recipients.append(cc_email)

        server.sendmail(sender_email, recipients, msg.as_string())
        server.quit()

        return f"✅ Email sent to {recipient['Email']}"

    except Exception as e:
        return f"❌ Error sending email to {recipient['Email']}: {str(e)}"
