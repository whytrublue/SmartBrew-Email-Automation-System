"""
Campaign Matcher Module for SmartBrew Email Automation System
Handles matching of campaigns based on executive CC
"""

import imaplib
import email
import pandas as pd
import re
from email.utils import parseaddr, parsedate_to_datetime
from datetime import datetime, timedelta

def match_campaigns(campaign_email, app_password, executive_email=None, 
                    start_date=None, end_date=None, subject_filter=None):
    """
    Match campaigns from sent emails based on CC executive
    
    Parameters:
    -----------
    campaign_email : str
        Campaign email account to analyze
    app_password : str
        Application-specific password for authentication
    executive_email : str, optional
        Executive email to filter by (in CC field)
    start_date : datetime.date, optional
        Date to filter emails from (inclusive)
    end_date : datetime.date, optional
        Date to filter emails until (inclusive)
    subject_filter : str, optional
        Subject line to filter emails by
        
    Returns:
    --------
    pandas.DataFrame
        Dataframe containing matched campaign information
    """
    try:
        # Connect to Gmail IMAP server
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(campaign_email, app_password)
        
        # Make sure the sent mail folder exists
        status, folders = mail.list()
        sent_folder = None
        for folder in folders:
            folder_str = folder.decode('utf-8')
            if '[Gmail]/Sent Mail' in folder_str:
                sent_folder = '"[Gmail]/Sent Mail"'
                break
            elif '[Gmail]/Sent' in folder_str:
                sent_folder = '"[Gmail]/Sent"'
                break
        
        # If we didn't find the sent folder, try a default
        if not sent_folder:
            sent_folder = '"[Gmail]/Sent Mail"'
        
        # Select the sent folder
        try:
            mail.select(sent_folder)
        except Exception as e:
            raise Exception(f"Could not access sent mail folder: {str(e)}")
            
        # Convert start_date to string format if provided
        if start_date:
            start_date_str = start_date.strftime("%d-%b-%Y")
        else:
            # Default to 30 days ago
            default_start = datetime.now().date() - timedelta(days=30)
            start_date_str = default_start.strftime("%d-%b-%Y")
        
        # Build search query
        search_parts = []
        search_parts.append(f'SINCE "{start_date_str}"')
        
        # Add end date if provided
        if end_date:
            end_date_str = end_date.strftime("%d-%b-%Y")
            search_parts.append(f'BEFORE "{end_date_str}"')
        
        # Add subject filter if provided
        if subject_filter:
            # Escape quotes in subject filter
            safe_subject = subject_filter.replace('"', '\\"')
            search_parts.append(f'SUBJECT "{safe_subject}"')
        
        # Combine search parts with AND
        search_query = '(' + ' '.join(search_parts) + ')'
        
        # Search for matching emails
        status, data = mail.search(None, search_query)
        if status != 'OK':
            raise Exception(f"Search failed with status: {status}")
            
        mail_ids = data[0].split()
        
        # List to store all matched campaigns
        matches = []
        
        # Process emails
        for email_id in mail_ids:
            try:
                status, data = mail.fetch(email_id, '(RFC822)')
                if status != 'OK' or not data or not data[0]:
                    continue
                
                # Parse email data
                raw_email = data[0][1]
                msg = email.message_from_bytes(raw_email)
                
                # Get CC recipients
                cc_field = msg.get('Cc', '')
                cc_list = cc_field if isinstance(cc_field, str) else ''
                
                # If executive email is specified, check if in CC
                if executive_email and executive_email.strip():
                    # Case insensitive check for the email in CC field
                    if executive_email.lower() not in cc_list.lower():
                        continue
                
                # Get email details
                to_field = msg.get('To', '')
                if not to_field:
                    continue
                    
                # Extract recipient name and email
                # Try to get name from the To field
                to_name = "Unknown"
                to_email = ""
                
                # First try parseaddr
                name, to_email = parseaddr(to_field)
                if name and name != to_email:
                    to_name = name
                # If that fails, try a simple extraction
                elif '<' in to_field:
                    to_name = to_field.split('<')[0].strip('" \t\n')
                    to_email_match = re.search(r'<([^>]+)>', to_field)
                    if to_email_match:
                        to_email = to_email_match.group(1)
                else:
                    to_email = to_field.strip()
                
                # Extract and format date
                date_str = msg.get('Date', '')
                try:
                    # Try to parse the date
                    parsed_date = parsedate_to_datetime(date_str)
                    date = parsed_date.strftime("%Y-%m-%d %H:%M")
                except:
                    # If parsing fails, use the original string
                    date = date_str
                
                # Get subject
                subject = msg.get('Subject', '(No Subject)')
                # Decode subject if needed
                if isinstance(subject, bytes):
                    try:
                        subject = subject.decode('utf-8')
                    except:
                        subject = "(Encoding Error)"
                
                # Extract message ID for response checking
                message_id = msg.get('Message-ID', '')
                
                # Determine executive name
                if executive_email:
                    # Extract name from email (before @)
                    exec_parts = executive_email.split('@')
                    if len(exec_parts) > 0:
                        executive_name = exec_parts[0].capitalize()
                    else:
                        executive_name = "Unknown"
                else:
                    # Try to get the From field for the sender's name
                    from_field = msg.get('From', '')
                    from_name, _ = parseaddr(from_field)
                    executive_name = from_name if from_name else "Various"
                
                # Check if there was a response
                has_response = _check_for_response(mail, message_id)
                
                # Add to our dataset
                matches.append({
                    'Name': to_name,
                    'Follow-up Email': to_email,
                    'Date': date,
                    'Subject': subject,
                    'Status': 'Responded' if has_response else 'Not Responded',
                    'Executive Name': executive_name
                })
            
            except Exception as e:
                # Skip this email if there's an error processing it
                continue
        
        # Convert to DataFrame
        df = pd.DataFrame(matches)
        
        # If DataFrame is empty, return an empty DataFrame with the correct columns
        if df.empty:
            return pd.DataFrame(columns=['Name', 'Follow-up Email', 'Date', 'Subject', 'Status', 'Executive Name'])
            
        return df
        
    except Exception as e:
        raise Exception(f"Error matching campaigns: {str(e)}")
    finally:
        try:
            mail.close()
            mail.logout()
        except:
            pass

def _check_for_response(mail, message_id):
    """
    Helper function to check if a message has received a response
    by searching for emails with In-Reply-To header matching the message_id
    
    Parameters:
    -----------
    mail : imaplib.IMAP4_SSL
        Active IMAP connection
    message_id : str
        Message ID to check for responses
        
    Returns:
    --------
    bool
        True if response found, False otherwise
    """
    if not message_id:
        return False
        
    try:
        # Save current folder
        current_folder = mail.select()[1][0].decode('utf-8').split('"')[1]
        
        # Switch to inbox to look for replies
        mail.select('inbox')
        
        # Search for emails that are replies to the given message_id
        # Escape quotes in message ID
        safe_message_id = message_id.replace('"', '\\"')
        search_query = f'(HEADER IN-REPLY-TO "{safe_message_id}")'
        status, data = mail.search(None, search_query)
        
        # If we found any replies, return True
        mail_ids = data[0].split()
        return len(mail_ids) > 0
    
    except Exception as e:
        # If there's an error, assume no response
        return False
    finally:
        # Switch back to original folder for continued operations
        try:
            mail.select(current_folder)
        except:
            try:
                mail.select('"[Gmail]/Sent Mail"')
            except:
                pass 