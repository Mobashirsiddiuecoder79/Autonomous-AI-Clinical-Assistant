import os
import json
from datetime import date

import streamlit as st

from database.connection import get_db
from database.models import Session
from database.operations import (
    create_patient,
    get_medical_reports,
    get_patient,
    list_patients,
)

from frontend.components.cards import kpi_card
from frontend.components.header import (
    page_header,
    section_header,
    status_badge,
    glass_card,
)


# ==========================================================
# HELPERS
# ==========================================================

def calculate_age(dob):

    if not dob:
        return "-"

    if isinstance(dob, str):
        dob = date.fromisoformat(dob)

    today = date.today()

    return (
        today.year
        - dob.year
        - ((today.month, today.day) < (dob.month, dob.day))
    )


def get_session_count(patient_id):

    with get_db() as db:

        return (
            db.query(Session)
            .filter(Session.patient_id == patient_id)
            .count()
        )


# ==========================================================
# DATABASE LOADERS
# ==========================================================

def load_patients():

    with get_db() as db:

        return list_patients(db)


def load_patient(patient_id):

    with get_db() as db:

        return get_patient(db, patient_id)


def load_reports(patient_id):

    with get_db() as db:

        return get_medical_reports(db, patient_id)


# ==========================================================
# REGISTER PATIENT
# ==========================================================

def register_patient():

    section_header(
        "➕ Register Patient",
        "Create a new patient profile"
    )

    with st.form("register_patient"):

        col1, col2 = st.columns(2)

        with col1:

            first_name = st.text_input("First Name")

            email = st.text_input("Email")

            gender = st.selectbox(
                "Gender",
                [
                    "Male",
                    "Female",
                    "Other"
                ]
            )

        with col2:

            last_name = st.text_input("Last Name")

            dob = st.date_input("Date of Birth")

        history = st.text_area(
            "Medical History",
            height=140
        )

        submit = st.form_submit_button(
            "Create Patient",
            use_container_width=True
        )

    if not submit:
        return

    if (
        not first_name
        or not last_name
        or not email
    ):

        st.warning(
            "Please fill all required fields."
        )

        return

    with get_db() as db:

        create_patient(
            db=db,
            first_name=first_name,
            last_name=last_name,
            email=email,
            date_of_birth=dob.strftime("%Y-%m-%d"),
            gender=gender,
            medical_history=history,
            operator="practitioner",
        )

    st.success("Patient created successfully.")

    st.rerun()


# ==========================================================
# PATIENT SELECTOR
# ==========================================================

def select_patient(patients):

    if not patients:

        return None

    patient_map = {

        p.id:
        f"{p.first_name} {p.last_name}"

        for p in patients

    }

    if "active_patient_id" not in st.session_state:

        st.session_state.active_patient_id = patients[0].id

    selected = st.selectbox(

        "👤 Active Patient",

        options=list(patient_map.keys()),

        index=list(patient_map.keys()).index(
            st.session_state.active_patient_id
        ),

        format_func=lambda pid:
            f"{patient_map[pid]}  (ID {pid})",

    )

    st.session_state.active_patient_id = selected

    return selected

# ==========================================================
# HEADER
# ==========================================================

def render_header(active_patient):

    patient_name = (
        f"{active_patient.first_name} {active_patient.last_name}"
        if active_patient
        else "No Patient Selected"
    )

    page_header(
        title="AI Clinical Assistant",
        subtitle="Modern Clinical Decision Support Dashboard",
        icon="🏥",
    )

    col1, col2 = st.columns([5, 1])

    with col1:

        st.markdown(
            f"### Welcome back 👋\n"
            f"Managing **{patient_name}**"
        )

    with col2:

        status_badge(
            "AI Online",
            "success",
        )


# ==========================================================
# KPI SECTION
# ==========================================================

def render_kpis(
    patients,
    reports_count,
    session_count,
):

    st.markdown("")

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        kpi_card(
            "Patients",
            len(patients),
            "👤",
        )

    with c2:

        kpi_card(
            "Reports",
            reports_count,
            "📄",
        )

    with c3:

        kpi_card(
            "AI Sessions",
            session_count,
            "💬",
        )

    with c4:

        kpi_card(
            "System",
            "Online",
            "🟢",
        )


# ==========================================================
# PATIENT OVERVIEW
# ==========================================================

def render_patient(patient):

    section_header(
        "👤 Patient Overview",
        "Current patient information"
    )

    with glass_card():

        left, right = st.columns(2)

        with left:

            st.markdown("**Full Name**")
            st.write(
                f"{patient.first_name} {patient.last_name}"
            )

            st.markdown("**Gender**")
            st.write(patient.gender)

            st.markdown("**Age**")
            st.write(
                calculate_age(
                    patient.date_of_birth
                )
            )

        with right:

            st.markdown("**Email**")
            st.write(patient.email)

            st.markdown("**Date of Birth**")
            st.write(patient.date_of_birth)

            st.markdown("**Created**")
            st.write(
                patient.created_at.strftime(
                    "%d %b %Y"
                )
            )

        st.markdown("---")

        st.markdown("### Medical History")

        if patient.medical_history:

            st.write(patient.medical_history)

        else:

            st.info(
                "No medical history available."
            )


# ==========================================================
# HEALTH SUMMARY
# ==========================================================

def render_health_summary(patient):

    section_header(
        "❤️ Health Summary",
        "Quick clinical overview"
    )

    with glass_card():

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Age",
                calculate_age(
                    patient.date_of_birth
                )
            )

            st.metric(
                "Gender",
                patient.gender
            )

        with col2:

            st.metric(
                "Reports",
                len(load_reports(patient.id))
            )

            st.metric(
                "AI Sessions",
                get_session_count(
                    patient.id
                )
            )

        st.progress(100)

        st.success(
            "Patient record loaded successfully."
        )


# ==========================================================
# REPORTS
# ==========================================================

def render_reports(patient_id):

    section_header(
        "📄 Medical Reports",
        "Uploaded diagnostic reports"
    )

    reports = load_reports(patient_id)

    if not reports:

        st.info(
            "No reports available."
        )

        return

    for report in reports:

        with glass_card():

            col1, col2 = st.columns(
                [4, 1]
            )

            with col1:

                st.markdown(
                    f"### {report.file_name}"
                )

                st.caption(
                    report.file_type
                )

            with col2:

                st.caption(
                    report.uploaded_at.strftime(
                        "%d %b %Y"
                    )
                )


# ==========================================================
# APPOINTMENTS
# ==========================================================

def render_appointments(patient_id):

    section_header(
        "📅 Upcoming Appointments",
        "Scheduled consultations"
    )

    appointments = []

    json_path = "logs/appointments.json"

    if os.path.exists(json_path):

        try:

            with open(
                json_path,
                "r",
                encoding="utf-8"
            ) as f:

                appointments = json.load(f)

        except Exception:

            appointments = []

    patient_items = [

        a for a in appointments

        if a.get("patient_id") == patient_id

    ]

    with glass_card():

        if not patient_items:

            st.info(
                "No upcoming appointments."
            )

            return

        for item in patient_items:

            st.markdown(
                f"""
**🩺 {item.get('doctor','Doctor')}**

📅 {item.get('date','-')}

🕒 {item.get('time','-')}

---
"""
            )


# ==========================================================
# REMINDERS
# ==========================================================

def render_reminders(patient_id):

    section_header(
        "💊 Medication & Reminders",
        "Patient reminders"
    )

    reminders = []

    json_path = "logs/reminders.json"

    if os.path.exists(json_path):

        try:

            with open(
                json_path,
                "r",
                encoding="utf-8"
            ) as f:

                reminders = json.load(f)

        except Exception:

            reminders = []

    patient_items = [

        r for r in reminders

        if r.get("patient_id") == patient_id

    ]

    with glass_card():

        if not patient_items:

            st.info(
                "No reminders."
            )

            return

        for reminder in patient_items:

            st.checkbox(
                reminder.get(
                    "title",
                    "Reminder"
                ),
                value=reminder.get(
                    "completed",
                    False
                ),
                disabled=True,
            )


# ==========================================================
# QUICK ACTIONS
# ==========================================================

def render_quick_actions():

    section_header(
        "⚡ Quick Actions",
        "Frequently used actions"
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "➕ Register Patient",
            use_container_width=True,
        ):
            register_patient()

    with col2:

        if st.button(
            "🤖 Open AI Assistant",
            use_container_width=True,
        ):
            st.session_state.navigation = "🤖 AI Assistant"
            st.rerun()


# ==========================================================
# RECENT ACTIVITY
# ==========================================================

def render_recent_activity(patient):

    section_header(
        "🕒 Recent Activity",
        "Latest patient events"
    )

    with glass_card():

        st.markdown(
            f"""
• Patient profile viewed

• {len(load_reports(patient.id))} medical report(s) available

• {get_session_count(patient.id)} AI consultation session(s)

• Last updated: {patient.created_at.strftime("%d %b %Y")}
"""
        )


# ==========================================================
# MAIN DASHBOARD
# ==========================================================

def show_dashboard():

    patients = load_patients()

    if not patients:

        page_header(
            "AI Clinical Assistant",
            "No patients found in the database.",
            "🏥"
        )

        register_patient()

        return

    selected_id = select_patient(patients)

    active_patient = load_patient(selected_id)

    if not active_patient:

        st.warning(
            "Unable to load patient."
        )

        return

    reports = load_reports(selected_id)

    sessions = get_session_count(selected_id)

    render_header(active_patient)

    render_kpis(
        patients,
        len(reports),
        sessions,
    )

    st.markdown("")

    left, right = st.columns(
        [2, 1]
    )

    with left:

        render_patient(active_patient)

        render_reports(selected_id)

    with right:

        render_health_summary(
            active_patient
        )

        render_appointments(
            selected_id
        )

        render_reminders(
            selected_id
        )

    st.markdown("")

    col1, col2 = st.columns(
        [1, 1]
    )

    with col1:

        render_quick_actions()

    with col2:

        render_recent_activity(
            active_patient
        )
