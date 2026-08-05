import streamlit as st
from contextlib import contextmanager


# ==========================================================
# PAGE HEADER
# ==========================================================

def page_header(
    title: str,
    subtitle: str = "",
    icon: str = "🏥"
):
    """
    Modern page header.
    """

    st.markdown(
        f"""
<div class="page-header">

<div style="display:flex;align-items:center;gap:18px;">

<div style="
font-size:54px;
line-height:1;">
{icon}
</div>

<div>

<div class="page-title">
{title}
</div>

<div class="page-subtitle">
{subtitle}
</div>

</div>

</div>

</div>
""",
        unsafe_allow_html=True,
    )


# ==========================================================
# SECTION HEADER
# ==========================================================

def section_header(
    title: str,
    subtitle: str = ""
):
    """
    Section title used inside pages.
    """

    st.markdown(
        f"""
<div class="mb-20">

<div class="section-title">
{title}
</div>

<div class="section-subtitle">
{subtitle}
</div>

</div>
""",
        unsafe_allow_html=True,
    )


# ==========================================================
# STATUS BADGE
# ==========================================================

def status_badge(
    text: str,
    status: str = "success"
):
    """
    status:
        success
        warning
        danger
        primary
    """

    badge_map = {
        "success": "badge-success",
        "warning": "badge-warning",
        "danger": "badge-danger",
        "primary": "badge-primary",
    }

    badge = badge_map.get(status, "badge-primary")

    st.markdown(
        f"""
<span class="badge {badge}">
{text}
</span>
""",
        unsafe_allow_html=True,
    )


# ==========================================================
# AI ENGINE CARD
# ==========================================================

def ai_engine_card():
    """
    Sidebar / dashboard AI status.
    """

    st.markdown(
        """
<div class="engine-card">

<div class="engine-title">
🧠 AI Engine
</div>

<div class="engine-row">
<span>LLM</span>
<span>GPT-5.5</span>
</div>

<div class="engine-row">
<span>Vector Memory</span>
<span>FAISS</span>
</div>

<div class="engine-row">
<span>Database</span>
<span>SQLite</span>
</div>

<div class="engine-row">
<span>Framework</span>
<span>LangGraph</span>
</div>

<div class="engine-row">
<span>Status</span>
<span style="color:#22C55E;">● Online</span>
</div>

</div>
""",
        unsafe_allow_html=True,
    )


# ==========================================================
# GLASS CARD
# ==========================================================

@contextmanager
def glass_card():
    """
    Usage:

    with glass_card():

        st.write(...)
    """

    st.markdown(
        '<div class="glass-card">',
        unsafe_allow_html=True,
    )

    yield

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


# ==========================================================
# PAGE DIVIDER
# ==========================================================

def page_divider():

    st.markdown(
        '<div class="sidebar-divider"></div>',
        unsafe_allow_html=True,
    )


# ==========================================================
# FOOTER
# ==========================================================

def page_footer():

    st.markdown(
        """
<div class="app-footer">

<strong>
🏥 AI Clinical Assistant
</strong>

<br><br>

Modern Autonomous Healthcare Decision Support Platform

<br><br>

Built with
<b>Streamlit</b> •
<b>LangGraph</b> •
<b>OpenAI</b> •
<b>FAISS</b> •
<b>SQLAlchemy</b>

<br><br>

Version 3.0.0

</div>
""",
        unsafe_allow_html=True,
    )