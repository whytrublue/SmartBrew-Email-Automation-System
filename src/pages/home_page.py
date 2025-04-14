"""
Home Page Module for SmartBrew Email Automation System
Contains the home page with feature selection and FAQs
"""

import streamlit as st

def show_home_page():
    """Display the home page with feature selection and FAQ section"""
    st.subheader("Welcome to SmartBrew Email Automation")
    
    # Feature selection
    st.markdown("### Select a Feature")
    st.markdown("Choose one of our powerful email automation tools:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="border:1px solid #DDDDDD; border-radius:5px; padding:15px;">
        <h4 style="text-align:center;">📧 Email Extractor</h4>
        <p>Extract email data from your inbox, filter by date and subject, and analyze response rates.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Use Email Extractor", key="btn_extractor", use_container_width=True):
            st.session_state.current_page = 'Email Extractor'
    
    with col2:
        st.markdown("""
        <div style="border:1px solid #DDDDDD; border-radius:5px; padding:15px;">
        <h4 style="text-align:center;">📨 Bulk Email Sender</h4>
        <p>Send personalized emails individually or in bulk with professional templates and tracking.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Use Bulk Email Sender", key="btn_sender", use_container_width=True):
            st.session_state.current_page = 'Bulk Email Sender'
    
    with col3:
        st.markdown("""
        <div style="border:1px solid #DDDDDD; border-radius:5px; padding:15px;">
        <h4 style="text-align:center;">🔍 Campaign Matcher</h4>
        <p>Match campaigns with follow-ups, track response rates, and analyze executive performance.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Use Campaign Matcher", key="btn_matcher", use_container_width=True):
            st.session_state.current_page = 'Campaign Matcher'
    
    # FAQ Section
    st.markdown("### Frequently Asked Questions")
    
    with st.expander("What is SmartBrew email automation?"):
        st.write("SmartBrew email automation is a comprehensive tool designed to streamline email communication processes for organizations. It helps extract email data, send bulk personalized emails, and match campaign responses effectively.")
    
    with st.expander("Is my personal data stored in this app?"):
        st.write("No personal data is stored in this app. Your email credentials are used only during the active session to perform the requested operations and are not saved anywhere.")
    
    with st.expander("What is an app password?"):
        st.write("""
        An app password is a 16-digit passcode that gives a less secure app or device permission to access your Google Account. 
        
        To create an app password:
        1. Go to your Google Account security settings
        2. Turn on 2-Step Verification if it's not already on
        3. Select "App passwords" under "Signing in to Google"
        4. Generate a new app password specifically for this application
        
        App passwords are recommended instead of your regular account password when using email automation tools.
        """)
    
    with st.expander("How many emails can I send at one click and in a day?"):
        st.write("You can send up to 500 emails in one click. Most email providers limit sending to 2000 emails per day from a single account.")
    
    with st.expander("Is there any break I have to take between email batches?"):
        st.write("Yes, it's recommended to take a 60-minute break after sending 100 emails to avoid being flagged as spam by email service providers. Our system will automatically pause between batches if you choose to send more than 100 emails at once.")
    
    with st.expander("Can I use my custom email templates?"):
        st.write("Yes, you can use your own custom email templates or choose from our predefined templates for different scenarios. The system supports dynamic field replacement for personalization.")
    
    with st.expander("What file formats are supported for attachments?"):
        st.write("You can attach PDF, DOCX, JPG, and PNG files to your emails. Other file formats may be supported by your email provider but are not currently supported by our application.")
    
    with st.expander("How do I format my CSV file for bulk sending?"):
        st.write("""
        Your CSV file should include at minimum the following columns:
        - Email: Recipient email addresses
        - Name: Recipient names (optional, but recommended for personalization)
        
        You can download a sample CSV template from the Bulk Email Sender page.
        """) 