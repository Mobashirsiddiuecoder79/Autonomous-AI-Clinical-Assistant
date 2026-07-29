import os
import streamlit as st

from database.connection import init_db

from frontend.components.sidebar import render_sidebar

from frontend.views.dashboard import show_dashboard
from frontend.views.chat import show_chat
from frontend.views.reports import show_reports
from frontend.views.settings import show_settings


# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="AI Clinical Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================================
# DATABASE INITIALIZATION
# ==========================================================

init_db()


# ==========================================================
# LOAD CUSTOM CSS
# ==========================================================

css_path = "frontend/styles.css"

if os.path.exists(css_path):

    with open(css_path, "r", encoding="utf-8") as css_file:

        st.markdown(
            f"<style>{css_file.read()}</style>",
            unsafe_allow_html=True
        )


# ==========================================================
# SIDEBAR
# ==========================================================

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

    show_settings()

else:

    st.error("Unknown page selected.")

    show_dashboard()


# ==========================================================
# FOOTER
# ==========================================================


from frontend.components.header import page_footer

st.divider()

page_footer()