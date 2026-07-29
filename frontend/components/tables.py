import streamlit as st
import pandas as pd


# ==========================================================
# GENERIC TABLE
# ==========================================================

def data_table(
    data,
    title: str = "",
    use_container_width: bool = True,
    hide_index: bool = True
):
    """
    Display any dataframe, list of dicts,
    or compatible tabular data.
    """

    if title:
        st.subheader(title)

    if data is None:
        st.info("No data available.")
        return

    if isinstance(data, list):
        if len(data) == 0:
            st.info("No data available.")
            return

        df = pd.DataFrame(data)

    elif isinstance(data, pd.DataFrame):

        if data.empty:
            st.info("No data available.")
            return

        df = data

    else:
        st.info("Unsupported table format.")
        return

    st.dataframe(
        df,
        use_container_width=use_container_width,
        hide_index=hide_index
    )


# ==========================================================
# PATIENT TABLE
# ==========================================================

def patient_table(patients):
    """
    Display patient list.
    """

    rows = []

    for patient in patients:

        rows.append({

            "ID": patient.id,

            "First Name": patient.first_name,

            "Last Name": patient.last_name,

            "Gender": patient.gender,

            "Email": patient.email,

            "Date of Birth": str(patient.date_of_birth)

        })

    data_table(
        rows,
        title="Registered Patients"
    )


# ==========================================================
# REPORT TABLE
# ==========================================================

def report_table(reports):
    """
    Display uploaded reports.
    """

    rows = []

    for report in reports:

        rows.append({

            "Report": getattr(report, "report_type", "-"),

            "Date": str(getattr(report, "created_at", "-")),

            "Status": getattr(report, "status", "-")

        })

    data_table(
        rows,
        title="Medical Reports"
    )


# ==========================================================
# AUDIT TABLE
# ==========================================================

def audit_table(logs):
    """
    Display audit logs.
    """

    rows = []

    for log in logs:

        rows.append({

            "Time": str(log.timestamp),

            "Action": log.user_action,

            "Operator": log.performed_by,

            "Table": log.target_table,

            "Record": log.record_id

        })

    data_table(
        rows,
        title="Audit Logs"
    )


# ==========================================================
# TOOL HISTORY TABLE
# ==========================================================

def tool_history_table(history):
    """
    Display executed tools.
    """

    rows = []

    for tool in history:

        rows.append({

            "Tool": tool.tool_name,

            "Status": tool.execution_status,

            "Started": str(tool.started_at),

            "Finished": str(tool.finished_at)

        })

    data_table(
        rows,
        title="Tool Execution History"
    )