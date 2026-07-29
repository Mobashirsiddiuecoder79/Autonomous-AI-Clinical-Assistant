from sqlalchemy import Column, Integer, String, Date, Text, DateTime, Float, ForeignKey, TypeDecorator
from sqlalchemy.orm import relationship
from datetime import datetime
from database.connection import Base
from config.settings import settings
from config.logging_config import system_logger

# Transparent Encryption Decorator for HIPAA PHI Protection
class EncryptedString(TypeDecorator):
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        try:
            return settings.cipher_suite.encrypt(value.encode("utf-8")).decode("utf-8")
        except Exception as e:
            system_logger.error(f"Encryption error for value: {e}")
            return value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        try:
            return settings.cipher_suite.decrypt(value.encode("utf-8")).decode("utf-8")
        except Exception as e:
            system_logger.error(f"Decryption error: {e}. Returning raw/obfuscated string.")
            return "[DECRYPTION_ERROR]"

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    encrypted_ssn = Column(EncryptedString(512), nullable=True) # Encrypted
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(50), nullable=False)
    medical_history = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    sessions = relationship("Session", back_populates="patient", cascade="all, delete-orphan")
    reports = relationship("MedicalReport", back_populates="patient", cascade="all, delete-orphan")

class Session(Base):
    __tablename__ = "sessions"

    session_id = Column(String(100), primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    patient = relationship("Patient", back_populates="sessions")
    chat_histories = relationship("ChatHistory", back_populates="session", cascade="all, delete-orphan")
    tool_histories = relationship("ToolHistory", back_populates="session", cascade="all, delete-orphan")

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), ForeignKey("sessions.session_id"), nullable=False)
    role = Column(String(50), nullable=False)  # 'user', 'assistant', 'system'
    message = Column(Text, nullable=False)     # Raw message
    masked_message = Column(Text, nullable=False) # Log-safe masked message
    timestamp = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="chat_histories")

class MedicalReport(Base):
    __tablename__ = "medical_reports"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # 'pdf', 'image', 'docx', etc.
    extracted_text = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    abnormal_findings = Column(Text, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="reports")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_action = Column(String(100), nullable=False)
    target_table = Column(String(100), nullable=True)
    record_id = Column(Integer, nullable=True)
    performed_by = Column(String(100), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    change_summary = Column(Text, nullable=True)

class ToolHistory(Base):
    __tablename__ = "tool_history"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), ForeignKey("sessions.session_id"), nullable=False)
    tool_name = Column(String(100), nullable=False)
    input_arguments = Column(Text, nullable=True)
    output_data = Column(Text, nullable=True)
    execution_status = Column(String(50), nullable=False) # 'success', 'failure'
    duration_ms = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="tool_histories")
