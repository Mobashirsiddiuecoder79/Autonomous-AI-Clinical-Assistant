from typing import Dict, Any, List
from sqlalchemy.orm import Session
from memory.vector_store import VectorMemoryManager
from memory.long_term import LongTermMemoryManager
from database.operations import get_patient, add_chat_message, get_chat_history
from security.masking import PIIMasker
from config.logging_config import system_logger

class MemoryManager:
    def __init__(self):
        self.vector_mem = VectorMemoryManager()
        self.long_term_mem = LongTermMemoryManager()

    def store_interaction(
        self,
        db: Session,
        session_id: str,
        patient_id: int,
        role: str,
        message: str
    ) -> None:
        """
        Saves chat messages into relational DB, masks PII for log security,
        and indexes the interaction in the vector database.
        """
        # 1. Mask PII for security compliance
        masked_message = PIIMasker.mask_text(message)
        
        # 2. Persist message in SQL DB
        add_chat_message(db, session_id, role, message, masked_message)
        
        # 3. Index interaction in Vector memory
        self.vector_mem.store_document(
            patient_id=patient_id,
            text=f"{role.upper()}: {message}",
            metadata={"session_id": session_id, "type": "chat_history"}
        )
        system_logger.info(f"Interaction stored and indexed for session {session_id}.")

    def get_patient_context(self, db: Session, patient_id: int, query: str) -> str:
        """
        Aggregates demographic details, clinical history from relational profile,
        and retrieves semantically relevant nodes from vector memory.
        """
        # 1. Load patient relational history
        patient = get_patient(db, patient_id)
        if not patient:
            return "No patient record found."

        dob_str = patient.date_of_birth.strftime("%Y-%m-%d")
        context = f"=== PATIENT PROFILE ===\n"
        context += f"Name: {patient.first_name} {patient.last_name}\n"
        context += f"Gender: {patient.gender}\n"
        context += f"DOB: {dob_str}\n"
        context += f"Baseline Medical History: {patient.medical_history or 'None recorded.'}\n\n"

        # 2. Search semantic logs/documents
        semantic_nodes = self.vector_mem.search_documents(patient_id, query, limit=3)
        if semantic_nodes:
            context += "=== SEMANTICALLY RELEVANT PAST RECORDS ===\n"
            for idx, node in enumerate(semantic_nodes, 1):
                context += f"Record [{idx}]: {node['text']}\n"
            context += "\n"

        return context

    def finalize_session(self, db: Session, session_id: str, patient_id: int) -> str:
        """
        Compresses conversation and updates the patient's long-term history column.
        """
        chats = get_chat_history(db, session_id)
        if not chats:
            return "No messages to summarize."

        messages_list = [{"role": c.role, "content": c.message} for c in chats]
        
        # Generate summary
        summary = self.long_term_mem.summarize_conversation(messages_list)
        
        # Persist summary to relational profile
        self.long_term_mem.persist_summary_to_profile(db, patient_id, summary)
        
        return summary
