import json
from typing import Dict, Any

from config.llm import get_llm
from config.logging_config import system_logger

from database.connection import get_db
from memory.manager import MemoryManager

from agent.state import AgentState


memory_manager = MemoryManager()


# ==========================================================
# FINAL ANSWER
# ==========================================================

def final_answer_node(
    state: AgentState
) -> Dict[str, Any]:

    system_logger.info(
        "Final Answer Node"
    )

    llm = get_llm()

    patient_id = state.get(
        "patient_id",
        0
    )

    session_id = state.get(
        "session_id",
        ""
    )

    patient_context = state.get(
        "patient_context",
        ""
    )

    follow_up = state.get(
        "follow_up_question"
    )

    # --------------------------------------------------
    # Need Follow-up
    # --------------------------------------------------

    if follow_up:

        answer = follow_up

    # --------------------------------------------------
    # Gemini already answered
    # --------------------------------------------------

    elif state.get(
        "final_output"
    ):

        answer = state["final_output"]

    # --------------------------------------------------
    # Summarize Tool Results
    # --------------------------------------------------

    else:

        tool_outputs = state.get(
            "tool_outputs",
            []
        )

        prompt = f"""
You are an expert clinical AI assistant.

Patient Context:

{patient_context}

Tool Results:

{json.dumps(tool_outputs, indent=2)}

Write a professional response.

Rules:

- Explain results clearly.
- Mention any risks.
- Give practical recommendations.
- Never invent tool results.
- Use bullet points.
- End with:

"This information does not replace professional medical advice."
"""

        answer = llm.generate(
            prompt
        )

    # --------------------------------------------------
    # Save Memory
    # --------------------------------------------------

    try:

        with get_db() as db:

            memory_manager.store_interaction(

                db=db,

                session_id=session_id,

                patient_id=patient_id,

                role="assistant",

                message=answer

            )

    except Exception as e:

        system_logger.warning(

            f"Unable to save conversation: {e}"

        )

    return {

        "final_output": answer,

        "next_step": "end"

    }