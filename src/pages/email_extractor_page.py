"""
Email Extractor Page Module for SmartBrew Email Automation System
Handles the UI and functionality for extracting emails
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Import utility functions
from src.utils.email_extractor import extract_emails
from src.components.ui_components import create_pie_chart, get_csv_download_link

def show_email_extractor_page():
    """Display the Email Extractor page with all functionality"""
    st.subheader("📧 Email Extractor")

    # Create a professional card-like container
    st.markdown("""
    <div style="padding: 10px; border-radius: 10px; background-color: var(--background-color); border: 1px solid var(--border-color);">
    <p style="color: var(--text-color); margin: 0;">Extract email data from your inbox, sent folder, or failure/delay labels based on filters. Process up to 3000+ emails at once for detailed analysis.</p>
    </div>
    """, unsafe_allow_html=True)

    # Add styling for input fields
    st.markdown("""
    <style>
        /* Base styles for all inputs */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div > div,
        .stDateInput > div > div > input {
            color: var(--text-color) !important;
            background-color: var(--background-color) !important;
            border-color: var(--border-color) !important;
        }

        /* Labels */
        .stTextInput > label,
        .stTextArea > label,
        .stSelectbox > label,
        .stDateInput > label,
        .stRadio > label {
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

        /* Help text and tooltips */
        .stTooltipIcon {
            color: var(--text-color) !important;
        }
        .stTooltipContent {
            color: var(--text-color) !important;
            background-color: var(--background-color) !important;
            border-color: var(--border-color) !important;
        }

        /* Markdown text */
        .stMarkdown h3,
        .stMarkdown h4,
        .stMarkdown p,
        .stMarkdown li {
            color: var(--text-color) !important;
        }

        /* Dataframe styling */
        .stDataFrame {
            background-color: var(--background-color) !important;
        }
        .stDataFrame > div > div > div > div {
            color: var(--text-color) !important;
            background-color: var(--background-color) !important;
        }

        /* Buttons */
        .stButton > button {
            color: var(--text-color) !important;
            background-color: var(--primary-color) !important;
            border-color: var(--border-color) !important;
        }

        /* Progress bar */
        .stProgress > div > div > div {
            background-color: var(--primary-color) !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # Create tabs for different sections
    tab1, tab2 = st.tabs(["Extract Emails", "Help & Info"])

    with tab1:
        # Input fields in a clean layout
        st.markdown("### Account Information")

        # Use columns for a cleaner layout
        col1, col2 = st.columns(2)
        with col1:
            email_id = st.text_input("Email ID", placeholder="example@gmail.com", help="Your Gmail address")
        with col2:
            app_password = st.text_input("App Password", type="password", help="Your app-specific password")

        # Folder selection
        folder = st.radio(
            "Select Folder",
            ["Sent", "Inbox", "Failure/Delay"],
            horizontal=True,
            help="Choose to extract from your sent emails, received emails, or emails labeled as failure/delay"
        )

        # Filter options in a clean layout
        st.markdown("### Filter Options")

        # Date range filters in two columns
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=datetime.now().date() - timedelta(days=30),  # Default to 30 days ago
                help="Only extract emails sent on or after this date"
            )
        with col2:
            end_date = st.date_input(
                "End Date (Optional)",
                value=None,  # Default to None (no end date filter)
                help="Only extract emails sent on or before this date (leave empty for no upper limit)"
            )

        # Subject filter
        subject_filter = st.text_input(
            "Subject Filter (optional)",
            placeholder="Enter keywords to filter by subject",
            help="Only extract emails containing these words in the subject line"
        )

        # Extract button
        extract_col1, extract_col2, extract_col3 = st.columns([1, 2, 1])
        with extract_col2:
            extract_button = st.button("Extract Emails", type="primary", use_container_width=True)

        if extract_button:
            if email_id and app_password:
                try:
                    # Show date range info
                    date_range_text = f"from {start_date}"
                    if end_date:
                        date_range_text += f" to {end_date}"

                    # Extract emails with progress
                    with st.spinner(f"Extracting Email ids from {folder} folder..."):
                        # Create a progress bar
                        progress_bar = st.progress(0)
                        status_text = st.empty()

                        # Show thread mapping message
                        status_text.text("Analyzing email threads for accurate response tracking...")
                        progress_bar.progress(25)

                        # Extract emails with optimized settings
                        emails = extract_emails(
                            email_id=email_id,
                            app_password=app_password,
                            start_date=start_date,
                            end_date=end_date,
                            folder=folder,
                            batch_size=100,  # Process 100 emails at a time
                            max_emails=3000,  # Allow up to 3000 emails
                            subject_filter=subject_filter if subject_filter else None
                        )

                        # Update progress
                        progress_bar.progress(100)
                        status_text.text("Extraction complete!")

                        if emails:
                            # Convert to DataFrame
                            df = pd.DataFrame(emails)

                            # Apply client-side subject filtering if provided
                            if subject_filter and not df.empty and 'Subject' in df.columns:
                                # Case-insensitive subject filtering
                                df = df[df['Subject'].str.contains(subject_filter, case=False, na=False)]
                                if df.empty:
                                    st.warning(f"No emails found with subject containing '{subject_filter}' in the {folder} folder.")
                                    return

                            # Store in session state
                            st.session_state.extracted_emails = {
                                'data': df,
                                'folder': folder,
                                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }

                            # Show success message
                            st.success(f"Successfully extracted {len(df)} emails from {folder} folder")

                            # Show data preview in a scrollable container
                            st.markdown("### Email Data")
                            st.markdown("""
                            <style>
                                .dataframe-container {
                                    max-height: 400px;
                                    overflow-y: auto;
                                    border: 1px solid var(--border-color);
                                    border-radius: 5px;
                                    padding: 5px;
                                }
                            </style>
                            """, unsafe_allow_html=True)

                            with st.container():
                                st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
                                st.dataframe(
                                    df,
                                    height=350,
                                    use_container_width=True,
                                    hide_index=True
                                )
                                st.markdown('</div>', unsafe_allow_html=True)

                            # Add visualization section
                            st.markdown("### 📊 Email Analysis")

                            # Create two columns for visualization
                            col1, col2 = st.columns([2, 1])

                            with col1:
                                # Calculate response statistics (if applicable for the folder)
                                if 'Status' in df.columns:
                                    total_emails = len(df)
                                    responded_count = len(df[df['Status'] == 'Responded'])
                                    not_responded_count = len(df[df['Status'] == 'Not Responded'])

                                    # Create pie chart data
                                    chart_data = pd.DataFrame({
                                        'Status': ['Responded', 'Not Responded'],
                                        'Count': [responded_count, not_responded_count]
                                    })

                                    # Create pie chart
                                    fig = create_pie_chart(
                                        chart_data,
                                        value_column='Count',
                                        names_column='Status',
                                        title="Email Response Status",
                                        color_map={'Responded': '#28a745', 'Not Responded': '#dc3545'}
                                    )

                                    # Display pie chart
                                    st.plotly_chart(fig)

                            with col2:
                                # Show statistics
                                if 'Status' in df.columns:
                                    st.markdown("""
                                    #### Response Statistics
                                    - **Total Emails:** {}
                                    - **Responded:** {} ({:.1f}%)
                                    - **Not Responded:** {} ({:.1f}%)
                                    """.format(
                                        total_emails,
                                        responded_count, (responded_count/total_emails*100),
                                        not_responded_count, (not_responded_count/total_emails*100)
                                    ))

                            # Show download button
                            csv = df.to_csv(index=False)
                            st.download_button(
                                label="Download CSV",
                                data=csv,
                                file_name=f"extracted_emails_{folder}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv"
                            )
                        else:
                            st.warning("No emails found matching the criteria")
                except Exception as e:
                    st.error(f"Error extracting emails: {str(e)}")
            else:
                st.error("Please enter your email ID and app password")

        # Show previous results if available
        elif 'extracted_emails' in st.session_state:
            folder_name = st.session_state['extracted_emails'].get('folder', 'inbox')
            df_previous = st.session_state['extracted_emails']['data']
            st.info(f"Showing previous extraction results from {folder_name} folder. Extract again to update.")
            display_extraction_results(df_previous, folder_name)

    with tab2:
        st.markdown("### Email Extractor Help")

        st.markdown("""
        #### How to Use the Email Extractor

        1. Enter your Gmail email address and app password
        2. Select whether to extract from "Sent" emails, "Inbox" (received emails), or "Failure/Delay" labeled emails.
        3. Set a date range to filter emails:
            - Start Date: Only include emails from this date onwards
            - End Date: Optionally limit to emails before this date
        4. Optionally, enter subject keywords to filter emails by subject
        5. Click "Extract Emails" to begin the extraction process

        #### What Gets Extracted

        When extracting from **Sent** folder:
        - Recipient names and email addresses
        - Email dates and subjects
        - Response status (whether recipients have replied)

        When extracting from **Inbox**:
        - Sender names and email addresses
        - Email dates and subjects
        - Response status (whether emails have been responded to)

        When extracting from **Failure/Delay**:
        - Sender/Recipient names and email addresses (where available)
        - Original recipient email address (if a delivery failure notification)
        - Email dates and subjects
        - Response status (generally 'Not Responded' for these types of emails)

        #### Limitations

        - Only processes up to 3000 emails at once for performance reasons
        - Only extracts from Gmail accounts (other providers coming soon)
        - Processes only email headers for faster extraction, not full content
        - The "Failure/Delay" option relies on your Gmail labels being named exactly 'Failure' and 'Delay'.

        #### Privacy

        Your email credentials are used only during the current session and are never stored or saved.
        """)

def display_extraction_results(df, folder):
    """Display the extraction results with data table and visualization"""
    # Results header
    st.markdown("### Extraction Results")

    # Configure columns based on the folder type
    if folder == 'sent':
        column_config = {
            "Sender Name": st.column_config.TextColumn("Sender Name"),
            "Sender Email": st.column_config.TextColumn("Sender Email"),
            "Recipient Name": st.column_config.TextColumn("Recipient Name"),
            "Recipient Email": st.column_config.TextColumn("Recipient Email"),
            "Date": st.column_config.TextColumn("Date Sent"),
            "Subject": st.column_config.TextColumn("Subject"),
            "Status": st.column_config.TextColumn("Response Status")
        }
    elif folder == 'inbox':
        column_config = {
            "Sender Name": st.column_config.TextColumn("Sender Name"),
            "Sender Email": st.column_config.TextColumn("Sender Email"),
            "Recipient Name": st.column_config.TextColumn("Recipient Name"),
            "Recipient Email": st.column_config.TextColumn("Recipient Email"),
            "Date": st.column_config.TextColumn("Date Received"),
            "Subject": st.column_config.TextColumn("Subject"),
            "Status": st.column_config.TextColumn("Response Status")
        }
    elif folder == 'Failure/Delay':
        column_config = {
            "Sender Name": st.column_config.TextColumn("Sender Name"),
            "Sender Email": st.column_config.TextColumn("Sender Email"),
            "Recipient Name": st.column_config.TextColumn("Recipient Name"),
            "Recipient Email": st.column_config.TextColumn("Recipient Email"),
            "Date": st.column_config.TextColumn("Date"),
            "Subject": st.column_config.TextColumn("Subject"),
            "Original Recipient Email": st.column_config.TextColumn("Original Recipient (if failure)"),
            "Status": st.column_config.TextColumn("Status")
        }
    else:
        column_config = None

    # Show data preview in a scrollable container
    st.markdown("""
    <style>
        .dataframe-container {
            max-height: 400px;
            overflow-y: auto;
            border: 1px solid var(--border-color);
            border
