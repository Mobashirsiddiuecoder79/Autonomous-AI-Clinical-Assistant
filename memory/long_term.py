from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from config.settings import settings
from config.logging_config import system_logger
from database.operations import get_patient, update_patient_history

class LongTermMemoryManager:
    def __init__(self):
        # Configure model fallback
        if not settings.OPENAI_API_KEY or "mock" in settings.OPENAI_API_KEY or "your_openai" in settings.OPENAI_API_KEY:
            self.model = None
        else:
            self.model = ChatOpenAI(model="gpt-4o-mini", openai_api_key=settings.OPENAI_API_KEY, temperature=0.3)

    def summarize_conversation(self, messages: List[Dict[str, str]]) -> str:
        """
        Uses LLM to summarize conversation history.
        Falls back to rule-based summary if LLM credentials are mock or fail.
        """
        if not messages:
            return "No previous dialogue recorded."

        formatted_dialogue = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in messages])

        if not self.model:
            # Fallback simple rule-based compressor
            lines = [m['content'] for m in messages if m['role'] in ('user', 'assistant')]
            summary = f"[Rule-based Summary]: Conversation spans {len(messages)} turns. Key inputs: "
            summary += "; ".join([line[:60] + "..." for line in lines[:3]])
            return summary

        prompt_template = """You are a professional medical scribe. Review the following conversation between a patient/practitioner and the AI Assistant. 
Summarize the key medical symptoms, lab results discussed, diagnostics proposed, and next steps. Make it concise and clinically structured.

CONVERSATION:
{dialogue}

CLINICAL SUMMARY:"""
        
        try:
            prompt = PromptTemplate.from_template(prompt_template)
            chain = prompt | self.model
            result = chain.invoke({"dialogue": formatted_dialogue})
            return result.content.strip()
        except Exception as e:
            system_logger.error(f"Failed to generate LLM summary: {e}. Falling back.")
            return f"[Fallback Summary]: Clinical chat containing {len(messages)} messages."

    def persist_summary_to_profile(self, db, patient_id: int, new_summary: str) -> bool:
        """Appends the new session summary to the patient's existing history profile."""
        patient = get_patient(db, patient_id)
        if not patient:
            return False
        
        current_history = patient.medical_history or ""
        updated_history = f"{current_history}\n\n[Session Summary - {datetime_now_str()}]: {new_summary}".strip()
        update_patient_history(db, patient_id, updated_history)
        return True

def datetime_now_str() -> str:
    from datetime import datetime
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
