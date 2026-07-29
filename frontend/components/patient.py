import streamlit as st
from datetime import date


# ==========================================================
# CALCULATE AGE
# ==========================================================

def calculate_age(dob):
    """
    Calculate patient age from date of birth.
    """

    if dob is None:
        return "-"

    today = date.today()

    return (
        today.year
        - dob.year
        - (
            (today.month, today.day)
            <
            (dob.month, dob.day)
        )
    )


# ==========================================================
# PATIENT PROFILE
# ==========================================================

def patient_profile(patient):
    """
    Professional patient summary card.
    """

    age = calculate_age(patient.date_of_birth)

    with st.container(border=True):

        st.subheader("👤 Patient Profile")

        c1, c2 = st.columns([1, 3])

        with c1:

            st.markdown("# 👨‍⚕️")

        with c2:

            st.markdown(
                f"### {patient.first_name} {patient.last_name}"
            )

            st.caption(f"Patient ID : {patient.id}")

        st.divider()

        c1, c2 = st.columns(2)

        with c1:

            st.write("**Gender**")
            st.write(patient.gender)

            st.write("**Age**")
            st.write(age)

            st.write("**DOB**")
            st.write(patient.date_of_birth)

        with c2:

            st.write("**Email**")
            st.write(patient.email)

            st.write("**Status**")

            st.success("Active")

        if patient.medical_history:

            st.divider()

            st.markdown("#### 🩺 Medical History")

            st.info(patient.medical_history)


# ==========================================================
# SMALL PATIENT CARD
# ==========================================================

def patient_mini_card(patient):
    """
    Compact patient card.
    """

    with st.container(border=True):

        st.markdown(
            f"""
### 👤 {patient.first_name} {patient.last_name}

**ID:** {patient.id}

**Gender:** {patient.gender}
"""
        )


# ==========================================================
# ACTIVE PATIENT BADGE
# ==========================================================

def active_patient_badge(patient):

    st.success(
        f"Active Patient : {patient.first_name} {patient.last_name}"
    )