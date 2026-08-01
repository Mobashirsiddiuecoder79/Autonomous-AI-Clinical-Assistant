from typing import Dict, Any
import re

from agent.state import AgentState
from config.logging_config import system_logger

from agent.legacy_nodes import (
    detect_intent,
    resolve_patient,
)


# ==========================================================
# INTENT DETECTOR
# ==========================================================

def intent_detector_node(
    state: AgentState,
) -> Dict[str, Any]:

    system_logger.info("Intent Detector")

    messages = state.get("messages", [])

    if not messages:

        return {

            "next_step": "end"

        }

    user_text = messages[-1]["content"]

    patient_id = state.get(
        "patient_id",
        0
    )

    email_match = re.search(
        r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b",
        user_text,
    )

    email = (

        email_match.group(0)

        if email_match

        else None

    )

    patient_id = resolve_patient(

        patient_id=patient_id,

        email=email,

    )

    intent = detect_intent(
        user_text
    )

    system_logger.info(

        f"Intent={intent} Patient={patient_id}"

    )

    return {

        "intent": intent,

        "patient_id": patient_id,

        "next_step": "planner",

    }