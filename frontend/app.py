import os
import sys

# Add project root to Python path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st

from database.connection import init_db
from database import models
from frontend.views.admin import show_admin_patients

# ==========================================================
# DATABASE INITIALIZATION
# ==========================================================

# Create all database tables before authentication.
# This is required for fresh Streamlit Cloud deployments.
init_db()

from frontend.components.sidebar import render_sidebar

from frontend.views.dashboard import show_dashboard
from frontend.views.chat import show_chat
from frontend.views.reports import show_reports
from frontend.views.user_settings import render_user_settings
from frontend.auth.authentication import require_authentication

require_authentication()

# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="AI Clinical Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================================
# LOAD CUSTOM CSS
# ==========================================================

css_path = "frontend/styles.css"

if os.path.exists(css_path):

    with open(css_path, "r", encoding="utf-8") as css_file:

        st.markdown(
            f"<style>{css_file.read()}</style>",
            unsafe_allow_html=True,
        )

# ==========================================================
# SIDEBAR
# ==========================================================

if "navigation" not in st.session_state:
    st.session_state.navigation = "🏠 Dashboard"

navigation = render_sidebar()

# ==========================================================
# PAGE ROUTER
# ==========================================================

if navigation == "🏠 Dashboard":

    show_dashboard()

elif navigation == "🤖 AI Assistant":

    show_chat()

elif navigation == "🧪 Lab Reports":

    show_reports()

elif navigation == "⚙️ Settings":

    render_user_settings()

elif navigation == "👥 Patients":

    show_admin_patients()

else:

    st.error("Unknown page selected.")

    show_dashboard()

# ==========================================================
# FOOTER
# ==========================================================

from frontend.components.header import page_footer

st.divider()

page_footer()
