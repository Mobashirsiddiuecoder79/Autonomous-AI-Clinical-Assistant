from typing import TypedDict, List, Dict, Any, Annotated, Optional


# ==========================================================
# MESSAGE MERGER
# ==========================================================

def append_messages(
    left: List[Dict[str, Any]],
    right: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Merge conversation history while preserving
    previous messages.
    """
    return left + right


# ==========================================================
# LANGGRAPH SHARED STATE
# ==========================================================

class AgentState(TypedDict):
    """
    Shared state passed between every LangGraph node.
    """

    # ------------------------------------------------------
    # Conversation
    # ------------------------------------------------------

    messages: Annotated[
        List[Dict[str, Any]],
        append_messages
    ]

    # ------------------------------------------------------
    # Patient Information
    # ------------------------------------------------------

    patient_id: int

    session_id: str

    patient_context: Optional[str]

    # ------------------------------------------------------
    # AI Understanding
    # ------------------------------------------------------

    intent: Optional[str]

    reasoning: Optional[str]

    requires_tool: bool

    follow_up_question: Optional[str]

    # ------------------------------------------------------
    # AI Planner Output
    # ------------------------------------------------------

    tool_calls: List[
        Dict[str, Any]
    ]

    # ------------------------------------------------------
    # Workflow Planning
    # ------------------------------------------------------

    plan: List[str]

    completed_tasks: List[str]

    current_task: Optional[str]

    # ------------------------------------------------------
    # Tool Execution
    # ------------------------------------------------------

    next_tool_call: Optional[
        Dict[str, Any]
    ]

    tool_outputs: List[
        Dict[str, Any]
    ]

    # ------------------------------------------------------
    # Errors
    # ------------------------------------------------------

    errors: List[str]

    # ------------------------------------------------------
    # Workflow
    # ------------------------------------------------------

    next_step: str

    # ------------------------------------------------------
    # Final Assistant Response
    # ------------------------------------------------------

    final_output: Optional[str]