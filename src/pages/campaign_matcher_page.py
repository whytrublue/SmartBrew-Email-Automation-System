"""
Campaign Matcher Page Module for SmartBrew Email Automation System
Handles the UI and functionality for matching campaigns
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Import utility functions
from src.utils.campaign_matcher import match_campaigns
from src.components.ui_components import create_pie_chart, get_csv_download_link

def show_campaign_matcher_page():
    """Display the Campaign Matcher page with all functionality"""
    st.subheader("🔍 Campaign Matcher")
    
    # Create a professional card-like container
    st.markdown("""
    <div style="padding: 10px; border-radius: 10px; background-color: var(--background-color); border: 1px solid var(--border-color);">
    <p style="color: var(--text-color); margin: 0;">Match campaigns with follow-ups based on CC fields and track response rates by executive.</p>
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
        
        /* Charts and visualizations */
        .stPlotlyChart {
            background-color: var(--background-color) !important;
        }
        .js-plotly-plot {
            background-color: var(--background-color) !important;
        }
        .plot-container {
            background-color: var(--background-color) !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Create tabs for different sections
    tab1, tab2 = st.tabs(["Match Campaigns", "Help & Info"])
    
    with tab1:
        # Input fields in a clean layout
        st.markdown("### Account Information")
        
        # Use columns for a cleaner layout
        col1, col2 = st.columns(2)
        with col1:
            campaign_email = st.text_input(
                "Campaign Email", 
                placeholder="campaign@smartbrew.com",
                help="Email account used for the campaign"
            )
            app_password = st.text_input(
                "App Password", 
                type="password", 
                key="campaign_password",
                help="App-specific password for authentication"
            )
        with col2:
            executive_email = st.text_input(
                "Executive Email (optional)", 
                placeholder="executive@smartbrew.com",
                help="Filter campaigns that have this executive in CC"
            )
        
        # Filter options in a clean layout
        st.markdown("### Filter Options")
        
        # Date range filters
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date", 
                value=datetime.now().date() - timedelta(days=30),  # Default to 30 days ago
                key="campaign_start_date",
                help="Only match campaigns sent on or after this date"
            )
        with col2:
            end_date = st.date_input(
                "End Date (Optional)", 
                value=None,
                key="campaign_end_date",
                help="Only match campaigns sent on or before this date (leave empty for no upper limit)"
            )
            
        # Subject filter
        subject_filter = st.text_input(
            "Subject Filter (optional)", 
            key="campaign_subject",
            placeholder="Enter keywords to filter by subject",
            help="Only match campaigns containing these words in the subject line"
        )
        
        # Match button
        match_col1, match_col2, match_col3 = st.columns([1, 2, 1])
        with match_col2:
            match_button = st.button("Match Campaigns", type="primary", use_container_width=True)
        
        if match_button:
            if campaign_email and app_password:
                try:
                    # Format date range text for display
                    date_range_text = f"from {start_date}"
                    if end_date:
                        date_range_text += f" to {end_date}"
                        
                    with st.spinner(f"Matching campaigns {date_range_text}... This may take a few minutes."):
                        # Use the campaign matcher utility
                        df = match_campaigns(
                            campaign_email, app_password, 
                            executive_email, start_date, end_date, subject_filter
                        )
                        
                        # Check if we got results
                        if len(df) > 0:
                            # Store results in session state for reuse
                            st.session_state.matched_df = df
                            st.session_state.has_matching_results = True
                            
                            # Show results
                            show_matching_results(df, executive_email, date_range_text)
                        else:
                            st.warning(f"No matching campaigns found {date_range_text}. Try different filter criteria or check account settings.")
                except Exception as e:
                    error_msg = str(e)
                    if "authentication failed" in error_msg.lower():
                        st.error("Authentication failed. Please check your email and app password.")
                    elif "could not access sent mail folder" in error_msg.lower():
                        st.error("Could not access the sent mail folder. Please verify account permissions.")
                    elif "connection" in error_msg.lower():
                        st.error("Connection error. Please check your internet connection and try again.")
                    else:
                        st.error(f"Error matching campaigns: {error_msg}")
                    
                    # Add help text
                    st.info("Tips: Make sure you've enabled IMAP in your Gmail settings and are using an app-specific password.")
            else:
                st.error("Please enter campaign email and app password")
        
        # Show previous results if available
        elif 'has_matching_results' in st.session_state and st.session_state.has_matching_results:
            if 'matched_df' in st.session_state:
                st.info("Showing previous matching results. Match again to update.")
                show_matching_results(st.session_state.matched_df, executive_email)
    
    with tab2:
        st.markdown("### Campaign Matcher Help")
        
        st.markdown("""
        #### How the Campaign Matcher Works
        
        The Campaign Matcher analyzes emails sent from your campaign account and tracks:
        
        1. Which emails included specific executives in the CC field
        2. Whether those emails received responses
        3. Overall campaign response rates
        
        This helps you identify:
        - Which executives are most effective in campaigns
        - Which types of emails get the best response rates
        - Follow-up opportunities for non-responsive contacts
        
        #### Using the Results
        
        The matched campaigns data can be used to:
        
        - Identify follow-up opportunities
        - Analyze executive performance
        - Refine targeting strategies
        - Improve email templates based on response rates
        
        #### Advanced Filtering
        
        You can filter results by:
        
        - Date range: Filter campaigns between specific dates
        - Subject keywords: Filter by campaign type
        - Executive: See performance by team member
        
        For best results, use specific date ranges and executive filters to focus your analysis.
        """)

def show_matching_results(df, executive_email, date_range_text=None):
    """Display the matching results with data table and visualization"""
    # Check for empty dataframe
    if df.empty:
        st.warning("No matching data found. Try different filter criteria.")
        return
        
    # Determine match type for message
    match_text = f"where {executive_email} was CC'd" if executive_email else "from the sent folder"
    if date_range_text:
        match_text += f" {date_range_text}"
    
    # Display success message
    st.success(f"Successfully matched {len(df)} campaigns {match_text}")
    
    # Results header
    st.markdown("### Matching Results")
    
    # Show dataframe with some styling
    st.dataframe(
        df,
        column_config={
            "Name": st.column_config.TextColumn("Organization Name"),
            "Follow-up Email": st.column_config.TextColumn("Email Address"),
            "Date": st.column_config.TextColumn("Date Sent"),
            "Subject": st.column_config.TextColumn("Subject Line"),
            "Status": st.column_config.TextColumn("Response Status"),
            "Executive Name": st.column_config.TextColumn("Executive")
        },
        use_container_width=True,
        hide_index=True
    )
    
    # Visualization and download section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Provide download link
        st.markdown(get_csv_download_link(df, "campaign_matches.csv"), unsafe_allow_html=True)
        
        # Show some basic stats
        responded = df[df['Status'] == 'Responded'].shape[0]
        not_responded = df[df['Status'] == 'Not Responded'].shape[0]
        total = len(df)
        
        st.markdown(f"""
        #### Campaign Statistics
        - Total Campaigns: {total}
        - Responded: {responded} ({round(responded/total*100 if total > 0 else 0, 1)}%)
        - Not Responded: {not_responded} ({round(not_responded/total*100 if total > 0 else 0, 1)}%)
        """)
        
        # Add executive performance if we have multiple executives
        if 'Executive Name' in df.columns and df['Executive Name'].nunique() > 1:
            try:
                st.markdown("#### Executive Performance")
                exec_stats = df.groupby(['Executive Name', 'Status']).size().unstack(fill_value=0)
                
                if not exec_stats.empty and 'Responded' in exec_stats.columns and 'Not Responded' in exec_stats.columns:
                    exec_stats['Total'] = exec_stats['Responded'] + exec_stats['Not Responded']
                    exec_stats['Response Rate'] = round(exec_stats['Responded'] / exec_stats['Total'] * 100, 1)
                    
                    # Reset index for display
                    exec_stats = exec_stats.reset_index()
                    
                    # Show the stats
                    st.dataframe(
                        exec_stats,
                        column_config={
                            "Executive Name": "Executive",
                            "Responded": st.column_config.NumberColumn("Responded"),
                            "Not Responded": st.column_config.NumberColumn("Not Responded"),
                            "Total": st.column_config.NumberColumn("Total"),
                            "Response Rate": st.column_config.NumberColumn("Response Rate (%)")
                        }
                    )
            except Exception as e:
                # Skip executive performance if there's an error
                st.warning("Could not analyze executive performance data.")
    
    with col2:
        try:
            # Create and display pie chart
            if 'Status' in df.columns:
                status_counts = df['Status'].value_counts().reset_index()
                status_counts.columns = ['Status', 'Count']
                
                fig = create_pie_chart(
                    status_counts,
                    value_column='Count',
                    names_column='Status',
                    title="Follow-up Response Status",
                    color_map={'Responded': 'green', 'Not Responded': 'orange'}
                )
                
                st.plotly_chart(fig)
            
            # If we have executive data, show another chart
            if 'Executive Name' in df.columns and df['Executive Name'].nunique() > 1:
                # Group by executive
                exec_data = df.groupby('Executive Name')['Status'].value_counts().unstack(fill_value=0)
                
                if not exec_data.empty and 'Responded' in exec_data.columns:
                    exec_data = exec_data.reset_index()
                    # Find the top performing executive
                    top_exec = exec_data.loc[exec_data['Responded'].idxmax()]['Executive Name']
                    st.info(f"Top performing executive: {top_exec}")
        except Exception:
            # If visualization fails, don't show it
            st.warning("Could not create visualizations for this data.") 
            st.warning("Could not create visualizations for this data.") 