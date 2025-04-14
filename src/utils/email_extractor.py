"""
Email Extractor Module for SmartBrew Email Automation System
Handles extraction of emails from a mailbox based on filters
"""

import imaplib
import email
import pandas as pd
from email.utils import parseaddr
from datetime import datetime
from typing import List, Dict, Optional
import gc

def extract_emails(
    email_id: str,
    app_password: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    folder: str = 'sent',
    batch_size: int = 100,
    max_emails: int = 3000
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
        
    Returns:
        List[Dict]: List of extracted emails with details
    """
    try:
        # Connect to Gmail IMAP server
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(email_id, app_password)
        
        # Select folder
        if folder.lower() == 'sent':
            mail.select('"[Gmail]/Sent Mail"')
        else:
            mail.select('inbox')
        
        # Build search query
        search_query = []
        
        # Add date filters if provided
        if start_date:
            start_date_str = start_date.strftime("%d-%b-%Y")
            search_query.append(f'(SINCE "{start_date_str}")')
        if end_date:
            end_date_str = end_date.strftime("%d-%b-%Y")
            search_query.append(f'(BEFORE "{end_date_str}")')
        
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
            
            # Fetch email headers first
            for num in batch:
                try:
                    # Fetch only headers first
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
                        'Message-ID': email_data.get('Message-ID', '')
                    }
                    
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
                                    
                                # Check for response using subject
                                has_response = "Re:" in email_info['Subject']
                                
                                extracted_emails.append({
                                    'Name': name,
                                    'Email': address,
                                    'Date': email_info['Date'],
                                    'Subject': email_info['Subject'],
                                    'Status': 'Responded' if has_response else 'Not Responded'
                                })
                            except Exception as e:
                                print(f"Warning: Error processing recipient {recipient}: {str(e)}")
                                continue
                    else:
                        # For inbox, get sender info
                        from_field = email_data.get('From', '')
                        if not from_field:
                            continue
                            
                        try:
                            from_name, from_email = parseaddr(from_field)
                            if not from_name:
                                from_name = "Unknown"
                            
                            if not from_email or "@bounces." in from_email:
                                continue
                                
                            # Check if this is a reply
                            has_response = "Re:" in email_info['Subject']
                            
                            extracted_emails.append({
                                'Name': from_name,
                                'Email': from_email,
                                'Date': email_info['Date'],
                                'Subject': email_info['Subject'],
                                'Status': 'Responded' if has_response else 'Not Responded'
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