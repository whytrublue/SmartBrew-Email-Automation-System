"""
Bulk Email Sender Page Module for SmartBrew Email Automation System
Handles the UI and functionality for sending bulk emails
"""

import streamlit as st
import pandas as pd
import os
import tempfile
from datetime import datetime

# Import utility functions
from src.utils.email_sender import send_email, send_bulk_emails
from src.components.ui_components import create_pie_chart

def show_bulk_email_sender_page():
    """Display the Bulk Email Sender page with all functionality"""
    st.subheader("📨 Bulk Email Sender")
    
    # Create a professional card-like container
    st.markdown("""
    <div style="padding: 10px; border-radius: 10px; background-color: var(--background-color); border: 1px solid var(--border-color);">
    <p style="color: var(--text-color); margin: 0;">Send personalized emails to individual recipients or in bulk with professional templates.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["Send Emails", "Templates", "Help & Info"])
    
    with tab1:
        # Authentication section
        st.markdown("### Account Information")
        
        # Add a prominent warning about email warming
        st.markdown("""
        <div style="padding: 15px; border-radius: 10px; background-color: var(--background-color); border: 1px solid var(--border-color);">
        <p style="color: var(--text-color); margin: 0;">
        ⚠️ **Important: Avoid Spam Filters**
        1. First time using this email? Start with just 5-10 emails to warm up the account.
        2. Gradually increase volume over several days.
        3. Ask recipients to mark your emails as "Not Spam" and add you to contacts.
        4. For best results, use a custom domain instead of free email providers.
        </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Create a container with proper styling for input fields
        st.markdown("""
        <style>
            .stTextInput > div > div > input {
                color: var(--text-color) !important;
                background-color: var(--background-color) !important;
            }
            .stTextInput > label {
                color: var(--text-color) !important;
            }
            .stRadio > div > label {
                color: var(--text-color) !important;
            }
            .stSelectbox > div > div > div {
                color: var(--text-color) !important;
                background-color: var(--background-color) !important;
            }
            .stSelectbox > label {
                color: var(--text-color) !important;
            }
            .stTextArea > div > div > textarea {
                color: var(--text-color) !important;
                background-color: var(--background-color) !important;
            }
            .stTextArea > label {
                color: var(--text-color) !important;
            }
            .stMarkdown h3 {
                color: var(--text-color) !important;
            }
            .stMarkdown p {
                color: var(--text-color) !important;
            }
            /* Radio button styling */
            .stRadio > div {
                background-color: var(--background-color) !important;
            }
            .stRadio > div > div {
                color: var(--text-color) !important;
            }
            .stRadio > div > div > div > div {
                color: var(--text-color) !important;
            }
            .stRadio > div > div > div > div > div {
                color: var(--text-color) !important;
            }
            .stRadio > div > div > div > div > div > div {
                color: var(--text-color) !important;
            }
            /* Radio button circles */
            .stRadio > div > div > div > div > div > div > div {
                border-color: var(--text-color) !important;
            }
            /* Radio button labels */
            .stRadio > div > div > div > div > div > div > label {
                color: var(--text-color) !important;
            }
            /* Radio button selected state */
            .stRadio > div > div > div > div > div > div > div[data-testid="stMarkdownContainer"] {
                color: var(--text-color) !important;
            }
            /* Radio button container */
            .stRadio > div > div > div > div > div {
                background-color: var(--background-color) !important;
            }
            /* Ensure help text is visible */
            .stTooltipIcon {
                color: var(--text-color) !important;
            }
            .stTooltipContent {
                color: var(--text-color) !important;
                background-color: var(--background-color) !important;
            }
        </style>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            email_id = st.text_input("Email ID", placeholder="your@gmail.com", key="sender_email", help="Your Gmail address")
            app_password = st.text_input("App Password", type="password", key="sender_password", help="Your app-specific password")
        with col2:
            cc_email = st.text_input("CC Email (optional)", placeholder="cc@example.com", help="Send a carbon copy to this email")
        
        # Sending mode selection
        st.markdown("### Recipients")
        sending_mode = st.radio(
            "Select Sending Mode",
            ["Single Email", "Bulk Email (CSV)"],
            horizontal=True,
            help="Choose whether to send to a single recipient or multiple recipients via CSV"
        )
        
        if sending_mode == "Bulk Email (CSV)":
            # Bulk email section
            uploaded_file = st.file_uploader(
                "Upload CSV with recipient details",
                type=["csv"],
                help="CSV file must include 'Name' and 'Email' columns"
            )
            
            # Sample CSV template download
            if not uploaded_file:
                sample_data = {
                    'Name': ['John Doe', 'Jane Smith', 'Unknown'],
                    'Email': ['john@example.com', 'jane@example.com', 'contact@company.com'],
                    'Company': ['ABC Corp', 'XYZ Inc', 'New Company'],
                    'Type': ['Client', 'Partner', 'Prospect']
                }
                sample_df = pd.DataFrame(sample_data)
                csv = sample_df.to_csv(index=False)
                
                st.download_button(
                    "Download Sample CSV Template",
                    csv,
                    "sample_recipients.csv",
                    "text/csv",
                    help="Download a sample CSV template to see the required format"
                )
        else:
            # Single email section
            col1, col2 = st.columns(2)
            with col1:
                recipient_email = st.text_input("Recipient Email", placeholder="recipient@example.com")
            with col2:
                recipient_name = st.text_input("Recipient Name", placeholder="John Doe")
        
        # Executive information section
        st.markdown("### Sender Information")
        col1, col2 = st.columns(2)
        with col1:
            executive_name = st.text_input("Executive Name", help="Your name to be included in the email signature")
            executive_gender = st.radio(
                "Select Gender",
                options=["Not Selected", "Male", "Female"],
                horizontal=True,
                help="Select gender for appropriate salutation in emails"
            )
        with col2:
            executive_number = st.text_input("Executive Number", help="Your contact number to be included in the email")
        
        # Convert gender selection to format expected by email sender
        executive_gender = executive_gender.lower() if executive_gender != "Not Selected" else None
        
        # Email content section
        st.markdown("### Email Content")
        
        # Email template selection
        st.markdown("### Email Template")
        email_type = st.selectbox(
            "Select Email Type",
            ["Custom Email/Write Own", "Initial Message - Does B2b Matters", 
             "Follow-up 1 - Awaiting Response", "Follow-up 2 - Still Confused", 
             "Follow-up 3 - KHUSHII Pads for Freedom", "Post-Discussion Email - KHUSHII Pads for Freedom",
             "Pricing Breakdown"],
            help="Choose a pre-defined template or create your own",
            key="email_template_type"
        )
        
        # Initialize default_template and default_subject
        default_template = ""
        default_subject = ""
        
        # Set template based on selection
        if email_type == "Custom Email/Write Own":
            subject = st.text_input("Subject", key="custom_subject")
            message = st.text_area("Message Body", height=200, key="custom_message")
        else:
            # Get default template content
            if email_type == "Initial Message - Does B2b Matters":
                default_subject = "Does B2b Matters"
                default_template = """Hi {name},

Transform your Commercial Real Estate approach.

We've recognized you as a significant influencer in commercial real estate. Our exclusive 15,000+ CRE Email list can greatly enhance your service offerings.

Our Email list has been designed with professionals like you in mind. It has over 95 percent accuracy, which could help streamline your business.

I would love to discuss this further. Ready to succeed.

Cheers,
{Executive Name}
DB Associate


To Suspend future emails type "Terminate"."""
            elif email_type == "Pricing Breakdown":
                default_subject = "Re: Touchbase with You"
                default_template = """Hi {name},

Wanted to make sure my previous message didn’t get buried.

Excited to hear from you.


Regards,
{Executive Name}


P.S. Enter "End" to opt-out."""
            elif email_type == "Follow-up 1 - Awaiting Response":
                default_subject = "Re: Awaiting Response"
                default_template = """Hi {name},

Any updates on our prior conversation?


Thanks,
{Executive Name}"""
            elif email_type == "Follow-up 2 - Still Confused":
                default_subject = "Re: Still Confused"
                default_template = """Dear {name},

Have an industry in mind? We're experts, ready to fuel your growth within your chosen field.

Best,
{Executive Name}"""
            elif email_type == "Follow-up 3 - KHUSHII Pads for Freedom":
                default_subject = "Re: Be the Reason She Stays in School 💜 | Pads for Freedom – KHUSHII"
                default_template = """Dear {name},

Subject: Still Hoping to Hear From You 💜 – Let's Empower Girls Together

I understand things can get busy, and I truly appreciate you taking the time to read this. I just didn't want to close this loop without giving one last nudge - because your support could mean the world to girls who are silently being pushed out of school due to period poverty.

Your leadership could help create real, lasting change. Even if you're unsure how you'd like to contribute, I'd be happy to walk you through a few simple ways you can get involved.

If now's not the right time, I completely understand. But if there's even a small window, I'd love to connect.

Thank you once again for everything you do.

Warm regards,

{Executive Name}
Campaign Volunteer, Pads for Freedom
Team KHUSHII
+91 {Executive Number}"""
            elif email_type == "Post-Discussion Email - KHUSHII Pads for Freedom":
                default_subject = "Re: Be the Reason She Stays in School 💜 | Pads for Freedom – KHUSHII"
                default_template = """Dear {name},

Subject: Post Discussion: Excited to Have You Onboard! | Pads for Freedom 💜

It was truly a pleasure connecting with you - and I'm so grateful for your willingness to support Pads for Freedom. Your voice will spark change that ripples far beyond what we can imagine.

As you know, 23 million girls in India drop out of school each year - not for lack of ability, but for lack of menstrual hygiene access and awareness. With your leadership, we shall break this silence and give girls the dignity, confidence, and freedom they deserve.

________________________________________
✨ Let's get you started! It's Super Easy:
Here's are the simple steps to you to lead and champion the cause:
1.	Send us a picture of yourself (we will create your personalized campaign poster).
2.	Pledge any number of girls you'd like to support (50, 100, 200, or even more)
3.	We'll send you:
○	A custom donation link for people to support directly.
○	A share-ready poster featuring you and your pledge.
4.	Share your link and poster on WhatsApp and social media (stories, reels, or posts—whatever feels right for you!).

Please know that your pledge is completely flexible - you can always choose to increase or decrease it based on your comfort. There is absolutely no financial obligation attached.
________________________________________

Why You Matter
Your involvement isn't just symbolic - it's transformative. You're helping ensure no girl is left behind because of something as natural as her period.

Let's make this year a turning point - for dignity, for education, and for equality.

Please share your photo and pledge at your convenience. And if you'd like us to guide you through any of this, we're just a text/call away.

Looking forward to creating a magical impact together!

Warm regards,

{Executive Name}
Campaign Volunteer, Pads for Freedom
Team KHUSHII
+91 {Executive Number}

PS. We've attached a cost breakdown, showing exactly how ₹1200 per girl is used to provide:
●	🌿 Free biodegradable sanitary pads		: ₹ 1104
●	💬 Menstrual and mental health counselling	: ₹     84	
●	📚 Awareness sessions to keep girls in school	: ₹     12"""
            
            # Apply current values to create preview
            preview_template = default_template
            if executive_name:
                preview_template = preview_template.replace("{Executive Name}", executive_name)
            if executive_number:
                preview_template = preview_template.replace("{Executive Number}", executive_number)
            
            # If in single email mode, also replace the name placeholder for preview
            if sending_mode == "Single Email":
                if recipient_name:
                    preview_template = preview_template.replace("{name}", recipient_name)
                else:
                    preview_template = preview_template.replace("Dear {name},", "Dear Ma'am,")
            
            subject = st.text_input("Subject", value=default_subject, key=f"{email_type.lower().replace(' ', '_')}_subject")
            message = st.text_area("Message Body", value=preview_template, height=200, key=f"{email_type.lower().replace(' ', '_')}_message")
        
        # Attachment option
        st.markdown("### Attachments")
        attachment_files = st.file_uploader(
            "Add Attachments (optional)",
            type=["pdf", "docx", "jpg", "png"],
            accept_multiple_files=True,
            help="Files must be PDF, DOCX, JPG, or PNG format. You can select multiple files."
        )
        
        # Send button
        send_col1, send_col2, send_col3 = st.columns([1, 2, 1])
        with send_col2:
            send_button = st.button("Send Email(s)", type="primary", use_container_width=True)
        
        if send_button:
            if email_id and app_password:
                # Handle attachments if uploaded
                attachment_paths = []
                temp_files = []  # Keep track of temp files for cleanup
                
                if attachment_files:
                    for attachment_file in attachment_files:
                        # Create a temporary file to save the uploaded file
                        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(attachment_file.name)[1]) as tmp:
                            tmp.write(attachment_file.getvalue())
                            # Store both the temporary path and original filename
                            attachment_paths.append((tmp.name, attachment_file.name))
                            temp_files.append(tmp.name)
                
                try:
                    if sending_mode == "Single Email":
                        if not recipient_email:
                            st.error("Please enter recipient email")
                        else:
                            with st.spinner("Sending email..."):
                                # Create recipient dictionary for single email
                                recipient = {
                                    'Email': recipient_email,
                                    'Name': recipient_name if recipient_name else ''
                                }
                                
                                # Send single email with keyword arguments
                                result = send_email(
                                    sender_email=email_id,
                                    sender_password=app_password,
                                    recipient=recipient,
                                    subject=subject,
                                    body=message,
                                    cc_email=cc_email,
                                    attachment_paths=attachment_paths if attachment_paths else None,
                                    executive_name=executive_name,
                                    executive_number=executive_number,
                                    executive_gender=executive_gender
                                )
                                
                                if result.startswith('✅'):
                                    st.success(result)
                                else:
                                    st.error(result)
                                
                                # Store in session state
                                st.session_state.last_send_result = {
                                    'type': 'single',
                                    'success': 1 if result.startswith('✅') else 0,
                                    'failed': 0 if result.startswith('✅') else 1,
                                    'last_email': recipient_email,
                                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                }
                                
                    else:  # Bulk Email (CSV)
                        if not uploaded_file:
                            st.error("Please upload a CSV file")
                        else:
                            with st.spinner("Sending emails..."):
                                try:
                                    # Send bulk emails
                                    result = send_bulk_emails(
                                        email_id, app_password, uploaded_file,
                                        subject, message, cc_email, 
                                        attachment_paths if attachment_paths else None,
                                        executive_name, executive_number, executive_gender
                                    )
                                    
                                    # Store in session state
                                    st.session_state.last_send_result = {
                                        'type': 'bulk',
                                        'success': result['success_count'],
                                        'failed': result['failed_count'],
                                        'last_email': result['last_email'],
                                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    }
                                    
                                    # Show success card
                                    st.success(f"Successfully sent {result['success_count']} emails. Last email sent to {result['last_email']}")
                                    
                                    # Show visualization
                                    show_send_results(result)
                                    
                                except Exception as e:
                                    st.error(f"Error sending bulk emails: {str(e)}")
                    
                    # Clean up temporary files
                    for temp_file in temp_files:
                        try:
                            os.unlink(temp_file)
                        except:
                            pass
                            
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    
                    # Clean up temporary files if there was an error
                    for temp_file in temp_files:
                        try:
                            os.unlink(temp_file)
                        except:
                            pass
            else:
                st.error("Please enter your email ID and app password")
            
            # Display email sending results and visualization
            if hasattr(st.session_state, 'last_send_result'):
                result = st.session_state.last_send_result
                
                # Create a container for results
                with st.container():
                    st.markdown("### 📊 Email Sending Results")
                    
                    # Display stats in columns
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        # Show detailed statistics
                        total_sent = result.get('success', 0)
                        total_failed = result.get('failed', 0)
                        total_attempts = total_sent + total_failed
                        success_rate = (total_sent / total_attempts * 100) if total_attempts > 0 else 0
                        
                        st.markdown(f"""
                        #### Summary Statistics
                        - **Total Emails Attempted:** {total_attempts}
                        - **Successfully Sent:** {total_sent}
                        - **Failed to Send:** {total_failed}
                        - **Success Rate:** {success_rate:.1f}%
                        """)
                        
                        # Show last email sent
                        if result.get('last_email'):
                            st.markdown(f"**Last Email Sent To:** {result['last_email']}")
                        
                        # Show timestamp
                        if result.get('timestamp'):
                            st.markdown(f"**Completed At:** {result['timestamp']}")
                    
                    with col2:
                        # Create pie chart for visualization
                        if total_attempts > 0:
                            chart_data = pd.DataFrame({
                                'Status': ['Successful', 'Failed'],
                                'Count': [total_sent, total_failed]
                            })
                            
                            fig = create_pie_chart(
                                chart_data,
                                value_column='Count',
                                names_column='Status',
                                title="Email Sending Results",
                                color_map={'Successful': '#28a745', 'Failed': '#dc3545'}
                            )
                            
                            st.plotly_chart(fig)
    
    with tab2:
        st.markdown("### Email Templates")
        
        st.markdown("""
        #### Template Types
        
        1. **Initial Message - Pads for Freedom**
           - Purpose: First contact with potential partners
           - Personalization: Uses recipient name, executive name, executive number
           - Best for: Introducing the initiative to new contacts
        
        2. **Follow-up 1 - Initial Check-in**
           - Purpose: First follow-up (5-7 days after initial contact)
           - Personalization: Uses recipient name, executive name, executive number
           - Best for: Gentle reminder about the initiative
        
        3. **Follow-up 2 - Additional Info**
           - Purpose: Second follow-up (7-10 days after first follow-up)
           - Personalization: Uses recipient name, executive name, executive number
           - Best for: Providing additional information and value
        
        4. **Follow-up 3 - Final Reminder**
           - Purpose: Final follow-up (7-10 days after second follow-up)
           - Personalization: Uses recipient name, executive name, executive number
           - Best for: Creating urgency with a deadline
        
        5. **Post-Discussion Email**
           - Purpose: After a meeting or call
           - Personalization: Uses recipient name, executive name, executive number
           - Best for: Thanking for time and providing additional materials
        
        #### Personalization Tags
        
        You can use the following tags in your custom emails:
        
        - `{name}`: Automatically replaced with recipient's name
        - `{Executive Name}`: Automatically replaced with executive name from the form
        - `{Executive Number}`: Automatically replaced with executive contact number from the form
        
        #### Best Practices
        
        1. Keep emails concise and focused
        2. Personalize when possible
        3. Include a clear call to action
        4. Avoid excessive formatting or images
        5. Send in batches of 100 with breaks in between
        """)
    
    with tab3:
        st.markdown("### Bulk Email Sender Help")
        
        st.markdown("""
        #### How to Use the Bulk Email Sender
        
        1. Enter your Gmail email address and app password
        2. Choose between single email or bulk mode
        3. For bulk mode, upload a CSV file with recipient details
        4. Fill in your executive information for the signature
        5. Select an email template or create your own
        6. Optionally add an attachment
        7. Click "Send Email(s)" to begin sending
        
        #### CSV File Format
        
        Your CSV file must include these columns:
        - **Email**: Recipient email addresses
        - **Name**: Recipient names for personalization
        
        Optional columns:
        - Company: Company names
        - Type: Contact types (Client, Prospect, etc.)
        
        #### Tips to Avoid Spam Filters
        
        Emails are more likely to land in inboxes if you:
        
        1. **Authenticate your domain**: Set up SPF, DKIM and DMARC records
        2. **Warm up your email account**: Start with small batches (10-20) and gradually increase
        3. **Personalize each email**: Use recipient names and relevant information
        4. **Send in smaller batches**: Send maximum 50-100 emails per day
        5. **Avoid spam trigger words**: "Free", "Act now", "Limited time", excessive exclamation marks
        6. **Include a physical address**: Add your business address in the footer
        7. **Add an unsubscribe link**: Let recipients opt-out easily
        8. **Use a balanced text-to-image ratio**: Don't rely too heavily on images
        9. **Send during business hours**: Avoid sending at unusual times
        10. **Ask recipients to add you to contacts**: Include this request in your initial emails
        
        #### Sending Limits
        
        - Gmail limits: 500 emails per day
        - Recommended: Take a 60-minute break after every 50 emails
        - The system will automatically pause between batches when needed
        
        #### Troubleshooting
        
        - If emails are not being sent, check your app password
        - Make sure your CSV file is formatted correctly
        - Some email providers may block bulk emails
        """)
        
        # Add spam score checker
        st.markdown("---")
        st.markdown("### 📊 Email Spam Score Checker")
        spam_text = st.text_area(
            "Paste your email content here to check for spam triggers",
            height=100,
            placeholder="Enter your email content to analyze for spam trigger words and phrases",
            key="spam_checker_text"
        )
        
        check_col1, check_col2, check_col3 = st.columns([1, 2, 1])
        with check_col2:
            check_button = st.button("Check Spam Score", key="check_spam_button", use_container_width=True)
        
        if check_button and spam_text:
            # Simple spam word checker
            spam_triggers = [
                "free", "act now", "limited time", "offer", "discount", "buy now",
                "cash", "clearance", "lowest price", "guarantee", "urgent", "immediate",
                "winner", "congratulations", "prize", "!!!!", "$$", "click here",
                "order now", "don't delete", "100% free", "risk free", "no risk",
                "special promotion", "unlimited", "instant", "best price"
            ]
            
            # Count triggers
            trigger_count = 0
            found_triggers = []
            
            for trigger in spam_triggers:
                if trigger.lower() in spam_text.lower():
                    trigger_count += 1
                    found_triggers.append(trigger)
            
            # Calculate score
            total_words = len(spam_text.split())
            score = min(100, int((trigger_count / max(1, total_words / 10)) * 100))
            
            # Display results
            if score < 20:
                st.success(f"Low spam score: {score}%. Your email looks good!")
            elif score < 50:
                st.warning(f"Medium spam score: {score}%. Consider revising some phrases.")
            else:
                st.error(f"High spam score: {score}%. Your email is likely to trigger spam filters!")
            
            if found_triggers:
                st.markdown("#### Spam Triggers Found:")
                st.write(", ".join(found_triggers))
                
            st.markdown("""
            #### Recommendations:
            - Personalize your emails with recipient names
            - Keep the text conversational and genuine
            - Avoid excessive punctuation (!!) and all caps
            - Don't use too many marketing phrases
            - Balance your text-to-link ratio
            """)

def show_send_results(result):
    """Display sending results with visualization"""
    # Create results container
    st.markdown("### Sending Results")
    
    # Display results in columns
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Show stats card
        if 'success' in result and 'failed' in result:
            total = result['success'] + result['failed']
            success_rate = round((result['success'] / total) * 100 if total > 0 else 0, 1)
            
            st.markdown(f"""
            #### Summary
            - Sent successfully: {result['success']}
            - Failed: {result['failed']}
            - Success rate: {success_rate}%
            """)
            
            if result['failed'] > 0:
                st.warning("Some emails failed to send. Check recipient addresses and try again.")
        
        # Show recipient info
        if 'recipient' in result:
            st.info(f"Email sent to: {result['recipient']}")
        elif 'last_email' in result:
            st.info(f"Last email sent to: {result['last_email']}")
    
    with col2:
        # Create visualization
        if 'success' in result and 'failed' in result:
            # Prepare data
            chart_data = {
                'Status': ['Successful', 'Bounced'],
                'Count': [result['success'], result['failed']]
            }
            df = pd.DataFrame(chart_data)
            
            # Create chart
            fig = create_pie_chart(
                df,
                value_column='Count',
                names_column='Status',
                title="Email Sending Status",
                color_map={'Successful': 'green', 'Bounced': 'red'}
            )
            
            st.plotly_chart(fig) 
