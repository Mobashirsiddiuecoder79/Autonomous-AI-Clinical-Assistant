import streamlit as st

from frontend.auth.authentication import (
    is_authenticated,
    get_authenticated_email,
)


PAGES = [
    ("🏠 Dashboard", "🏠 Dashboard"),
    ("🤖 AI Assistant", "🤖 AI Assistant"),
    ("🧪 Lab Reports", "🧪 Lab Reports"),
    ("⚙️ Settings", "⚙️ Settings"),
]


def is_admin():

    if not is_authenticated():
        return False

    authenticated_email = get_authenticated_email()

    if not authenticated_email:
        return False

    try:
        admin_email = st.secrets["admin"]["email"]
    except Exception:
        return False

    return (
        authenticated_email.strip().lower()
        == str(admin_email).strip().lower()
    )


if "navigation" not in st.session_state:
    st.session_state.navigation = "🏠 Dashboard"


def render_sidebar():

    with st.sidebar:

        st.markdown(
            """
<div class="sidebar-logo">

<div class="sidebar-logo-icon">
🏥
</div>

<div class="sidebar-title">
AI Clinical Assistant
</div>

<div class="sidebar-subtitle">
Autonomous Healthcare Platform
</div>

</div>
""",
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="sidebar-divider"></div>',
            unsafe_allow_html=True,
        )

        patient_id = st.session_state.get(
            "active_patient_id",
            None,
        )

        if patient_id:

            st.markdown(
                f"""
<div class="patient-card">

<div class="patient-label">
ACTIVE PATIENT
</div>

<div class="patient-id">
#{patient_id}
</div>

<div class="patient-status">

<div class="status-dot"></div>

Connected

</div>

</div>
""",
                unsafe_allow_html=True,
            )

        else:

            st.markdown(
                """
<div class="patient-card">

<div class="patient-label">
ACTIVE PATIENT
</div>

<div class="patient-id">
None
</div>

<div class="patient-status-offline">
No patient selected
</div>

</div>
""",
                unsafe_allow_html=True,
            )

        st.markdown(
            '<div class="sidebar-section-title">Navigation</div>',
            unsafe_allow_html=True,
        )

        for page, label in PAGES:

            if st.button(
                label,
                key=f"nav_{page}",
                use_container_width=True,
            ):
                st.session_state.navigation = page

        if is_admin():

            st.markdown(
                '<div class="sidebar-section-title">Administration</div>',
                unsafe_allow_html=True,
            )

            if st.button(
                "👥 Patients",
                key="nav_admin_patients",
                use_container_width=True,
            ):
                st.session_state.navigation = "👥 Patients"

        st.markdown(
            '<div class="sidebar-divider"></div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="sidebar-section-title">Quick Actions</div>',
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "➕ Patient",
                use_container_width=True,
            ):
                st.session_state.navigation = "🏠 Dashboard"

        with col2:

            if st.button(
                "💬 Chat",
                use_container_width=True,
            ):
                st.session_state.navigation = "🤖 AI Assistant"

        st.markdown(
            '<div class="sidebar-divider"></div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="sidebar-section-title">System Status</div>',
            unsafe_allow_html=True,
        )

        status = [
            ("Database", "🟢 Online"),
            ("AI Engine", "🟢 Ready"),
            ("Memory", "🟢 Active"),
            ("Tools", "🟢 Loaded"),
        ]

        for title, value in status:

            st.markdown(
                f"""
<div class="status-card-small">

<div>{title}</div>

<div class="status-online">
{value}
</div>

</div>
""",
                unsafe_allow_html=True,
            )

        st.markdown(
            '<div class="sidebar-divider"></div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            """
<div class="sidebar-footer">

Version <b>4.0.0</b>

<br><br>

<span>
AI Clinical Assistant
</span>

</div>
""",
            unsafe_allow_html=True,
        )

    return st.session_state.navigation
