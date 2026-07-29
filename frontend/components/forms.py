import streamlit as st


# ==========================================================
# TEXT INPUT
# ==========================================================

def text_input(
    label: str,
    value: str = "",
    placeholder: str = ""
):
    return st.text_input(
        label,
        value=value,
        placeholder=placeholder
    )


# ==========================================================
# EMAIL INPUT
# ==========================================================

def email_input(
    label: str,
    value: str = ""
):
    return st.text_input(
        label,
        value=value,
        placeholder="example@email.com"
    )


# ==========================================================
# DATE INPUT
# ==========================================================

def date_input(
    label: str
):
    return st.date_input(label)


# ==========================================================
# GENDER SELECT
# ==========================================================

def gender_select():
    return st.selectbox(
        "Gender",
        [
            "Male",
            "Female",
            "Other"
        ]
    )


# ==========================================================
# TEXT AREA
# ==========================================================

def medical_history_input():
    return st.text_area(
        "Medical History",
        height=120
    )


# ==========================================================
# PRIMARY BUTTON
# ==========================================================

def primary_button(text: str):
    return st.form_submit_button(
        text,
        use_container_width=True
    )