import streamlit as st


# ==========================================================
# SIDEBAR
# ==========================================================

PAGES = [
    ("🏠 Dashboard", "🏠 Dashboard"),
    ("🤖 AI Assistant", "🤖 AI Assistant"),
    ("🧪 Lab Reports", "🧪 Lab Reports"),
    ("⚙️ Settings", "⚙️ Settings"),
]


# ==========================================================
# INITIALIZE SESSION
# ==========================================================

if "navigation" not in st.session_state:
    st.session_state.navigation = "🏠 Dashboard"


# ==========================================================
# SIDEBAR
# ==========================================================

def render_sidebar():

    with st.sidebar:

        # --------------------------------------------------
        # LOGO
        # --------------------------------------------------

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

        # --------------------------------------------------
        # ACTIVE PATIENT
        # --------------------------------------------------

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

        # --------------------------------------------------
        # NAVIGATION
        # --------------------------------------------------

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

        st.markdown(
            '<div class="sidebar-divider"></div>',
            unsafe_allow_html=True,
        )

        # --------------------------------------------------
        # QUICK ACTIONS
        # --------------------------------------------------

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

        # --------------------------------------------------
        # SYSTEM STATUS
        # --------------------------------------------------

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

Version <b>2.0.0</b>

<br><br>

<span>
AI Clinical Assistant
</span>

</div>
""",
            unsafe_allow_html=True,
        )

    return st.session_state.navigation