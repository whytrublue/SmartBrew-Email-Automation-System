"""
Email Extractor Module for SmartBrew Email Automation System
Handles extraction of emails from a mailbox based on filters
"""

import imaplib
import email
import pandas as pd
from email.utils import parseaddr
from datetime import datetime
from typing import List, Dict, Optional, Set
import gc
import re

def extract_emails(
    email_id: str,
    app_password: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    folder: str = 'sent',
    batch_size: int = 100,
    max_emails: int = 3000,
    subject_filter: Optional[str] = None
) -> List[Dict]:
    """
    Extract emails from Gmail account with optimized performance.

    Args:
        email_id (str): Email address
        app_password (str): App-specific password
        start_date (datetime, optional): Start date for filtering (inclusive)
        end_date (datetime, optional): End date for filtering (inclusive)
        folder (str): 'sent', 'inbox', or 'Failure/Delay'
        batch_size (int): Number of emails to process in each batch
        max_emails (int, optional): Maximum number of emails to extract
        subject_filter (str, optional): Filter emails by subject keywords

    Returns:
        List[Dict]: List of extracted emails with details
    """
    try:
        # Connect to Gmail IMAP server
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(email_id, app_password)

        # First, let's build a thread mapping to track conversations
        thread_mapping = {}
        message_id_to_thread = {}

        # Get relevant folders for thread analysis
        sent_folder = '"[Gmail]/Sent Mail"'
        inbox_folder = 'inbox'

        # Function to extract message-id and references for threading
        def process_emails_for_threads(mail_folder):
            try:
                mail.select(mail_folder, readonly=True)  # Select in readonly mode
                thread_search = []
                if start_date:
                    thread_search.append(f'(SINCE "{start_date.strftime("%d-%b-%Y")}")')
                if end_date:
                    thread_search.append(f'(BEFORE "{end_date.strftime("%d-%b-%Y")}")')
                search_criteria = ' '.join(thread_search) if thread_search else 'ALL'
                _, message_numbers = mail.search(None, search_criteria)
                message_numbers = message_numbers[0].split()
                message_numbers = message_numbers[:1000]  # Limit for performance

                start_time = datetime.now()
                max_processing_time = 60

                for num in message_numbers:
                    current_time = datetime.now()
                    if (current_time - start_time).total_seconds() > max_processing_time:
                        print(f"Thread mapping timeout in {mail_folder}, partial mapping used.")
                        break
                    try:
                        _, msg_data = mail.fetch(num, '(BODY.PEEK[HEADER])')
                        if not msg_data or not isinstance(msg_data[0], tuple) or not msg_data[0][1]:
                            continue
                        email_headers = email.message_from_bytes(msg_data[0][1])
                        message_id = email_headers.get('Message-ID', '')
                        if not message_id:
                            continue
                        references = email_headers.get('References', '')
                        in_reply_to = email_headers.get('In-Reply-To', '')
                        ref_list = [ref for ref in references.split() if ref] + ([in_reply_to] if in_reply_to else [])

                        if ref_list:
                            thread_id = next((message_id_to_thread[ref] for ref in ref_list if ref in message_id_to_thread), None)
                            if thread_id:
                                thread_mapping[thread_id].add(message_id)
                                message_id_to_thread[message_id] = thread_id
                                for ref in ref_list:
                                    message_id_to_thread[ref] = thread_id
                            else:
                                thread_id = message_id
                                thread_mapping[thread_id] = set([message_id] + ref_list)
                                message_id_to_thread[message_id] = thread_id
                                for ref in ref_list:
                                    message_id_to_thread[ref] = thread_id
                        elif message_id not in message_id_to_thread:
                            thread_mapping[message_id] = set([message_id])
                            message_id_to_thread[message_id] = message_id
                    except Exception as e:
                        print(f"Error processing header for threading in {mail_folder} (ID: {num}): {e}")
            finally:
                try:
                    mail.close() # Close connection after processing threads for a folder
                    mail.login(email_id, app_password) # Re-login if needed
                except Exception as e:
                    print(f"Error closing/re-logging after threading in {mail_folder}: {e}")

        # Build thread mapping from both folders
        process_emails_for_threads(sent_folder)
        process_emails_for_threads(inbox_folder)

        # Select the target folder
        if folder.lower() == 'sent':
            mail.select(sent_folder)
        elif folder.lower() == 'inbox':
            mail.select(inbox_folder)
        elif folder.lower() == 'failure/delay':
            # Need to search for emails with "Failure" or "Delay" labels
            status, label_uids = mail.search(None, 'X-GM-LABELS', 'Failure', 'X-GM-LABELS', 'Delay')
            if status == 'OK':
                message_numbers = b','.join(label_uids).split(b',')
            else:
                message_numbers = []
        else:
            raise ValueError(f"Invalid folder: {folder}. Must be 'sent', 'inbox', or 'Failure/Delay'.")

        if folder.lower() != 'failure/delay':
            # Build search query for 'sent' and 'inbox'
            search_query = []
            if start_date:
                search_query.append(f'(SINCE "{start_date.strftime("%d-%b-%Y")}")')
            if end_date:
                search_query.append(f'(BEFORE "{end_date.strftime("%d-%b-%Y")}")')
            if subject_filter:
                safe_subject = subject_filter.replace('"', '\\"')
                search_query.append(f'(SUBJECT "{safe_subject}")')
            search_query.append('(SMALLER 1000000)')
            search_criteria = ' '.join(search_query)
            _, message_numbers = mail.search(None, search_criteria)
            message_numbers = message_numbers[0].split() if message_numbers[0] else []

        total_emails = len(message_numbers)
        if max_emails:
            message_numbers = message_numbers[:max_emails]

        extracted_emails = []
        consecutive_errors = 0

        for i in range(0, len(message_numbers), batch_size):
            batch = message_numbers[i:i + batch_size]
            for num in batch:
                try:
                    _, msg_data = mail.fetch(num, '(RFC822)')
                    if not msg_data or not isinstance(msg_data[0], tuple) or not msg_data[0][1]:
                        print(f"Warning: Invalid message data for email {num}")
                        consecutive_errors += 1
                        if consecutive_errors >= 5:
                            print("Too many consecutive errors, stopping extraction.")
                            break
                        continue

                    email_data = email.message_from_bytes(msg_data[0][1])
                    consecutive_errors = 0

                    email_info = {
                        'Subject': email_data.get('Subject', ''),
                        'From': email_data.get('From', ''),
                        'To': email_data.get('To', ''),
                        'Date': email_data.get('Date', ''),
                        'Message-ID': email_data.get('Message-ID', ''),
                        'Body': ''
                    }

                    if email_data.is_multipart():
                        for part in email_data.walk():
                            ctype = part.get_content_type()
                            cdispo = str(part.get('Content-Disposition'))
                            if ctype == 'text/plain' and 'attachment' not in cdispo:
                                body = part.get_payload(decode=True).decode(errors='ignore')
                                email_info['Body'] = body
                                break
                    else:
                        body = email_data.get_payload(decode=True).decode(errors='ignore')
                        email_info['Body'] = body

                    has_response = False
                    message_id = email_info['Message-ID']
                    if message_id and message_id in message_id_to_thread:
                        thread_id = message_id_to_thread[message_id]
                        has_response = len(thread_mapping.get(thread_id, set())) > 1

                    subject_lower = email_info['Subject'].lower() if email_info['Subject'] else ""
                    if not has_response and ("re:" in subject_lower or "fw:" in subject_lower or "fwd:" in subject_lower):
                        has_response = True
                    if not has_response and (email_data.get('References') or email_data.get('In-Reply-To')):
                        has_response = True

                    original_recipient_email = None
                    if folder.lower() == 'failure/delay':
                        email_matches = re.findall(r'[\w\.-]+@[\w\.-]+\.[\w]+', email_info['Body'])
                        for match in email_matches:
                            if match != email_id and not match.endswith(".bounces.google.com"):
                                original_recipient_email = match
                                break

                        extracted_emails.append({
                            'Sender Name': parseaddr(email_info['From'])[0] if email_info['From'] else "System",
                            'Sender Email': parseaddr(email_info['From'])[1] if email_info['From'] else "mailer-daemon@google.com",
                            'Recipient Name': parseaddr(email_info['To'])[0] if email_info['To'] else "Unknown",
                            'Recipient Email': parseaddr(email_info['To'])[1] if email_info['To'] else "Unknown",
                            'Date': email_info['Date'],
                            'Subject': email_info['Subject'],
                            'Status': 'Failure/Delay',
                            'Original Recipient Email': original_recipient_email,
                            'Body': email_info['Body']
                        })
                    elif folder.lower() == 'sent':
                        to_field = email_data.get('To', '')
                        recipients = to_field.split(',')
                        for recipient in recipients:
                            try:
                                name, address = parseaddr(recipient)
                                if not name:
                                    name = "Unknown"
                                if not address or "@bounces." in address:
                                    continue
                                extracted_emails.append({
                                    'Sender Name': parseaddr(email_info['From'])[0] if email_info['From'] else "Me",
                                    'Sender Email': parseaddr(email_info['From'])[1] if email_info['From'] else email_id,
                                    'Recipient Name': name.strip(),
                                    'Recipient Email': address.strip(),
                                    'Date': email_info['Date'],
                                    'Subject': email_info['Subject'],
                                    'Status': 'Responded' if has_response else 'Not Responded',
                                    'Original Recipient Email': None
                                })
                            except Exception as e:
                                print(f"Warning: Error processing recipient {recipient}: {e}")
                                continue
                    elif folder.lower() == 'inbox':
                        from_field = email_data.get('From', '')
                        to_field = email_data.get('To', '')
                        try:
                            from_name, from_email = parseaddr(from_field)
                            to_name, to_email = parseaddr(to_field) if to_field else ("", "")
                            extracted_emails.append({
                                'Sender Name': from_name.strip() if from_name else "Unknown",
                                'Sender Email': from_email.strip() if from_email else "Unknown",
                                'Recipient Name': to_name.strip() if to_name else "Me",
                                'Recipient Email': to_email.strip() if to_email else email_id,
                                'Date': email_info['Date'],
                                'Subject': email_info['Subject'],
                                'Status': 'Responded' if has_response else 'Not Responded',
                                'Original Recipient Email': None,
                                'Body': email_info['Body']
                            })
                        except Exception as e:
                            print(f"Warning: Error processing sender/recipient in inbox: {e}")
                            continue

                except Exception as e:
                    print(f"Warning: Error processing email {num}: {e}")
                    consecutive_errors += 1
                    if consecutive_errors >= 5:
                        print("Too many consecutive errors, stopping extraction.")
                        break
                    continue

            del batch
            gc.collect()
            if consecutive_errors >= 5:
                break

        mail.close()
        mail.logout()
        return extracted_emails

    except Exception as e:
        raise Exception(f"Error extracting emails: {str(e)}")

def _count_frequency(email_id, app_password, target_email):
    """
    Helper function to count how many times we've emailed a specific address
    """
    try:
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(email_id, app_password)
        mail.select('"[Gmail]/Sent Mail"')
        status, data = mail.search(None, f'(TO "{target_email}")')
        mail_ids = data[0].split()
        return len(mail_ids)
    except Exception:
        return 1
    finally:
        try:
            mail.close()
            mail.logout()
        except:
            pass
