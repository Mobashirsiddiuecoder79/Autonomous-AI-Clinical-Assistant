import streamlit as st
import pandas as pd


# ==========================================================
# LINE CHART
# ==========================================================

def line_chart(
    title: str,
    x_values: list,
    y_values: list,
    y_label: str = "Value"
):
    """
    Display a reusable line chart.
    """

    st.subheader(title)

    if not x_values or not y_values:
        st.info("No data available.")
        return

    df = pd.DataFrame(
        {
            "X": x_values,
            y_label: y_values
        }
    )

    st.line_chart(
        df.set_index("X"),
        use_container_width=True
    )


# ==========================================================
# BAR CHART
# ==========================================================

def bar_chart(
    title: str,
    labels: list,
    values: list,
    y_label: str = "Value"
):
    """
    Display reusable bar chart.
    """

    st.subheader(title)

    if not labels or not values:
        st.info("No data available.")
        return

    df = pd.DataFrame(
        {
            "Label": labels,
            y_label: values
        }
    )

    st.bar_chart(
        df.set_index("Label"),
        use_container_width=True
    )


# ==========================================================
# HEALTH TREND CHART
# ==========================================================

def health_trend_chart(
    metric_name: str,
    values: list
):
    """
    Display health trend.
    """

    if not values:
        st.info(f"No {metric_name} history available.")
        return

    x = list(range(1, len(values) + 1))

    line_chart(
        title=f"{metric_name} Trend",
        x_values=x,
        y_values=values,
        y_label=metric_name
    )


# ==========================================================
# BMI CHART
# ==========================================================

def bmi_chart(values: list):
    health_trend_chart(
        "BMI",
        values
    )


# ==========================================================
# GLUCOSE CHART
# ==========================================================

def glucose_chart(values: list):
    health_trend_chart(
        "Blood Glucose",
        values
    )


# ==========================================================
# CHOLESTEROL CHART
# ==========================================================

def cholesterol_chart(values: list):
    health_trend_chart(
        "Cholesterol",
        values
    )


# ==========================================================
# BLOOD PRESSURE CHART
# ==========================================================

def blood_pressure_chart(values: list):
    health_trend_chart(
        "Blood Pressure",
        values
    )


# ==========================================================
# PLACEHOLDER
# ==========================================================

def chart_placeholder(title: str):
    """
    Display placeholder when no chart data exists.
    """

    with st.container(border=True):

        st.subheader(title)

        st.info(
            "Patient history is required to generate charts."
        )