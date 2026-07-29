from typing import TypedDict, List, Dict, Any, Annotated, Optional


def append_messages(
    left: List[Dict[str, Any]],
    right: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Merge chat messages while preserving history.
    """
    return left + right


class AgentState(TypedDict):
    """
    Shared state passed between all LangGraph nodes.
    """

    # Conversation history
    messages: Annotated[List[Dict[str, Any]], append_messages]

    # Patient & Session
    patient_id: int
    session_id: str

    # Intent detected from user prompt
    intent: Optional[str]

    # Planning
    plan: List[str]
    completed_tasks: List[str]
    current_task: Optional[str]

    # Tool execution
    next_tool_call: Optional[Dict[str, Any]]
    tool_outputs: List[Dict[str, Any]]

    # Error tracking
    errors: List[str]

    # Workflow control
    next_step: str

    # Final assistant response
    final_output: Optional[str]