import streamlit as st

from database.connection import get_db
from database.models import Patient


def is_admin():
    try:
        if not st.user.is_logged_in:
            return False

        authenticated_email = st.user.get("email")

        if not authenticated_email:
            return False

        admin_email = st.secrets.get("admin", {}).get("email", "")

        return (
            str(authenticated_email).strip().lower()
            == str(admin_email).strip().lower()
        )

    except Exception:
        return False


def show_admin_patients():

    if not is_admin():
        st.error("⛔ Access denied.")
        st.info("This page is available only to the administrator.")
        return

    st.html(
        """
        <div style="
            padding:24px 28px;
            margin-bottom:24px;
            border-radius:18px;
            background:rgba(15,23,42,0.65);
            border:1px solid rgba(148,163,184,0.15);
        ">
            <div style="
                font-size:28px;
                font-weight:700;
                color:#e5edf8;
            ">
                👥 Registered Patients
            </div>

            <div style="
                margin-top:6px;
                font-size:14px;
                color:#94a3b8;
            ">
                Private administrator view of registered healthcare accounts
            </div>
        </div>
        """
    )

    with get_db() as db:
        patients = (
            db.query(Patient)
            .order_by(Patient.id.asc())
            .all()
        )

    st.metric(
        "Total Registered Patients",
        len(patients),
    )

    st.markdown("### Patient Accounts")

    if not patients:
        st.info("No patient accounts have been registered yet.")
        return

    patient_data = []

    for patient in patients:
        patient_data.append(
            {
                "Patient ID": patient.id,
                "Name": f"{patient.first_name} {patient.last_name}",
                "Email": patient.email,
                "Gender": patient.gender,
                "Date of Birth": (
                    patient.date_of_birth.strftime("%Y-%m-%d")
                    if patient.date_of_birth
                    else "—"
                ),
                "Created": (
                    patient.created_at.strftime("%Y-%m-%d %H:%M")
                    if patient.created_at
                    else "—"
                ),
            }
        )

    st.dataframe(
        patient_data,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("### Patient Details")

    patient_options = {
        f"#{patient.id} — {patient.first_name} {patient.last_name}": patient
        for patient in patients
    }

    selected_name = st.selectbox(
        "Select a patient",
        list(patient_options.keys()),
    )

    selected_patient = patient_options[selected_name]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            f"""
**Patient ID:** #{selected_patient.id}

**First Name:** {selected_patient.first_name}

**Last Name:** {selected_patient.last_name}

**Email:** {selected_patient.email}
"""
        )

    with col2:
        st.markdown(
            f"""
**Gender:** {selected_patient.gender}

**Date of Birth:** {
    selected_patient.date_of_birth.strftime("%Y-%m-%d")
    if selected_patient.date_of_birth
    else "—"
}

**Account Created:** {
    selected_patient.created_at.strftime("%Y-%m-%d %H:%M")
    if selected_patient.created_at
    else "—"
}
"""
        )
