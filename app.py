import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


import streamlit as st

st.set_page_config(
    page_title="Smart Interview System",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar navigation
st.sidebar.title("🎯 Smart Interview")
st.sidebar.markdown("---")

page = st.sidebar.radio("Navigate", [
    "🏠 Home",
    "📋 Start Interview",
    "📊 Recruiter Dashboard"
])

# Route to correct page
if page == "🏠 Home":
    from pages.home import show
    show()
elif page == "📋 Start Interview":
    from pages.interview import show
    show()
elif page == "📊 Recruiter Dashboard":
    from pages.dashboard import show
    show()