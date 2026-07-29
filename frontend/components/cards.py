import streamlit as st
from contextlib import contextmanager


# ==========================================================
# PAGE SECTION
# ==========================================================

def section_header(
    title: str,
    subtitle: str = ""
):
    st.markdown(f"## {title}")

    if subtitle:
        st.caption(subtitle)

    st.divider()


# ==========================================================
# GLASS CARD
# ==========================================================

@contextmanager
def glass_card(title: str = ""):

    with st.container(border=True):

        if title:
            st.markdown(f"### {title}")

        yield


# ==========================================================
# KPI CARD
# ==========================================================

def kpi_card(
    title: str,
    value,
    icon: str = "📊",
    subtitle: str = "",
    delta: str = ""
):

    with st.container(border=True):

        col1, col2 = st.columns([1, 4])

        with col1:
            st.markdown(f"# {icon}")

        with col2:

            st.caption(title)

            st.markdown(
                f"## {value}"
            )

            if subtitle:
                st.caption(subtitle)

            if delta:
                st.success(delta)


# ==========================================================
# INFO CARD
# ==========================================================

def info_card(
    title: str,
    value: str,
    icon: str = "ℹ️"
):

    with st.container(border=True):

        st.markdown(f"### {icon} {title}")

        st.write(value)


# ==========================================================
# STATUS CARD
# ==========================================================

def status_card(
    title: str,
    status: str,
    status_type: str = "success"
):

    with st.container(border=True):

        st.markdown(f"### {title}")

        if status_type == "success":
            st.success(status)

        elif status_type == "warning":
            st.warning(status)

        elif status_type == "error":
            st.error(status)

        else:
            st.info(status)


# ==========================================================
# APPOINTMENT CARD
# ==========================================================

def appointment_card(
    specialty: str,
    date: str,
    time: str
):

    with st.container(border=True):

        st.markdown("### 📅 Appointment")

        st.write(f"**Department**")

        st.write(specialty)

        st.write(f"**Date**")

        st.write(date)

        st.write(f"**Time**")

        st.write(time)


# ==========================================================
# REPORT CARD
# ==========================================================

def report_card(
    report_name: str,
    report_date: str,
    status: str
):

    with st.container(border=True):

        st.markdown(f"### 🧪 {report_name}")

        st.caption(report_date)

        if status.lower() == "normal":

            st.success(status)

        elif status.lower() == "abnormal":

            st.error(status)

        else:

            st.info(status)


# ==========================================================
# EMPTY STATE
# ==========================================================

def empty_state(
    title: str,
    description: str,
    icon: str = "📄"
):

    with st.container(border=True):

        st.markdown(f"# {icon}")

        st.subheader(title)

        st.caption(description)


# ==========================================================
# MESSAGE HELPERS
# ==========================================================

def success_message(text):

    st.success(text)


def warning_message(text):

    st.warning(text)


def error_message(text):

    st.error(text)


def info_message(text):

    st.info(text)


# ==========================================================
# METRIC ROW
# ==========================================================

def metric_row(metrics: list):
    """
    metrics = [
        ("Patients",12),
        ("Reports",5),
        ("Appointments",2)
    ]
    """

    cols = st.columns(len(metrics))

    for col, metric in zip(cols, metrics):

        title, value = metric

        with col:

            st.metric(
                title,
                value
            )


# ==========================================================
# QUICK ACTION BUTTONS
# ==========================================================

def quick_actions(actions):

    cols = st.columns(len(actions))

    clicked = None

    for col, action in zip(cols, actions):

        with col:

            if st.button(
                action,
                use_container_width=True
            ):
                clicked = action

    return clicked


# ==========================================================
# DIVIDER
# ==========================================================

def page_divider():

    st.divider()