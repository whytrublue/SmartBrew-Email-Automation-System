
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
        folder (str): 'sent' or 'inbox'
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

        # Get both sent and inbox to analyze threads
        sent_folder = '"[Gmail]/Sent Mail"'
        inbox_folder = 'inbox'

        # Function to extract message-id and references
        def process_emails_for_threads(mail_folder):
            mail.select(mail_folder)

            # Build basic search for threading
            thread_search = []
            if start_date:
                thread_search.append(f'(SINCE "{start_date.strftime("%d-%b-%Y")}")')
            if end_date:
                thread_search.append(f'(BEFORE "{end_date.strftime("%d-%b-%Y")}")')

            # Search for all emails
            search_criteria = ' '.join(thread_search) if thread_search else 'ALL'
            _, message_numbers = mail.search(None, search_criteria)
            message_numbers = message_numbers[0].split()

            # Limit to avoid performance issues (use a smaller limit for thread mapping)
            message_numbers = message_numbers[:1000]

            # Set a counter for timeout
            processed = 0
            start_time = datetime.now()
            max_processing_time = 60  # Max 60 seconds for thread mapping

            # Process each message
            for num in message_numbers:
                try:
                    # Check if we've spent too much time
                    current_time = datetime.now()
                    if (current_time - start_time).total_seconds() > max_processing_time:
                        print("Thread mapping timeout reached, using partial mapping")
                        break

                    # Fetch only headers
                    _, msg_data = mail.fetch(num, '(BODY.PEEK[HEADER])')

                    # Skip invalid data
                    if not msg_data or not isinstance(msg_data[0], tuple) or not msg_data[0][1]:
                        continue

                    # Parse email headers
                    email_headers = email.message_from_bytes(msg_data[0][1])

                    # Get the unique message ID
                    message_id = email_headers.get('Message-ID', '')
                    if not message_id:
                        continue

                    # Get references to track thread
                    references = email_headers.get('References', '')
                    in_reply_to = email_headers.get('In-Reply-To', '')

                    # Split references into list
                    ref_list = []
                    if references:
                        ref_list.extend(references.split())
                    if in_reply_to and in_reply_to not in ref_list:
                        ref_list.append(in_reply_to)

                    # If this email has references, it belongs to an existing thread
                    if ref_list:
                        # Find the thread this belongs to
                        thread_id = None
                        for ref in ref_list:
                            if ref in message_id_to_thread:
                                thread_id = message_id_to_thread[ref]
                                break

                        if thread_id:
                            # Add to existing thread
                            thread_mapping[thread_id].add(message_id)
                            message_id_to_thread[message_id] = thread_id
                        else:
                            # Start new thread with this message id
                            thread_id = message_id
                            thread_mapping[thread_id] = set([message_id] + ref_list)
                            message_id_to_thread[message_id] = thread_id

                            # Also add references to the mapping
                            for ref in ref_list:
                                message_id_to_thread[ref] = thread_id
                    else:
                        # This is a new thread
                        thread_mapping[message_id] = set([message_id])
                        message_id_to_thread[message_id] = message_id

                except Exception as e:
                    print(f"Error processing email for threading: {str(e)}")
                    continue

        # Build thread mapping from both folders
        process_emails_for_threads(sent_folder)
        process_emails_for_threads(inbox_folder)

        # Now extract emails from the requested folder with proper thread tracking
        mail.select(sent_folder if folder.lower() == 'sent' else inbox_folder)

        # Build search query
        search_query = []

        # Add date filters if provided
        if start_date:
            start_date_str = start_date.strftime("%d-%b-%Y")
            search_query.append(f'(SINCE "{start_date_str}")')
        if end_date:
            end_date_str = end_date.strftime("%d-%b-%Y")
            search_query.append(f'(BEFORE "{end_date_str}")')

        # Add subject filter if provided
        if subject_filter:
            # Escape quotes in subject filter
            safe_subject = subject_filter.replace('"', '\\"')
            search_query.append(f'(SUBJECT "{safe_subject}")')

        # Add size filter to exclude large emails
        search_query.append('(SMALLER 1000000)')  # Exclude emails larger than 1MB

        # Combine search criteria
        search_criteria = ' '.join(search_query)

        # Search for emails
        _, message_numbers = mail.search(None, search_criteria)
        message_numbers = message_numbers[0].split()

        # Limit number of emails if specified
        if max_emails:
            message_numbers = message_numbers[:max_emails]

        total_emails = len(message_numbers)
        if total_emails == 0:
            return []

        # Process emails in batches
        extracted_emails = []
        consecutive_errors = 0  # Track consecutive errors

        for i in range(0, total_emails, batch_size):
            batch = message_numbers[i:i + batch_size]

            # Fetch email content
            for num in batch:
                try:
                    # Fetch the full email content
                    _, msg_data = mail.fetch(num, '(RFC822)')

                    # Check if msg_data is valid
                    if not msg_data or not isinstance(msg_data[0], tuple) or not msg_data[0][1]:
                        print(f"Warning: Invalid message data for email {num}")
                        consecutive_errors += 1
                        if consecutive_errors >= 5:  # Break if too many consecutive errors
                            print("Too many consecutive errors, stopping extraction")
                            break
                        continue

                    email_data = email.message_from_bytes(msg_data[0][1])

                    # Reset consecutive errors counter on success
                    consecutive_errors = 0

                    # Extract basic information from headers with safe defaults
                    email_info = {
                        'Subject': email_data.get('Subject', ''),
                        'From': email_data.get('From', ''),
                        'To': email_data.get('To', ''),
                        'Date': email_data.get('Date', ''),
                        'Message-ID': email_data.get('Message-ID', ''),
                        'Body': '' # Initialize body
                    }

                    # Get the body
                    if email_data.is_multipart():
                        for part in email_data.walk():
                            ctype = part.get_content_type()
                            cdispo = str(part.get('Content-Disposition'))

                            # Look for the plain text part
                            if ctype == 'text/plain' and 'attachment' not in cdispo:
                                body = part.get_payload(decode=True).decode()
                                email_info['Body'] = body
                                break # Assuming plain text is sufficient
                    else:
                        body = email_data.get_payload(decode=True).decode()
                        email_info['Body'] = body

                    # Check thread status for response
                    has_response = False
                    message_id = email_info['Message-ID']

                    # If this message is in a thread, check if the thread has more than one message
                    if message_id and message_id in message_id_to_thread:
                        thread_id = message_id_to_thread[message_id]
                        thread_size = len(thread_mapping.get(thread_id, set()))
                        has_response = thread_size > 1

                    # Also check standard reply indicators as backup
                    if not has_response:
                        # Check for reply prefixes in subject (case insensitive)
                        subject = email_info['Subject'].lower() if email_info['Subject'] else ""
                        if "re:" in subject or "fw:" in subject or "fwd:" in subject:
                            has_response = True

                        # Check for references or in-reply-to headers
                        if email_data.get('References') or email_data.get('In-Reply-To'):
                            has_response = True

                    # Process recipient information
                    if folder.lower() == 'sent':
                        to_field = email_data.get('To', '')
                        if not to_field:
                            continue

                        # Handle multiple recipients
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
                                    'Recipient Name': name,
                                    'Recipient Email': address,
                                    'Date': email_info['Date'],
                                    'Subject': email_info['Subject'],
                                    'Status': 'Responded' if has_response else 'Not Responded',
                                    'Original Recipient Email': None # Not applicable for sent emails
                                })
                            except Exception as e:
                                print(f"Warning: Error processing recipient {recipient}: {str(e)}")
                                continue
                    else:  # folder.lower() == 'inbox'
                        from_field = email_data.get('From', '')
                        to_field = email_data.get('To', '') # Get the 'To' field of the received email
                        original_recipient_email = None

                        # If it's a delivery status notification, try to extract the original recipient
                        subject_lower = email_info['Subject'].lower()
                        if "delivery status notification" in subject_lower or "delivery incomplete" in subject_lower or "failure" in subject_lower:
                            email_matches = re.findall(r'[\w\.-]+@[\w\.-]+\.[\w]+', email_info['Body'])
                            if email_matches:
                                # Assuming the first valid email found is the original recipient
                                for match in email_matches:
                                    if match != email_id and not match.endswith(".bounces.google.com"):
                                        original_recipient_email = match
                                        break

                        if not from_field:
                            continue

                        try:
                            from_name, from_email = parseaddr(from_field)
                            if not from_name:
                                from_name = "Unknown"

                            if not from_email or "@bounces." in from_email:
                                continue

                            _, to_email = parseaddr(to_field) if to_field else ("", "")

                            extracted_emails.append({
                                'Sender Name': from_name,
                                'Sender Email': from_email,
                                'Recipient Name': parseaddr(to_field)[0] if to_field else "Me",
                                'Recipient Email': to_email if to_email else email_id, # Default to your email
                                'Date': email_info['Date'],
                                'Subject': email_info['Subject'],
                                'Status': 'Responded' if has_response else 'Not Responded',
                                'Original Recipient Email': original_recipient_email,
                                'Body': email_info['Body']
                            })
                        except Exception as e:
                            print(f"Warning: Error processing sender {from_field}: {str(e)}")
                            continue

                except Exception as e:
                    print(f"Warning: Error processing email {num}: {str(e)}")
                    consecutive_errors += 1
                    if consecutive_errors >= 5:  # Break if too many consecutive errors
                        print("Too many consecutive errors, stopping extraction")
                        break
                    continue

            # Clear memory after each batch
            del batch
            gc.collect()

            # Break the outer loop if we hit too many consecutive errors
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
        # Connect to Gmail IMAP server
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(email_id, app_password)
        mail.select('"[Gmail]/Sent Mail"')

        # Search for emails sent to target
        status, data = mail.search(None, f'(TO "{target_email}")')
        mail_ids = data[0].split()

        # Return count of emails sent
        return len(mail_ids)

    except Exception:
        # If we can't get an accurate count, just return 1
        return 1
    finally:
        try:
            mail.close()
            mail.logout()
        except:
            pass
