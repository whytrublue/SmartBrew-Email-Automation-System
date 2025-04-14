"""
SmartBrew Email Automation System
Main application entry point
"""

import streamlit as st
import os
import dotenv

# Load environment variables if .env file exists
if os.path.exists('.env'):
    dotenv.load_dotenv()

# Import components and pages
from src.components.ui_components import configure_theme, display_header, display_footer, create_sidebar_navigation
from src.pages.home_page import show_home_page
from src.pages.email_extractor_page import show_email_extractor_page
from src.pages.bulk_email_sender_page import show_bulk_email_sender_page
from src.pages.campaign_matcher_page import show_campaign_matcher_page

# Set page configuration
st.set_page_config(
    page_title="SmartBrew Email Automation",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application entry point"""
    # Configure theme
    configure_theme()
    
    # Display header
    display_header()
    
    # Create sidebar navigation
    create_sidebar_navigation()
    
    # Render the current page
    if st.session_state.current_page == "Home":
        show_home_page()
    elif st.session_state.current_page == "Email Extractor":
        show_email_extractor_page()
    elif st.session_state.current_page == "Bulk Email Sender":
        show_bulk_email_sender_page()
    elif st.session_state.current_page == "Campaign Matcher":
        show_campaign_matcher_page()
    
    # Display footer
    display_footer()

if __name__ == "__main__":
    main() 