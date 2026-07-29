import os
import streamlit as st

from database.connection import (
    get_db,
    init_db
)

from database.operations import (
    list_patients,
    create_patient
)

from database.models import (
    Session,
    MedicalReport,
    ToolHistory,
    AuditLog
)

from config.settings import settings


# ==========================================================
# SETTINGS PAGE
# ==========================================================

def show_settings():

    st.markdown(
        '<h1 class="gradient-title">⚙️ AI Healthcare Administration Center</h1>',
        unsafe_allow_html=True
    )

    st.caption(
        "Monitor system health, patient database, audit logs and AI agent runtime."
    )

    st.divider()

    # =====================================================
    # DATABASE STATUS
    # =====================================================

    try:

        with get_db() as db:

            patient_count = len(
                list_patients(db)
            )

            report_count = db.query(
                MedicalReport
            ).count()

            session_count = db.query(
                Session
            ).count()

            tool_count = db.query(
                ToolHistory
            ).count()

        db_status = "Healthy"

    except Exception:

        patient_count = 0
        report_count = 0
        session_count = 0
        tool_count = 0

        db_status = "Disconnected"

    # =====================================================
    # SYSTEM HEALTH
    # =====================================================

    st.subheader("🏥 System Health")

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.markdown(f"""
<div class="glass-card" style="text-align:center;">
<h3>Database</h3>
<h1>{"🟢" if db_status=="Healthy" else "🔴"}</h1>
<p>{db_status}</p>
</div>
""", unsafe_allow_html=True)

    with c2:

        st.markdown("""
<div class="glass-card" style="text-align:center;">
<h3>AI Agent</h3>
<h1>🟢</h1>
<p>Operational</p>
</div>
""", unsafe_allow_html=True)

    with c3:

        st.markdown("""
<div class="glass-card" style="text-align:center;">
<h3>Vector Store</h3>
<h1>🟢</h1>
<p>FAISS Ready</p>
</div>
""", unsafe_allow_html=True)

    with c4:

        logs_exist = os.path.exists(
            settings.SYSTEM_LOG_FILE
        )

        st.markdown(f"""
<div class="glass-card" style="text-align:center;">
<h3>Runtime Logs</h3>
<h1>{"🟢" if logs_exist else "🟡"}</h1>
<p>{"Available" if logs_exist else "Waiting"}</p>
</div>
""", unsafe_allow_html=True)

    st.divider()

    # =====================================================
    # DATABASE METRICS
    # =====================================================

    st.subheader("📊 Database Statistics")

    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.metric(
            "Patients",
            patient_count
        )

    with m2:
        st.metric(
            "Reports",
            report_count
        )

    with m3:
        st.metric(
            "Sessions",
            session_count
        )

    with m4:
        st.metric(
            "Tool Runs",
            tool_count
        )

    st.divider()

    # =====================================================
    # DATABASE MANAGEMENT
    # =====================================================

    st.subheader("🗄 Database Management")

    b1, b2, b3 = st.columns(3)

    with b1:

        if st.button(
            "Initialize Database",
            use_container_width=True
        ):

            init_db()

            st.success(
                "Database initialized successfully."
            )

    with b2:

        if st.button(
            "Refresh Dashboard",
            use_container_width=True
        ):

            st.rerun()

    with b3:

        if st.button(
            "Seed Sample Database",
            use_container_width=True
        ):

            with get_db() as db:

                existing = list_patients(db)

                if existing:

                    st.info(
                        "Database already contains patient records."
                    )

                else:

                    create_patient(
                        db=db,
                        first_name="John",
                        last_name="Doe",
                        email="john.doe@hospital.org",
                        date_of_birth="1980-05-15",
                        gender="Male",
                        ssn="123-45-6789",
                        medical_history=(
                            "Hypertension diagnosed in 2021. "
                            "Currently taking Simvastatin 20mg daily."
                        ),
                        operator="admin"
                    )

                    create_patient(
                        db=db,
                        first_name="Jane",
                        last_name="Smith",
                        email="jane.smith@hospital.org",
                        date_of_birth="1992-09-22",
                        gender="Female",
                        ssn="987-65-4321",
                        medical_history=(
                            "Type 2 Diabetes Mellitus. "
                            "Metformin therapy."
                        ),
                        operator="admin"
                    )

                    st.success(
                        "Sample patients added successfully."
                    )

                    st.rerun()

    st.divider()

    # =====================================================
    # TOOL EXECUTION ANALYTICS
    # =====================================================

    st.subheader("🛠 Tool Execution Analytics")

    with get_db() as db:

        try:

            tool_history = (
                db.query(ToolHistory)
                .order_by(
                    ToolHistory.timestamp.desc()
                )
                .all()
            )

        except Exception:

            tool_history = []

    if tool_history:

        success_count = 0
        failure_count = 0

        tool_summary = {}

        total_runtime = 0.0

        for row in tool_history:

            tool_summary[row.tool_name] = (
                tool_summary.get(
                    row.tool_name,
                    0
                ) + 1
            )

            total_runtime += row.duration_ms

            if row.execution_status.lower() == "success":

                success_count += 1

            else:

                failure_count += 1

        avg_runtime = (
            total_runtime / len(tool_history)
            if tool_history
            else 0
        )

        t1, t2, t3, t4 = st.columns(4)

        with t1:

            st.metric(
                "Executions",
                len(tool_history)
            )

        with t2:

            st.metric(
                "Successful",
                success_count
            )

        with t3:

            st.metric(
                "Failed",
                failure_count
            )

        with t4:

            st.metric(
                "Avg Runtime",
                f"{avg_runtime:.1f} ms"
            )

        st.markdown("### Tool Usage Summary")

        tool_table = []

        for tool_name, count in sorted(

            tool_summary.items(),

            key=lambda x: x[1],

            reverse=True

        ):

            tool_table.append({

                "Tool Name": tool_name,

                "Executions": count

            })

        st.dataframe(

            tool_table,

            use_container_width=True,

            hide_index=True

        )

        with st.expander(
            "Recent Tool Executions",
            expanded=False
        ):

            latest = []

            for row in tool_history[:20]:

                latest.append({

                    "Time":
                    row.timestamp.strftime(
                        "%Y-%m-%d %H:%M"
                    ),

                    "Tool":
                    row.tool_name,

                    "Status":
                    row.execution_status,

                    "Runtime (ms)":
                    round(
                        row.duration_ms,
                        2
                    )

                })

            st.dataframe(

                latest,

                use_container_width=True,

                hide_index=True

            )

    else:

        st.info(
            "No tool execution history available yet."
        )

    st.divider()

    with b3:

        if st.button(
            "Seed Sample Database",
            use_container_width=True
        ):

            with get_db() as db:

                existing = list_patients(db)

                if existing:

                    st.info(
                        "Database already contains patient records."
                    )

                else:

                    create_patient(
                        db=db,
                        first_name="John",
                        last_name="Doe",
                        email="john.doe@hospital.org",
                        date_of_birth="1980-05-15",
                        gender="Male",
                        ssn="123-45-6789",
                        medical_history=(
                            "Hypertension diagnosed in 2021. "
                            "Currently taking Simvastatin 20mg daily."
                        ),
                        operator="admin"
                    )

                    create_patient(
                        db=db,
                        first_name="Jane",
                        last_name="Smith",
                        email="jane.smith@hospital.org",
                        date_of_birth="1992-09-22",
                        gender="Female",
                        ssn="987-65-4321",
                        medical_history=(
                            "Type 2 Diabetes Mellitus. "
                            "Metformin therapy."
                        ),
                        operator="admin"
                    )

                    st.success(
                        "Sample patients added successfully."
                    )

                    st.rerun()

    st.divider()

    # =====================================================
    # TOOL EXECUTION ANALYTICS
    # =====================================================

    st.subheader("🛠 Tool Execution Analytics")

    with get_db() as db:

        try:

            tool_history = (
                db.query(ToolHistory)
                .order_by(
                    ToolHistory.timestamp.desc()
                )
                .all()
            )

        except Exception:

            tool_history = []

    if tool_history:

        success_count = 0
        failure_count = 0

        tool_summary = {}

        total_runtime = 0.0

        for row in tool_history:

            tool_summary[row.tool_name] = (
                tool_summary.get(
                    row.tool_name,
                    0
                ) + 1
            )

            total_runtime += row.duration_ms

            if row.execution_status.lower() == "success":

                success_count += 1

            else:

                failure_count += 1

        avg_runtime = (
            total_runtime / len(tool_history)
            if tool_history
            else 0
        )

        t1, t2, t3, t4 = st.columns(4)

        with t1:

            st.metric(
                "Executions",
                len(tool_history)
            )

        with t2:

            st.metric(
                "Successful",
                success_count
            )

        with t3:

            st.metric(
                "Failed",
                failure_count
            )

        with t4:

            st.metric(
                "Avg Runtime",
                f"{avg_runtime:.1f} ms"
            )

        st.markdown("### Tool Usage Summary")

        tool_table = []

        for tool_name, count in sorted(

            tool_summary.items(),

            key=lambda x: x[1],

            reverse=True

        ):

            tool_table.append({

                "Tool Name": tool_name,

                "Executions": count

            })

        st.dataframe(

            tool_table,

            use_container_width=True,

            hide_index=True

        )

        with st.expander(
            "Recent Tool Executions",
            expanded=False
        ):

            latest = []

            for row in tool_history[:20]:

                latest.append({

                    "Time":
                    row.timestamp.strftime(
                        "%Y-%m-%d %H:%M"
                    ),

                    "Tool":
                    row.tool_name,

                    "Status":
                    row.execution_status,

                    "Runtime (ms)":
                    round(
                        row.duration_ms,
                        2
                    )

                })

            st.dataframe(

                latest,

                use_container_width=True,

                hide_index=True

            )

    else:

        st.info(
            "No tool execution history available yet."
        )

    st.divider()

        # =====================================================
    # RUNTIME LOG VIEWER
    # =====================================================

    st.subheader("📜 Runtime System Logs")

    if os.path.exists(settings.SYSTEM_LOG_FILE):

        with open(
            settings.SYSTEM_LOG_FILE,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as f:

            all_logs = f.readlines()

        log_search = st.text_input(
            "Search Runtime Logs",
            placeholder="Search ERROR, INFO, WARNING..."
        )

        if log_search:

            filtered_logs = [

                line

                for line in all_logs

                if log_search.lower() in line.lower()

            ]

        else:

            filtered_logs = all_logs

        max_lines = st.slider(

            "Number of Lines",

            min_value=20,

            max_value=500,

            value=100,

            step=20

        )

        log_text = "".join(
            filtered_logs[-max_lines:]
        )

        st.text_area(

            "Runtime Output",

            value=log_text,

            height=350,

            disabled=True,

            key="runtime_logs"

        )

        st.download_button(

            "⬇ Download Log File",

            data="".join(all_logs),

            file_name="system_logs.txt",

            mime="text/plain",

            use_container_width=True

        )

    else:

        st.info(
            "System log file has not been generated yet."
        )

    st.divider()

    # =====================================================
    # SYSTEM INFORMATION
    # =====================================================

    st.subheader("💻 System Information")

    import platform
    import sys

    left, right = st.columns(2)

    with left:

        st.metric(
            "Operating System",
            platform.system()
        )

        st.metric(
            "Python",
            platform.python_version()
        )

        st.metric(
            "Database",
            "SQLite"
            if "sqlite" in settings.DATABASE_URL.lower()
            else "SQL Database"
        )

    with right:

        st.metric(
            "Platform",
            platform.machine()
        )

        st.metric(
            "Processor",
            platform.processor() or "Unknown"
        )

        st.metric(
            "Application",
            "AI Healthcare Agent"
        )

    st.divider()

    # =====================================================
    # STORAGE INFORMATION
    # =====================================================

    st.subheader("💾 Storage Overview")

    upload_files = len(os.listdir("logs/uploads")) if os.path.exists("logs/uploads") else 0

    appointment_files = os.path.exists("logs/appointments.json")

    reminder_files = os.path.exists("logs/reminders.json")

    s1, s2, s3 = st.columns(3)

    with s1:

        st.metric(
            "Uploaded Reports",
            upload_files
        )

    with s2:

        st.metric(
            "Appointments",
            "Available" if appointment_files else "None"
        )

    with s3:

        st.metric(
            "Reminders",
            "Available" if reminder_files else "None"
        )

    st.divider()

    # =====================================================
    # FOOTER
    # =====================================================

    st.markdown(
        """
<div style="text-align:center;
padding:20px;
opacity:0.75;
font-size:0.9rem;">

AI Healthcare Assistant Portal<br>

Built with Streamlit • LangGraph • OpenAI • SQLAlchemy • FAISS

</div>
""",
        unsafe_allow_html=True
    )
