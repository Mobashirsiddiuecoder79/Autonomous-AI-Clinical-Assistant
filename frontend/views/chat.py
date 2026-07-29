import uuid
import textwrap

import streamlit as st

from database.connection import get_db
from database.operations import (
    create_session,
    get_chat_history,
    get_patient
)

from agent.graph import run_agent_flow


# ==========================================================
# HTML HELPER
# ==========================================================

def html(content: str):
    """
    Render HTML safely without Markdown turning it
    into a code block.
    """
    st.markdown(
        textwrap.dedent(content),
        unsafe_allow_html=True
    )


# ==========================================================
# PAGE HEADER
# ==========================================================

def render_header():

    html("""
<div class="glass-card">

<div style="display:flex;
justify-content:space-between;
align-items:center;">

<div>

<h1 class="gradient-title"
style="margin-bottom:4px;">

🤖 Autonomous Clinical Assistant

</h1>

<div style="color:#94a3b8;
font-size:15px;">

AI-powered Healthcare Decision Support System

</div>

</div>

<div style="text-align:right;">

<div style="
font-size:14px;
font-weight:700;
color:#22c55e;">

🟢 AI Online

</div>

<div style="
font-size:13px;
color:#94a3b8;">

Model : GPT-4o-mini

</div>

</div>

</div>

</div>
""")


# ==========================================================
# PATIENT CARD
# ==========================================================

def render_patient_card(patient):

    html(f"""
<div class="glass-card">

<h3>👤 Active Patient</h3>

<hr>

<table style="width:100%;">

<tr>
<td><b>Name</b></td>
<td>{patient.first_name} {patient.last_name}</td>
</tr>

<tr>
<td><b>ID</b></td>
<td>{patient.id}</td>
</tr>

<tr>
<td><b>Gender</b></td>
<td>{patient.gender}</td>
</tr>

<tr>
<td><b>Date of Birth</b></td>
<td>{patient.date_of_birth}</td>
</tr>

<tr>
<td><b>Email</b></td>
<td>{patient.email}</td>
</tr>

</table>

</div>
""")


# ==========================================================
# AI STATUS
# ==========================================================

def render_ai_status():

    html("""
<div class="glass-card">

<h3>🧠 AI Status</h3>

<hr>

<div class="badge-success">
Database Connected
</div>

<br><br>

<div class="badge-success">
Vector Memory Ready
</div>

<br><br>

<div class="badge-success">
LangGraph Running
</div>

<br><br>

<div class="badge-success">
Clinical Agent Ready
</div>

</div>
""")

# ==========================================================
# SUGGESTED PROMPTS
# ==========================================================

def render_suggestions():

    st.markdown("### 💡 Quick Actions")

    suggestions = [
        ("🩺 Calculate BMI", "Calculate BMI for 70 kg and 170 cm."),
        ("❤️ Assess Chest Pain", "Patient has chest pain."),
        ("💊 Drug Interaction", "Check interaction between Aspirin and Warfarin."),
        ("📅 Book Appointment", "Schedule a cardiology appointment."),
        ("🧪 Analyze Lab Report", "Analyze cholesterol 245 LDL 170 HDL 38."),
        ("🌐 Search Guidelines", "Search hypertension treatment guidelines.")
    ]

    cols = st.columns(2)

    selected_prompt = None

    for i, (title, prompt) in enumerate(suggestions):

        with cols[i % 2]:

            if st.button(
                title,
                use_container_width=True,
                key=f"suggestion_{i}"
            ):
                selected_prompt = prompt

    return selected_prompt


# ==========================================================
# MAIN PAGE
# ==========================================================

def show_chat():

    render_header()

    # ------------------------------------------------------
    # ACTIVE PATIENT CHECK
    # ------------------------------------------------------

    if (
        "active_patient_id" not in st.session_state
        or st.session_state.active_patient_id <= 0
    ):

        st.warning(
            "Please select a patient from the Dashboard first."
        )

        return

    patient_id = st.session_state.active_patient_id

    # ------------------------------------------------------
    # LOAD PATIENT
    # ------------------------------------------------------

    with get_db() as db:

        patient = get_patient(
            db,
            patient_id
        )

    if patient is None:

        st.error("Patient not found.")

        return

    # ------------------------------------------------------
    # CREATE SESSION
    # ------------------------------------------------------

    if "chat_session_id" not in st.session_state:

        session_id = f"sess_{uuid.uuid4().hex[:10]}"

        st.session_state.chat_session_id = session_id

        with get_db() as db:

            create_session(
                db,
                session_id,
                patient_id
            )

    session_id = st.session_state.chat_session_id

    # ------------------------------------------------------
    # PAGE LAYOUT
    # ------------------------------------------------------

    sidebar, main = st.columns(
        [1, 2.6],
        gap="large"
    )

    # ======================================================
    # LEFT PANEL
    # ======================================================

    with sidebar:

        render_patient_card(patient)

        render_ai_status()

        suggested_prompt = render_suggestions()

    # ======================================================
    # RIGHT PANEL
    # ======================================================

    with main:

        st.markdown("## 💬 Clinical Conversation")

        with get_db() as db:

            history = get_chat_history(
                db,
                session_id
            )

        # --------------------------------------------------
        # EMPTY CHAT
        # --------------------------------------------------

        if not history:

            html("""
<div class="glass-card"
style="text-align:center;padding:45px;">

<h2>👋 Welcome</h2>

<p>

Ask the AI Healthcare Assistant anything.

</p>

<br>

<div class="badge-success">
🩺 BMI Calculator
</div>

<br><br>

<div class="badge-success">
💊 Drug Interaction Checker
</div>

<br><br>

<div class="badge-success">
📄 Medical Report Analysis
</div>

<br><br>

<div class="badge-success">
📅 Appointment Scheduling
</div>

</div>
""")

        # ==================================================
        # CHAT HISTORY
        # ==================================================

        for message in history:

            with st.chat_message(message.role):

                st.markdown(message.message)

        # ==================================================
        # CHAT INPUT
        # ==================================================

        chat_prompt = st.chat_input(
            "Ask your healthcare question..."
        )

        # Use suggested prompt if selected
        if suggested_prompt:

            chat_prompt = suggested_prompt

        if not chat_prompt:

            return

        # ==================================================
        # USER MESSAGE
        # ==================================================

        with st.chat_message("user"):

            st.markdown(chat_prompt)

        # ==================================================
        # AI EXECUTION
        # ==================================================

        with st.spinner("AI is analyzing..."):

            progress = st.progress(0)

            status = st.empty()

            status.info("🧠 Understanding your request...")
            progress.progress(15)

            status.info("📋 Building execution plan...")
            progress.progress(35)

            status.info("🛠 Selecting clinical tools...")
            progress.progress(55)

            status.info("⚙ Executing workflow...")
            progress.progress(80)

            result = run_agent_flow(

                session_id=session_id,

                patient_id=patient_id,

                prompt=chat_prompt

            )

            status.success("✅ Preparing final response...")
            progress.progress(100)

        progress.empty()
        status.empty()

        # ==================================================
        # ASSISTANT RESPONSE
        # ==================================================

        final_output = result.get(
            "final_output",
            "Unable to generate a response."
        )

        with st.chat_message("assistant"):

            html(f"""
<div class="glass-card">

<h3>🤖 Clinical Assistant</h3>

<hr>

{final_output}

</div>
""")

        # ==================================================
        # EXECUTION DATA
        # ==================================================

        tool_outputs = result.get(
            "tool_outputs",
            []
        )

        completed_tasks = result.get(
            "completed_tasks",
            []
        )

        plan = result.get(
            "plan",
            []
        )

        # ==================================================
        # TOOL RESULT DASHBOARD
        # ==================================================

        if tool_outputs:

            st.divider()

            st.markdown("## 🛠 AI Tool Results")

            for tool in tool_outputs:

                tool_name = tool.get("tool", "Unknown")
                success = tool.get("success", False)
                data = tool.get("data", {})
                error = tool.get("error")

                # ------------------------------------------
                # TOOL FAILED
                # ------------------------------------------

                if not success:

                    st.error(error)
                    continue

                # ------------------------------------------
                # BMI
                # ------------------------------------------

                if tool_name == "bmi_calculator":

                    c1, c2 = st.columns([1, 2])

                    with c1:

                        st.metric(
                            "BMI",
                            data.get("bmi")
                        )

                    with c2:

                        html(f"""
<div class="glass-card">

<h3>🩺 Body Mass Index</h3>

<b>Classification</b>

<p>{data.get("classification")}</p>

<hr>

{data.get("details")}

</div>
""")

                # ------------------------------------------
                # DRUG INTERACTION
                # ------------------------------------------

                elif tool_name == "drug_interaction_checker":

                    html("""
<div class="glass-card">
<h3>💊 Drug Interaction Report</h3>
</div>
""")

                    if data.get("interactions_count", 0) == 0:

                        st.success(
                            "No clinically significant interaction detected."
                        )

                    else:

                        for item in data.get("details", []):

                            severity = item.get("severity", "")

                            if "Fatal" in severity or "Contraindicated" in severity:

                                st.error(
                                    f"**{' + '.join(item['drugs'])}**\n\n"
                                    f"{severity}\n\n"
                                    f"{item['description']}"
                                )

                            elif "Major" in severity:

                                st.warning(
                                    f"**{' + '.join(item['drugs'])}**\n\n"
                                    f"{severity}\n\n"
                                    f"{item['description']}"
                                )

                            else:

                                st.info(
                                    f"**{' + '.join(item['drugs'])}**\n\n"
                                    f"{severity}\n\n"
                                    f"{item['description']}"
                                )

                # ------------------------------------------
                # SYMPTOMS
                # ------------------------------------------

                elif tool_name == "symptom_assessment":

                    html(f"""
<div class="glass-card">

<h3>❤️ Symptom Assessment</h3>

<b>Urgency Level</b>

<h2>{data.get("urgency_level")}</h2>

</div>
""")

                    st.markdown("### Findings")

                    for finding in data.get("findings", []):

                        st.info(
                            finding["assessment"]
                        )

                    st.markdown("### Recommended Specialists")

                    cols = st.columns(2)

                    for i, specialist in enumerate(
                        data.get(
                            "recommended_specialists",
                            []
                        )
                    ):

                        with cols[i % 2]:

                            st.success(
                                specialist
                            )

                # ------------------------------------------
                # APPOINTMENT
                # ------------------------------------------

                elif tool_name == "appointment_scheduler":

                    st.success(
                        data.get(
                            "message",
                            "Appointment booked."
                        )
                    )

                # ------------------------------------------
                # LAB REPORT
                # ------------------------------------------

                elif tool_name == "lab_report_analyzer":

                    html(f"""
<div class="glass-card">

<h3>🧪 Laboratory Analysis</h3>

<b>Summary</b>

<p>{data.get("summary")}</p>

<hr>

<b>Recommendations</b>

<p>{data.get("recommendations")}</p>

</div>
""")

                    biomarkers = data.get(
                        "biomarkers_found",
                        []
                    )

                    if biomarkers:

                        st.dataframe(

                            biomarkers,

                            use_container_width=True,

                            hide_index=True

                        )

                # ------------------------------------------
                # REPORT PARSER
                # ------------------------------------------

                elif tool_name == "medical_report_parser":

                    html(f"""
<div class="glass-card">

<h3>📄 Medical Report Parser</h3>

<b>File</b>

<p>{data.get("file_name")}</p>

<b>Characters Extracted</b>

<p>{data.get("total_character_count")}</p>

</div>
""")

                    st.text_area(

                        "Extracted Report",

                        value=data.get(
                            "raw_text",
                            ""
                        ),

                        height=220,

                        disabled=True,

                        key="parsed_report"

                    )

                # ------------------------------------------
                # WEB SEARCH
                # ------------------------------------------

                elif tool_name == "web_search":

                    html("""
<div class="glass-card">

<h3>🌐 Medical Knowledge Search</h3>

</div>
""")

                    st.markdown(
                        data.get(
                            "results",
                            ""
                        )
                    )

          