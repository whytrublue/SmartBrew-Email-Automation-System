"""
UI Components Module for SmartBrew Email Automation System
Contains reusable UI components for the Streamlit interface
"""

import streamlit as st
import base64
import plotly.express as px
from PIL import Image
import os

# Theme settings
def configure_theme():
    """Configure and apply the current theme settings"""
    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'
        
    # Apply theme
    if st.session_state.theme == 'dark':
        st.markdown("""
        <style>
        .main {
            background-color: #121212;
            color: white !important;
        }
        .stApp {
            background-color: #121212;
        }
        .stTextInput > div > div > input {
            color: white;
        }
        .stTextArea textarea {
            color: white;
        }
        .stMarkdown {
            color: white;
        }
        .stSelectbox, .stMultiselect {
            color: white;
        }
        .st-cb, .st-bq, .st-ae, .st-af, .st-ag, .st-ah, .st-ai, .st-aj, .st-ak, .st-al {
            color: white !important;
        }
        .st-c3, .st-c4, .st-c5, .st-c6, .st-c7, .st-c8, .st-c9, .st-ca, .st-cb, .st-cc {
            color: white !important;
        }
        .css-145kmo2, .css-1aehpvj, .css-81oif8, .css-16idsys {
            color: white !important;
        }
        .block-container {
            background-color: #1E1E1E;
        }
        h1, h2, h3, h4, h5, h6 {
            color: white !important;
        }
        .stTabs [data-baseweb="tab-list"] {
            background-color: #2C2C2C;
        }
        .stTabs [data-baseweb="tab"] {
            color: white;
        }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        .main {
            background-color: white;
            color: black !important;
        }
        .stApp {
            background-color: white;
        }
        .stTextInput > div > div > input {
            color: black;
        }
        .stTextArea textarea {
            color: black;
        }
        .stMarkdown {
            color: black;
        }
        .stSelectbox, .stMultiselect {
            color: black;
        }
        .block-container {
            background-color: #F8F8F8;
        }
        h1, h2, h3, h4, h5, h6 {
            color: black !important;
        }
        .stTabs [data-baseweb="tab-list"] {
            background-color: #F0F0F0;
        }
        .stTabs [data-baseweb="tab"] {
            color: black;
        }
        </style>
        """, unsafe_allow_html=True)

def toggle_theme():
    """Toggle between light and dark theme"""
    if st.session_state.theme == 'light':
        st.session_state.theme = 'dark'
    else:
        st.session_state.theme = 'light'

# Header component
def display_header():
    """Display the application header with logo and theme toggle"""
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        # Use logo from assets or a placeholder
        logo_path = os.path.join("assets", "logo.png")
        if os.path.exists(logo_path):
            logo = Image.open(logo_path)
            st.image(logo, width=150)
        else:
            st.image("https://via.placeholder.com/150x80?text=SmartBrew", width=150)
    
    with col2:
        title_color = "white" if st.session_state.theme == 'dark' else "black"
        st.markdown(f'<h1 style="color: {title_color}; text-align: center;">SmartBrew Email Automation System</h1>', unsafe_allow_html=True)
    
    with col3:
        theme_button_text = "🌙 Dark" if st.session_state.theme == 'light' else "☀️ Light"
        st.button(theme_button_text, on_click=toggle_theme)

# Footer component
def display_footer():
    """Display the application footer"""
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("© 2025 SmartBrew Email Automation System. All rights reserved.")
    with col2:
        support_email = "giridhar.chennuru@smartbrew.in"
        # Create a clickable mailto link for the support email
        st.markdown(f'For support: <a href="mailto:{support_email}">{support_email}</a>', unsafe_allow_html=True)

# Navigation
def create_sidebar_navigation():
    """Create sidebar navigation menu"""
    with st.sidebar:
        st.title("Navigation")
        
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'Home'
            
        # Navigation buttons
        if st.button("🏠 Home", key="nav_home", use_container_width=True):
            st.session_state.current_page = 'Home'
            
        if st.button("📧 Email Extractor", key="nav_extractor", use_container_width=True):
            st.session_state.current_page = 'Email Extractor'
            
        if st.button("📨 Bulk Email Sender", key="nav_sender", use_container_width=True):
            st.session_state.current_page = 'Bulk Email Sender'
            
        if st.button("🔍 Campaign Matcher", key="nav_matcher", use_container_width=True):
            st.session_state.current_page = 'Campaign Matcher'
        
        # Add some space for better appearance
        st.markdown("---")
        st.markdown("### Quick Help")
        with st.expander("How to Use"):
            st.write("Select a feature from the navigation menu to get started. Each feature requires email credentials for authentication.")

# Data visualization
def create_pie_chart(data, value_column, names_column, title, color_map=None):
    """
    Create a pie chart for data visualization
    
    Parameters:
    -----------
    data : pandas.DataFrame or dict
        Data to visualize
    value_column : str
        Column name or key for values
    names_column : str
        Column name or key for category names
    title : str
        Chart title
    color_map : dict, optional
        Color mapping for categories
    
    Returns:
    --------
    plotly.graph_objects.Figure
        Plotly figure object
    """
    if color_map is None:
        color_map = {'Responded': 'blue', 'Not Responded': 'red', 
                    'Successful': 'green', 'Bounced': 'red'}
    
    fig = px.pie(
        data,
        values=value_column,
        names=names_column,
        title=title,
        color=names_column,
        color_discrete_map=color_map
    )
    
    # Improve appearance for both themes
    fig.update_layout(
        width=400, 
        height=300,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(
            color='gray' if st.session_state.theme == 'dark' else 'black',
            size=12
        )
    )
    
    return fig

# CSV download link
def get_csv_download_link(df, filename="data.csv"):
    """
    Generate a download link for a dataframe
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Dataframe to convert to CSV
    filename : str
        Filename for the download
        
    Returns:
    --------
    str
        HTML link for downloading the CSV
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}" class="download-link">Download CSV File</a>'
    
    # Add styling based on theme
    if st.session_state.theme == 'dark':
        href = f'<style>.download-link {{ color: #4CAF50; text-decoration: none; padding: 5px 10px; border: 1px solid #4CAF50; border-radius: 4px; }}</style>{href}'
    else:
        href = f'<style>.download-link {{ color: #1E6B35; text-decoration: none; padding: 5px 10px; border: 1px solid #1E6B35; border-radius: 4px; }}</style>{href}'
        
    return href 