import streamlit as st

from frontend.auth.authentication import logout
from database.connection import get_db
from database.models import Patient


def mask_email(email):
    if not email:
        return "Not available"

    if "@" not in email:
        return email

    name, domain = email.split("@", 1)

    if len(name) <= 2:
        masked_name = name[0] + "*"
    else:
        masked_name = name[0] + "*" * (len(name) - 2) + name[-1]

    return f"{masked_name}@{domain}"


def get_current_patient():
    patient_id = st.session_state.get("active_patient_id")

    if not patient_id:
        return None

    with get_db() as db:
        return (
            db.query(Patient)
            .filter(Patient.id == patient_id)
            .first()
        )


def render_user_settings():

    patient = get_current_patient()

    st.markdown(
        """
        <style>

        .settings-title {
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 4px;
        }

        .settings-subtitle {
            color: #6b7280;
            font-size: 15px;
            margin-bottom: 28px;
        }

        .profile-card {
            padding: 28px;
            border-radius: 18px;
            border: 1px solid rgba(128, 128, 128, 0.20);
            background: rgba(128, 128, 128, 0.04);
            margin-bottom: 22px;
        }

        .avatar {
            width: 82px;
            height: 82px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 30px;
            font-weight: 700;
            background: #e8f3ff;
            color: #1677c8;
            margin-bottom: 14px;
        }

        .profile-name {
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 4px;
        }

        .profile-email {
            color: #6b7280;
            font-size: 14px;
            margin-bottom: 8px;
        }

        .patient-id {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 8px;
            background: rgba(22, 119, 200, 0.10);
            color: #1677c8;
            font-size: 13px;
            font-weight: 600;
        }

        .section-title {
            font-size: 20px;
            font-weight: 700;
            margin-top: 8px;
            margin-bottom: 14px;
        }

        .info-label {
            color: #6b7280;
            font-size: 13px;
            margin-bottom: 3px;
        }

        .info-value {
            font-size: 15px;
            font-weight: 500;
            margin-bottom: 14px;
        }

        .security-card,
        .privacy-card,
        .about-card {
            padding: 22px;
            border-radius: 16px;
            border: 1px solid rgba(128, 128, 128, 0.20);
            background: rgba(128, 128, 128, 0.03);
            margin-bottom: 18px;
        }

        .privacy-item {
            margin: 8px 0;
            font-size: 14px;
        }

        .privacy-check {
            color: #16a34a;
            font-weight: 700;
        }

        .about-name {
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 5px;
        }

        .about-text {
            color: #6b7280;
            font-size: 14px;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="settings-title">⚙️ Settings</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="settings-subtitle">'
        "Manage your profile, account and privacy preferences."
        "</div>",
        unsafe_allow_html=True,
    )

    if patient is None:

        st.warning(
            "No patient profile is currently selected."
        )

        st.info(
            "Please select or create a patient profile from the Dashboard."
        )

        return

    first_name = patient.first_name or ""
    last_name = patient.last_name or ""

    full_name = f"{first_name} {last_name}".strip()

    initials = ""

    if first_name:
        initials += first_name[0].upper()

    if last_name:
        initials += last_name[0].upper()

    if not initials:
        initials = "U"

    # =====================================================
    # PROFILE
    # =====================================================

    st.markdown(
        '<div class="profile-card">',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="avatar">{initials}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="profile-name">{full_name}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="profile-email">{patient.email}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<span class="patient-id">'
        f'Patient ID: P-{patient.id:04d}'
        f"</span>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-title" style="margin-top:28px;">'
        "Personal Information"
        "</div>",
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)

    with c1:

        st.markdown(
            '<div class="info-label">First Name</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="info-value">{first_name}</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="info-label">Email</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="info-value">{patient.email}</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="info-label">Date of Birth</div>',
            unsafe_allow_html=True,
        )

        dob = (
            patient.date_of_birth.strftime("%d %B %Y")
            if patient.date_of_birth
            else "Not available"
        )

        st.markdown(
            f'<div class="info-value">{dob}</div>',
            unsafe_allow_html=True,
        )

    with c2:

        st.markdown(
            '<div class="info-label">Last Name</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="info-value">{last_name}</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="info-label">Gender</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="info-value">{patient.gender}</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="info-label">Member Since</div>',
            unsafe_allow_html=True,
        )

        created = (
            patient.created_at.strftime("%d %B %Y")
            if patient.created_at
            else "Not available"
        )

        st.markdown(
            f'<div class="info-value">{created}</div>',
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

    # =====================================================
    # EDIT PROFILE
    # =====================================================

    st.markdown(
        '<div class="section-title">✏️ Edit Profile</div>',
        unsafe_allow_html=True,
    )

    with st.expander(
        "Update your personal information",
        expanded=False
    ):

        with st.form("edit_profile_form"):

            e1, e2 = st.columns(2)

            with e1:

                new_first_name = st.text_input(
                    "First Name",
                    value=patient.first_name or "",
                )

                new_email = st.text_input(
                    "Email",
                    value=patient.email or "",
                )

            with e2:

                new_last_name = st.text_input(
                    "Last Name",
                    value=patient.last_name or "",
                )

                gender_options = [
                    "Male",
                    "Female",
                    "Other",
                    "Prefer not to say",
                ]

                current_gender = patient.gender or ""

                if current_gender not in gender_options:
                    gender_options = (
                        [current_gender]
                        + gender_options
                        if current_gender
                        else gender_options
                    )

                gender_index = (
                    gender_options.index(current_gender)
                    if current_gender in gender_options
                    else 0
                )

                new_gender = st.selectbox(
                    "Gender",
                    gender_options,
                    index=gender_index,
                )

            current_dob = patient.date_of_birth

            if current_dob:

                new_dob = st.date_input(
                    "Date of Birth",
                    value=current_dob,
                )

            else:

                new_dob = st.date_input(
                    "Date of Birth",
                    value=None,
                )

            st.caption(
                "Your profile information is stored in your patient record."
            )

            save_profile = st.form_submit_button(
                "💾 Save Changes",
                use_container_width=True,
                type="primary",
            )

            if save_profile:

                new_first_name = new_first_name.strip()
                new_last_name = new_last_name.strip()
                new_email = new_email.strip().lower()

                if not new_first_name:

                    st.error("First name cannot be empty.")

                elif not new_last_name:

                    st.error("Last name cannot be empty.")

                elif not new_email or "@" not in new_email:

                    st.error("Please enter a valid email address.")

                elif not new_dob:

                    st.error("Please select your date of birth.")

                else:

                    try:

                        with get_db() as db:

                            current_patient = (
                                db.query(Patient)
                                .filter(
                                    Patient.id
                                    == patient.id
                                )
                                .first()
                            )

                            if current_patient is None:

                                st.error(
                                    "Patient profile could not be found."
                                )

                            else:

                                duplicate_email = (
                                    db.query(Patient)
                                    .filter(
                                        Patient.email
                                        == new_email,
                                        Patient.id
                                        != patient.id,
                                    )
                                    .first()
                                )

                                if duplicate_email:

                                    st.error(
                                        "This email address is already "
                                        "associated with another patient."
                                    )

                                else:

                                    current_patient.first_name = (
                                        new_first_name
                                    )

                                    current_patient.last_name = (
                                        new_last_name
                                    )

                                    current_patient.email = (
                                        new_email
                                    )

                                    current_patient.gender = (
                                        new_gender
                                    )

                                    current_patient.date_of_birth = (
                                        new_dob
                                    )

                                    db.commit()

                                    st.success(
                                        "Profile updated successfully."
                                    )

                                    st.rerun()

                    except Exception as e:

                        st.error(
                            f"Unable to update profile: {e}"
                        )

    # =====================================================
    # ACCOUNT & SECURITY
    # =====================================================

    st.markdown(
        '<div class="security-card">',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-title">🔐 Account & Security</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="info-label">Authentication Status</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="info-value">Not connected</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div style="color:#6b7280; font-size:14px; '
        'margin-bottom:18px;">'
        'Your healthcare profile is currently managed locally. '
        'Secure account authentication will be available after '
        'authentication is configured.'
        '</div>',
        unsafe_allow_html=True,
    )

    if st.button(
        "🚪 Sign Out",
        use_container_width=True,
    ):
        logout()

    st.markdown("</div>", unsafe_allow_html=True)

    # =====================================================
    # PRIVACY
    # =====================================================

    st.markdown(
        '<div class="privacy-card">',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-title">🛡️ Privacy</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="privacy-item">'
        '<span class="privacy-check">✓</span> '
        "Your medical records are private"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="privacy-item">'
        '<span class="privacy-check">✓</span> '
        "Your medical reports are private"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="privacy-item">'
        '<span class="privacy-check">✓</span> '
        "Your conversations are private"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="privacy-item">'
        '<span class="privacy-check">✓</span> '
        "Your AI interactions are associated with your patient profile"
        "</div>",
        unsafe_allow_html=True,
    )

    st.divider()

    if st.button(
        "🗑️ Delete My Data",
        type="secondary",
    ):

        st.warning(
            "This action is currently disabled. "
            "Permanent data deletion should only be enabled "
            "after authentication and authorization are implemented."
        )

    st.markdown("</div>", unsafe_allow_html=True)

    # =====================================================
    # ABOUT
    # =====================================================

    st.markdown(
        '<div class="about-card">',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-title">ℹ️ About</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="about-name">'
        "Autonomous AI Clinical Assistant"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="about-text">'
        "AI-powered healthcare assistance for patient "
        "information, medical reports and clinical interactions."
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<br><div class="about-text">'
        "<b>Version:</b> 3.0"
        "<br>"
        "<b>AI:</b> Gemini"
        "<br>"
        "<b>Workflow:</b> LangGraph"
        "<br>"
        "<b>Database:</b> SQLAlchemy"
        "<br>"
        "<b>Vector Store:</b> FAISS"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)
