import os
import textwrap
from html import escape

import streamlit as st

from database.connection import get_db
from database.operations import (
    create_medical_report,
    get_medical_reports,
    get_patient
)
from database.models import MedicalReport

from tools.document_tools import (
    MedicalReportParserTool,
    LabReportAnalyzerTool
)


# ==========================================================
# CONFIG
# ==========================================================

UPLOAD_DIR = "logs/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ==========================================================
# HTML HELPER
# ==========================================================

def html(content: str):
    st.markdown(
        textwrap.dedent(content),
        unsafe_allow_html=True
    )


# ==========================================================
# PAGE
# ==========================================================

def show_reports():

    # ------------------------------------------------------
    # ACTIVE PATIENT
    # ------------------------------------------------------

    if (
        "active_patient_id" not in st.session_state
        or st.session_state.active_patient_id <= 0
    ):
        st.warning(
            "Please select a patient from Dashboard."
        )
        return

    patient_id = st.session_state.active_patient_id

    with get_db() as db:

        patient = get_patient(
            db,
            patient_id
        )

    # ------------------------------------------------------
    # HEADER
    # ------------------------------------------------------

    html(f"""
<div class="glass-card">

<div style="
display:flex;
justify-content:space-between;
align-items:center;">

<div>

<h1 class="gradient-title">

🧪 Medical Report Analysis Center

</h1>

<div style="
color:#94a3b8;
font-size:15px;">

AI-powered Laboratory &
Diagnostic Report Analyzer

</div>

</div>

<div style="text-align:right;">

<div style="
color:#22c55e;
font-size:16px;
font-weight:700;">

🟢 AI Ready

</div>

<div style="
color:#94a3b8;
font-size:14px;">

Patient:
<b>{patient.first_name} {patient.last_name}</b>

</div>

</div>

</div>

</div>
""")

    # ------------------------------------------------------
    # UPLOAD SECTION
    # ------------------------------------------------------

    st.markdown("## 📤 Upload Laboratory Report")

    uploaded_file = st.file_uploader(

        "Supported formats: PDF, PNG, JPG, JPEG, TXT",

        type=[
            "pdf",
            "png",
            "jpg",
            "jpeg",
            "txt"
        ],

        key="medical_report_upload"

    )

    # ------------------------------------------------------
    # FILE UPLOADED
    # ------------------------------------------------------

    if uploaded_file:

        file_path = os.path.join(
            UPLOAD_DIR,
            uploaded_file.name
        )

        with open(file_path, "wb") as f:

            f.write(
                uploaded_file.getbuffer()
            )

        html(f"""
<div class="glass-card">

<h3>📄 Uploaded Report</h3>

<table style="width:100%;">

<tr>

<td><b>Filename</b></td>

<td>{uploaded_file.name}</td>

</tr>

<tr>

<td><b>Size</b></td>

<td>{round(uploaded_file.size/1024,2)} KB</td>

</tr>

<tr>

<td><b>Status</b></td>

<td style="color:#22c55e;">
Ready for Analysis
</td>

</tr>

</table>

</div>
""")

        if st.button(

            "🚀 Start AI Analysis",

            use_container_width=True,

            key="analyze_btn"

        ):

            progress = st.progress(0)

            status = st.empty()

            # ------------------------------------------
            # PARSE REPORT
            # ------------------------------------------

            status.info(
                "📄 Extracting report..."
            )

            progress.progress(20)

            parser = MedicalReportParserTool()

            parse_result = parser.run(
                file_path=file_path
            )

            if not parse_result["success"]:

                st.error(
                    parse_result["error"]
                )

                return

            raw_text = parse_result["data"]["raw_text"]

            # ------------------------------------------
            # ANALYZE REPORT
            # ------------------------------------------

            status.info(
                "🧠 AI analyzing biomarkers..."
            )

            progress.progress(60)

            analyzer = LabReportAnalyzerTool()

            analysis = analyzer.run(
                report_text=raw_text
            )

            if not analysis["success"]:

                st.error(
                    analysis["error"]
                )

                return

            data = analysis["data"]

            progress.progress(90)

            # ------------------------------------------
            # SAVE DATABASE
            # ------------------------------------------

            with get_db() as db:

                create_medical_report(

                    db=db,

                    patient_id=patient_id,

                    file_name=uploaded_file.name,

                    file_type=uploaded_file.name.split(".")[-1],

                    extracted_text=raw_text,

                    summary=data.get(
                        "summary",
                        ""
                    ),

                    abnormal_findings=data.get(
                        "recommendations",
                        ""
                    ),

                    operator="AI Agent"

                )

            # --------------------------------------------------
            # KEEP ONLY THE 5 LATEST REPORTS FOR THIS PATIENT
            # --------------------------------------------------

            with get_db() as db:

                patient_reports = get_medical_reports(
                    db,
                    patient_id
                )

                old_reports = patient_reports[5:]

                for old_report in old_reports:

                    old_file_path = os.path.join(
                        UPLOAD_DIR,
                        old_report.file_name
                    )

                    if os.path.exists(old_file_path):
                        try:
                            os.remove(old_file_path)
                        except OSError:
                            pass

                    db.delete(old_report)

                if old_reports:
                    db.commit()

            progress.progress(100)

            status.success(
                "✅ Analysis Complete"
            )

            st.success(
                "Medical report successfully analyzed."
            )

            biomarkers = data.get(
                "biomarkers_found",
                []
            )

            abnormal = data.get(
                "abnormalities_count",
                0
            )

            summary = data.get(
                "summary",
                ""
            )

            recommendations = data.get(
                "recommendations",
                ""
            )
    
            # ======================================================
            # AI ANALYSIS DASHBOARD
            # ======================================================

            st.divider()

            st.markdown("## 🧠 AI Analysis Summary")

            c1, c2, c3 = st.columns(3)

            with c1:

                st.metric(
                    "Biomarkers",
                    len(biomarkers)
                )

            with c2:

                st.metric(
                    "Abnormal",
                    abnormal
                )

            with c3:

                status = (
                    "Normal"
                    if abnormal == 0
                    else "Attention Needed"
                )

                st.metric(
                    "Overall",
                    status
                )

            # ======================================================
            # SUMMARY
            # ======================================================

            html(f"""
<div class="glass-card">

<h3>📋 Clinical Summary</h3>

<hr>

<p>

{summary}

</p>

</div>
""")

            # ======================================================
            # RECOMMENDATIONS
            # ======================================================

            html(f"""
<div class="glass-card">

<h3>💡 Recommendations</h3>

<hr>

<p>

{recommendations}

</p>

</div>
""")

            # ======================================================
            # BIOMARKER TABLE
            # ======================================================

            if biomarkers:

                st.markdown("## 🧪 Biomarker Results")

                display_rows = []

                for item in biomarkers:

                    display_rows.append({

                        "Biomarker":
                            item.get("biomarker"),

                        "Measured Value":
                            item.get("value"),

                        "Reference Range":
                            item.get("reference_range"),

                        "Status":
                            item.get("status")

                    })

                st.dataframe(

                    display_rows,

                    use_container_width=True,

                    hide_index=True

                )

            else:

                st.info(
                    "No biomarkers were detected in the uploaded report."
                )

            # ======================================================
            # RAW EXTRACTED TEXT
            # ======================================================

            with st.expander(
                "📄 View Extracted Report Text",
                expanded=False
            ):

                st.text_area(

                    "Extracted Text",

                    value=raw_text,

                    height=300,

                    disabled=True,

                    key="report_raw_text"

                )

            # ======================================================
            # REFRESH TO UPDATE HISTORY
            # ======================================================

            st.rerun()

    # ==========================================================
    # REPORT HISTORY
    # ==========================================================

    st.divider()

    st.markdown("## 📚 Patient Report Archive")

    with get_db() as db:

        reports = get_medical_reports(
            db,
            patient_id
        )

    if not reports:

        st.info(
            "No previous laboratory reports available."
        )

        return

    st.caption(
        f"{len(reports)} report(s) found for this patient."
    )

    # ----------------------------------------------------------
    # SHOW HISTORY
    # ----------------------------------------------------------

    for index, report in enumerate(reports):

        with st.expander(

            f"📄 {report.file_name}   |   {report.uploaded_at.strftime('%d %b %Y  %H:%M')}",

            expanded=False

        ):

            # --------------------------------------------------
            # REPORT INFORMATION
            # --------------------------------------------------

            c1, c2, c3 = st.columns(3)

            with c1:

                st.metric(
                    "Report ID",
                    report.id
                )

            with c2:

                st.metric(
                    "File Type",
                    report.file_type.upper()
                )

            with c3:

                st.metric(
                    "Uploaded",
                    report.uploaded_at.strftime("%Y-%m-%d")
                )

            # --------------------------------------------------
            # SUMMARY
            # --------------------------------------------------

            html(f"""
<div class="glass-card">

<h3>📋 Clinical Summary</h3>

<p>

{report.summary or "No summary available."}

</p>

</div>
""")

            # --------------------------------------------------
            # ABNORMAL FINDINGS
            # --------------------------------------------------

            html(f"""
<div class="glass-card">

<h3>⚠ Clinical Review & Recommendations</h3>

<p>

{report.abnormal_findings or "No abnormal findings."}

</p>

</div>
""")

            # --------------------------------------------------
            # EXTRACTED TEXT
            # --------------------------------------------------

            # --------------------------------------------------
            # PROFESSIONAL EXTRACTED REPORT VIEWER
            # --------------------------------------------------

            extracted_text = escape(
                report.extracted_text or "No report content available."
            )

            st.html(f"""
<div style="
    margin-top:24px;
    border:1px solid rgba(148,163,184,0.18);
    border-radius:18px;
    overflow:hidden;
    background:#111827;
    box-shadow:0 10px 30px rgba(0,0,0,0.16);
">

    <div style="
        padding:24px 28px;
        max-height:500px;
        overflow-y:auto;
        background:#111827;
    ">

        <div style="
            color:#d1d5db;
            font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;
            font-size:13px;
            line-height:1.75;
            letter-spacing:0.05px;
            white-space:pre-wrap;
            word-break:break-word;
        ">{extracted_text}</div>

    </div>

</div>
""")
    # ==========================================================
    # ARCHIVE STATISTICS
    # ==========================================================

    st.divider()

    st.markdown("## 📈 Archive Statistics")

    total_reports = len(reports)

    total_text = sum(
        len(r.extracted_text or "")
        for r in reports
    )

    total_size = 0

    for r in reports:

        path = os.path.join(
            UPLOAD_DIR,
            r.file_name
        )

        if os.path.exists(path):

            total_size += os.path.getsize(path)

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "Reports Stored",
            total_reports
        )

    with c2:

        st.metric(
            "Characters Extracted",
            f"{total_text:,}"
        )

    with c3:

        st.metric(
            "Storage Used",
            f"{total_size/1024:.1f} KB"
        )

    # ==========================================================
    # DOWNLOAD SECTION
    # ==========================================================

    st.divider()

    st.markdown("## 📥 Export")

    latest_report = reports[0]

    st.download_button(

        label="⬇ Download Latest Extracted Text",

        data=latest_report.extracted_text or "",

        file_name=f"{latest_report.file_name}_text.txt",

        mime="text/plain",

        use_container_width=True

    )

    # ==========================================================
    # REPORT MANAGEMENT
    # ==========================================================

    st.divider()

    st.markdown("## 🗑️ Report Management")

    report_options = {
        f"{report.file_name} — {report.uploaded_at.strftime('%d %b %Y %H:%M')} (ID: {report.id})": report
        for report in reports
    }

    selected_label = st.selectbox(
        "Select a report to delete",
        options=list(report_options.keys()),
        key="delete_report_selector"
    )

    selected_report = report_options[selected_label]

    if st.button(
        "🗑️ Delete Selected Report",
        use_container_width=True,
        type="secondary",
        key="delete_selected_report"
    ):

        with get_db() as db:

            report_to_delete = db.query(MedicalReport).filter(
                MedicalReport.id == selected_report.id,
                MedicalReport.patient_id == patient_id
            ).first()

            if report_to_delete:

                file_path = os.path.join(
                    UPLOAD_DIR,
                    report_to_delete.file_name
                )

                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except OSError:
                        pass

                db.delete(report_to_delete)
                db.commit()

                st.success(
                    f"Report '{selected_report.file_name}' deleted successfully."
                )
                st.rerun()
            else:
                st.error("Selected report could not be found.")

    # ==========================================================
    # FOOTER
    # ==========================================================

    st.divider()

    html("""
<div style="
text-align:center;
padding:30px;
color:#94a3b8;
font-size:14px;">

🏥 AI Healthcare Assistant Portal

<br><br>

Medical Report Analysis powered by

<b>Streamlit • LangGraph • OpenAI • SQLAlchemy • FAISS</b>

<br><br>

© 2026 Healthcare AI Platform

</div>
""")
