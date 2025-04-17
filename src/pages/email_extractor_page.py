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
    <p style="color: var(--text-color); margin: 0;">Extract email data from your inbox or sent folder based on filters. Process up to 3000+ emails at once for detailed analysis.</p>
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
            ["Sent", "Inbox"],
            horizontal=True,
            help="Choose to extract from your sent emails or received emails"
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
                    with st.spinner("Extracting Email ids..."):
                        # Create a progress bar
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        # Extract emails with optimized settings
                        emails = extract_emails(
                            email_id=email_id,
                            app_password=app_password,
                            start_date=start_date,
                            end_date=end_date,
                            folder=folder,
                            batch_size=100,  # Process 100 emails at a time
                            max_emails=3000  # Allow up to 3000 emails
                        )
                        
                        # Update progress
                        progress_bar.progress(100)
                        status_text.text("Extraction complete!")
                        
                        if emails:
                            # Convert to DataFrame
                            df = pd.DataFrame(emails)
                            
                            # Store in session state
                            st.session_state.extracted_emails = {
                                'data': df,
                                'folder': folder,
                                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                            
                            # Show success message
                            st.success(f"Successfully extracted {len(df)} emails from {folder} folder")
                            
                            # Show data preview
                            st.dataframe(df.head())
                            
                            # Add visualization section
                            st.markdown("### 📊 Email Response Analysis")
                            
                            # Create two columns for visualization
                            col1, col2 = st.columns([2, 1])
                            
                            with col1:
                                # Calculate response statistics
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
        elif 'has_extraction_results' in st.session_state and st.session_state.has_extraction_results:
            if 'extracted_df' in st.session_state:
                folder_name = st.session_state.get('extraction_folder', 'inbox')
                st.info(f"Showing previous extraction results from {folder_name} folder. Extract again to update.")
                display_extraction_results(st.session_state.extracted_df, folder_name)
    
    with tab2:
        st.markdown("### Email Extractor Help")
        
        st.markdown("""
        #### How to Use the Email Extractor
        
        1. Enter your Gmail email address and app password
        2. Select whether to extract from "Sent" emails or "Inbox" (received emails)
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
        - How many times you've communicated with each sender
        - Response status (whether emails have been responded to)
        
        #### Limitations
        
        - Only processes up to 3000 emails at once for performance reasons
        - Only extracts from Gmail accounts (other providers coming soon)
        - Processes only email headers for faster extraction, not full content
        
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
            "Name": st.column_config.TextColumn("Recipient Name"),
            "Email": st.column_config.TextColumn("Recipient Email"),
            "Date": st.column_config.TextColumn("Date Sent"),
            "Subject": st.column_config.TextColumn("Subject"),
            "Status": st.column_config.TextColumn("Response Status")
        }
    else:
        column_config = {
            "Name": st.column_config.TextColumn("Sender Name"),
            "Email": st.column_config.TextColumn("Sender Email"),
            "Date": st.column_config.TextColumn("Date Received"),
            "Subject": st.column_config.TextColumn("Subject"),
            "Frequency": st.column_config.NumberColumn("Contact Frequency"),
            "Status": st.column_config.TextColumn("Response Status")
        }
    
    # Show dataframe with styled columns
    st.dataframe(
        df,
        column_config=column_config,
        use_container_width=True,
        hide_index=True
    )
    
    # Visualization and download section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Provide download link
        filename = f"extracted_emails_{folder}.csv"
        st.markdown(get_csv_download_link(df, filename), unsafe_allow_html=True)
        
        # Show some basic stats
        responded = df[df['Status'] == 'Responded'].shape[0]
        not_responded = df[df['Status'] == 'Not Responded'].shape[0]
        
        email_type = "recipients" if folder == 'sent' else "senders"
        st.markdown(f"""
        #### Quick Stats
        - Total Unique {email_type.title()}: {len(df)}
        - Responded: {responded} ({round(responded/len(df)*100 if len(df) > 0 else 0, 1)}%)
        - Not Responded: {not_responded} ({round(not_responded/len(df)*100 if len(df) > 0 else 0, 1)}%)
        """)
    
    with col2:
        # Create and display pie chart
        status_counts = df['Status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        
        title = "Response Status"
        fig = create_pie_chart(
            status_counts,
            value_column='Count',
            names_column='Status',
            title=title,
            color_map={'Responded': 'blue', 'Not Responded': 'red'}
        )
        
        st.plotly_chart(fig) 