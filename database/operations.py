from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Dict, Any, Optional
from database.models import Patient, Session as DBSession, ChatHistory, MedicalReport, AuditLog, ToolHistory
from config.logging_config import log_audit_event, system_logger

# ----------------- PATIENT CRUD -----------------

def create_patient(
    db: Session,
    first_name: str,
    last_name: str,
    email: str,
    date_of_birth: str,  # format 'YYYY-MM-DD'
    gender: str,
    ssn: Optional[str] = None,
    medical_history: Optional[str] = None,
    operator: str = "system"
) -> Patient:
    dob = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
    patient = Patient(
        first_name=first_name,
        last_name=last_name,
        email=email,
        encrypted_ssn=ssn,
        date_of_birth=dob,
        gender=gender,
        medical_history=medical_history
    )
    db.add(patient)
    db.flush()  # Populates patient.id

    add_audit_log(
        db,
        user_action="CREATE_PATIENT",
        target_table="patients",
        record_id=patient.id,
        performed_by=operator,
        change_summary=f"Created patient {first_name} {last_name} ({email})"
    )
    return patient

def get_patient(db: Session, patient_id: int) -> Optional[Patient]:
    return db.query(Patient).filter(Patient.id == patient_id).first()

def list_patients(db: Session) -> List[Patient]:
    return db.query(Patient).all()

def update_patient_history(db: Session, patient_id: int, history: str, operator: str = "system") -> Optional[Patient]:
    patient = get_patient(db, patient_id)
    if patient:
        old_history = patient.medical_history
        patient.medical_history = history
        db.flush()
        add_audit_log(
            db,
            user_action="UPDATE_PATIENT_HISTORY",
            target_table="patients",
            record_id=patient_id,
            performed_by=operator,
            change_summary=f"Updated history for patient ID {patient_id}. Length change: {len(old_history or '')} -> {len(history)}"
        )
    return patient


# ----------------- SESSION & CHAT HISTORY -----------------

def create_session(db: Session, session_id: str, patient_id: int) -> DBSession:
    session = DBSession(session_id=session_id, patient_id=patient_id)
    db.add(session)
    db.flush()
    return session

def get_session(db: Session, session_id: str) -> Optional[DBSession]:
    return db.query(DBSession).filter(DBSession.session_id == session_id).first()

def add_chat_message(
    db: Session,
    session_id: str,
    role: str,
    message: str,
    masked_message: str
) -> ChatHistory:
    chat = ChatHistory(
        session_id=session_id,
        role=role,
        message=message,
        masked_message=masked_message
    )
    db.add(chat)
    
    # Also update the session last activity
    sess = get_session(db, session_id)
    if sess:
        sess.last_activity = datetime.utcnow()
        
    db.flush()
    return chat

def get_chat_history(db: Session, session_id: str) -> List[ChatHistory]:
    return db.query(ChatHistory).filter(ChatHistory.session_id == session_id).order_by(ChatHistory.timestamp.asc()).all()


# ----------------- MEDICAL REPORTS -----------------

def create_medical_report(
    db: Session,
    patient_id: int,
    file_name: str,
    file_type: str,
    extracted_text: str,
    summary: Optional[str] = None,
    abnormal_findings: Optional[str] = None,
    operator: str = "system"
) -> MedicalReport:
    report = MedicalReport(
        patient_id=patient_id,
        file_name=file_name,
        file_type=file_type,
        extracted_text=extracted_text,
        summary=summary,
        abnormal_findings=abnormal_findings
    )
    db.add(report)
    db.flush()

    add_audit_log(
        db,
        user_action="UPLOAD_REPORT",
        target_table="medical_reports",
        record_id=report.id,
        performed_by=operator,
        change_summary=f"Uploaded report '{file_name}' for patient ID {patient_id}"
    )
    return report

def get_medical_reports(db: Session, patient_id: int) -> List[MedicalReport]:
    return db.query(MedicalReport).filter(MedicalReport.patient_id == patient_id).all()


# ----------------- TOOL HISTORY -----------------

def add_tool_execution(
    db: Session,
    session_id: str,
    tool_name: str,
    input_arguments: str,
    output_data: str,
    execution_status: str,
    duration_ms: float
) -> ToolHistory:
    history = ToolHistory(
        session_id=session_id,
        tool_name=tool_name,
        input_arguments=input_arguments,
        output_data=output_data,
        execution_status=execution_status,
        duration_ms=duration_ms
    )
    db.add(history)
    db.flush()
    return history

def get_tool_history(db: Session, session_id: str) -> List[ToolHistory]:
    return db.query(ToolHistory).filter(ToolHistory.session_id == session_id).order_by(ToolHistory.timestamp.asc()).all()


# ----------------- AUDIT LOGS -----------------

def add_audit_log(
    db: Session,
    user_action: str,
    target_table: Optional[str],
    record_id: Optional[int],
    performed_by: str,
    change_summary: Optional[str]
) -> AuditLog:
    log = AuditLog(
        user_action=user_action,
        target_table=target_table,
        record_id=record_id,
        performed_by=performed_by,
        change_summary=change_summary
    )
    db.add(log)
    db.flush()

    # Log to the secure text logger
    log_audit_event(
        action=user_action,
        target=f"{target_table}:{record_id}" if target_table else "None",
        user=performed_by,
        details={"change_summary": change_summary}
    )
    return log
