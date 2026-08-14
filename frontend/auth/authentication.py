import streamlit as st

from database.connection import get_db
from database.models import Patient


def is_authenticated():
    """
    Return True only when the user has successfully
    authenticated through the configured OIDC provider.
    """

    try:
        return bool(st.user.is_logged_in)
    except Exception:
        return False


def get_authenticated_email():
    """
    Get the email supplied by the authenticated identity provider.

    The email is NOT hardcoded in the application.
    """

    if not is_authenticated():
        return None

    try:
        email = st.user.get("email")
    except Exception:
        email = None

    if not email:
        return None

    return str(email).strip().lower()


def get_authenticated_patient():
    """
    Map the authenticated identity to exactly one Patient.

    Authorization rule:
        authenticated Google email == Patient.email

    If there is no matching patient, access is denied.
    """

    email = get_authenticated_email()

    if not email:
        return None

    with get_db() as db:
        patient = (
            db.query(Patient)
            .filter(Patient.email.ilike(email))
            .first()
        )

        return patient


def establish_patient_session():
    """
    Establish the application session for the authenticated user.

    Returns:
        Patient object when authorized.
        None when authentication succeeds but no patient
        account is linked.
    """

    if not is_authenticated():
        return None

    patient = get_authenticated_patient()

    if patient is None:
        st.session_state.pop("active_patient_id", None)
        st.session_state["authenticated_patient"] = False
        return None

    st.session_state["authenticated_patient"] = True
    st.session_state["authenticated_email"] = get_authenticated_email()
    st.session_state["active_patient_id"] = patient.id

    return patient


def create_new_patient_account():
    """
    Create a new Patient account for an authenticated Google user.
    Required profile information is collected before database creation.
    """

    email = get_authenticated_email()

    if not email:
        st.error("Unable to determine your authenticated email.")
        st.stop()

    try:
        google_name = st.user.get("name") or ""
    except Exception:
        google_name = ""

    name_parts = google_name.strip().split(maxsplit=1)

    default_first_name = name_parts[0] if name_parts else ""
    default_last_name = name_parts[1] if len(name_parts) > 1 else ""

    st.markdown(
        """
        <div style="
            max-width: 700px;
            margin: 40px auto;
            padding: 30px;
            border-radius: 18px;
            border: 1px solid rgba(128,128,128,0.20);
        ">
            <h1>🏥 Create Your Healthcare Profile</h1>
            <p style="color:#6b7280;">
                Your Google account has been authenticated successfully.
                Complete your profile to continue.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("new_patient_account_form"):

        col1, col2 = st.columns(2)

        with col1:
            first_name = st.text_input(
                "First Name",
                value=default_first_name,
            )

        with col2:
            last_name = st.text_input(
                "Last Name",
                value=default_last_name,
            )

        st.text_input(
            "Email",
            value=email,
            disabled=True,
        )

        from datetime import date

        today = date.today()

        date_of_birth = st.date_input(
            "Date of Birth",
            value=None,
            min_value=date(today.year - 100, today.month, today.day),
            max_value=today,
        )

        gender = st.selectbox(
            "Gender",
            [
                "Male",
                "Female",
                "Other",
                "Prefer not to say",
            ],
        )

        submit = st.form_submit_button(
            "Create Healthcare Account",
            use_container_width=True,
            type="primary",
        )

    if not submit:
        st.stop()

    first_name = first_name.strip()
    last_name = last_name.strip()

    if not first_name:
        st.error("Please enter your first name.")
        st.stop()

    if not last_name:
        st.error("Please enter your last name.")
        st.stop()

    if not date_of_birth:
        st.error("Please select your date of birth.")
        st.stop()

    try:
        with get_db() as db:

            existing_patient = (
                db.query(Patient)
                .filter(Patient.email.ilike(email))
                .first()
            )

            if existing_patient:
                patient = existing_patient

            else:
                patient = Patient(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    date_of_birth=date_of_birth,
                    gender=gender,
                    medical_history=None,
                )

                db.add(patient)
                db.flush()

                patient_id = patient.id

            if existing_patient:
                patient_id = existing_patient.id

            db.commit()

        st.session_state["authenticated_patient"] = True
        st.session_state["authenticated_email"] = email
        st.session_state["active_patient_id"] = patient_id

        st.success("Healthcare account created successfully.")
        st.rerun()

    except Exception as e:
        st.error(f"Unable to create healthcare account: {e}")
        st.stop()


def require_authentication():
    """
    Stop the application until the user authenticates.
    """

    if not is_authenticated():

        st.markdown(
            """
            <div style="
                max-width: 520px;
                margin: 100px auto;
                text-align: center;
                padding: 40px;
                border-radius: 20px;
                border: 1px solid rgba(128,128,128,0.2);
            ">
                <div style="font-size:52px;">🏥</div>

                <h1>AI Clinical Assistant</h1>

                <p style="color:#6b7280;">
                    Secure access to your personal healthcare profile.
                </p>

                <p style="color:#6b7280;">
                    Please authenticate to continue.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.button(
            "Continue with Google",
            on_click=st.login,
            use_container_width=True,
        )

        st.stop()

    patient = establish_patient_session()

    if patient is None:

        create_new_patient_account()

        st.stop()

    return patient


def logout():
    """
    Securely log the current user out.
    """

    st.session_state.pop("active_patient_id", None)
    st.session_state.pop("authenticated_patient", None)
    st.session_state.pop("authenticated_email", None)

    st.logout()
