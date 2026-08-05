from typing import Dict, Any

from config.logging_config import system_logger

from agent.state import AgentState

from agent.reflection.validator import ReflectionValidator
from agent.reflection.grounding import grounding_verifier
from agent.reflection.confidence import confidence_policy


validator = ReflectionValidator()


# ==========================================================
# LangGraph Node
# ==========================================================

def reflector_node(
    state: AgentState
) -> Dict[str, Any]:

    system_logger.info(
        "Reflection Node"
    )

    count = state.get(
        "reflection_count",
        0
    )

    # ------------------------------------------------------
    # Prevent Infinite Reflection
    # ------------------------------------------------------

    if count >= 2:

        system_logger.info(
            "Maximum reflection attempts reached."
        )

        return {

            "confidence": state.get(
                "confidence",
                0.50
            ),

            "reflection_feedback":
                "Maximum reflection attempts reached.",

            "next_step": "final_answer"

        }

    # ------------------------------------------------------
    # Rule Validation
    # ------------------------------------------------------

    ok, message = validator.validate_reasoning(
        state
    )

    if not ok:

        return {

            "confidence": 0.0,

            "reflection_feedback": message,

            "reflection_count": count + 1,

            "next_step": "reasoner"

        }

    ok, message = validator.validate_tool_selection(
        state
    )

    if not ok:

        return {

            "confidence": 0.0,

            "reflection_feedback": message,

            "reflection_count": count + 1,

            "next_step": "reasoner"

        }

    ok, message = validator.validate_tool_output(
        state
    )

    if not ok:

        return {

            "confidence": 0.0,

            "reflection_feedback": message,

            "reflection_count": count + 1,

            "next_step": "reasoner"

        }

    # ------------------------------------------------------
    # LLM Grounding Verification
    # ------------------------------------------------------

    result = grounding_verifier.verify(
        state
    )

    confidence = float(
        result.get(
            "confidence",
            0.0
        )
    )

    feedback = result.get(
        "feedback",
        ""
    )

    retry = bool(
        result.get(
            "retry",
            False
        )
    )

    grounded = bool(
        result.get(
            "grounded",
            True
        )
    )

    hallucination = bool(
        result.get(
            "hallucination",
            False
        )
    )

    system_logger.info(
        f"Reflection Confidence: {confidence:.2f}"
    )

    system_logger.info(
        f"Grounded: {grounded}"
    )

    system_logger.info(
        f"Hallucination: {hallucination}"
    )

    system_logger.info(
        f"Reflection Feedback: {feedback}"
    )

    # ------------------------------------------------------
    # Confidence Policy
    # ------------------------------------------------------

    decision = confidence_policy.evaluate(
        confidence
    )

    if retry or decision.retry:

        system_logger.info(
            "Reflection requested another reasoning cycle."
        )

        return {

            "reflection_count": count + 1,

            "confidence": confidence,

            "reflection_feedback": feedback,

            "next_step": "reasoner"

        }

    # ------------------------------------------------------
    # Reflection Approved
    # ------------------------------------------------------

    system_logger.info(
        "Reflection approved."
    )

    return {

        "confidence": confidence,

        "reflection_feedback": feedback,

        "next_step": "final_answer"

    }