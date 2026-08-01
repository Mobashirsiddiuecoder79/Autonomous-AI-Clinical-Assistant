from typing import Dict, Any

from langgraph.graph import StateGraph, END

from agent.state import AgentState

from agent.edges import (
    route_after_intent,
    route_after_planner,
    route_after_reasoner,
    route_after_reflector,
)
from agent.nodes import (
    intent_detector_node,
    planner_node,
    reasoner_node,
    tool_executor_node,
    final_answer_node,
)

# Temporary until we migrate reflector
from agent.legacy_nodes import reflector_node



from config.logging_config import system_logger
from security.sanitizer import InputSanitizer

from database.connection import get_db
from memory.manager import MemoryManager


# ============================================================
# Build Workflow
# ============================================================

workflow = StateGraph(AgentState)


# ============================================================
# Register Nodes
# ============================================================

workflow.add_node(
    "intent_detector",
    intent_detector_node
)

workflow.add_node(
    "planner",
    planner_node
)

workflow.add_node(
    "reasoner",
    reasoner_node
)

workflow.add_node(
    "tool_executor",
    tool_executor_node
)

workflow.add_node(
    "reflector",
    reflector_node
)

workflow.add_node(
    "final_answer",
    final_answer_node
)


# ============================================================
# Entry Point
# ============================================================

workflow.set_entry_point("intent_detector")


# ============================================================
# Edges
# ============================================================

workflow.add_conditional_edges(
    "intent_detector",
    route_after_intent,
    {
        "planner": "planner",
        "end": END,
    },
)

workflow.add_conditional_edges(
    "planner",
    route_after_planner,
    {
        "reasoner": "reasoner",
        "final_answer": "final_answer",
    },
)

workflow.add_conditional_edges(
    "reasoner",
    route_after_reasoner,
    {
        "tool_executor": "tool_executor",
        "reflector": "reflector",
        "reasoner": "reasoner",
        "final_answer": "final_answer",
    },
)

workflow.add_edge(
    "tool_executor",
    "reasoner"
)

workflow.add_conditional_edges(
    "reflector",
    route_after_reflector,
    {
        "reasoner": "reasoner",
        "final_answer": "final_answer",
    },
)

workflow.add_edge(
    "final_answer",
    END
)


# ============================================================
# Compile Graph
# ============================================================

compiled_graph = workflow.compile()


# ============================================================
# Memory Manager
# ============================================================

memory_manager = MemoryManager()



# ============================================================
# Execute Workflow
# ============================================================


def run_agent_flow(
    session_id: str,
    patient_id: int,
    prompt: str
) -> Dict[str, Any]:

    system_logger.info(
        f"Starting agent workflow | session={session_id} patient={patient_id}"
    )

    # --------------------------------------------------------
    # Sanitize User Input
    # --------------------------------------------------------

    cleaned_prompt = InputSanitizer.clean_text(prompt)

    if InputSanitizer.check_prompt_injection(cleaned_prompt):

        system_logger.warning(
            "Prompt injection detected."
        )

        return {

            "final_output":
                "Security warning: The request appears to contain prompt injection or system override instructions. Please rephrase your request.",

            "plan": [],

            "completed_tasks": [],

            "tool_outputs": []
        }

    # --------------------------------------------------------
    # Initial Graph State
    # --------------------------------------------------------

    initial_state = {

    "messages": [
        {
            "role": "user",
            "content": cleaned_prompt
        }
    ],

    "patient_id": patient_id,

    "session_id": session_id,

    "patient_context": None,

    "intent": None,

    "reasoning": None,

    "requires_tool": False,

    "plan": [],

    "completed_tasks": [],

    "current_task": None,

    "tool_calls": [],

    "next_tool_call": None,

    "tool_outputs": [],

    "follow_up_question": None,

    "errors": [],

    "next_step": "intent_detector",

    "final_output": None,
}

    # --------------------------------------------------------
    # Save User Message
    # --------------------------------------------------------

    try:

        with get_db() as db:

            memory_manager.store_interaction(

                db=db,

                session_id=session_id,

                patient_id=patient_id,

                role="user",

                message=cleaned_prompt

            )

    except Exception as e:

        system_logger.error(
            f"Unable to save chat history: {e}"
        )

    # --------------------------------------------------------
    # Execute LangGraph
    # --------------------------------------------------------

    try:

        final_state = compiled_graph.invoke(
            initial_state
        )

        system_logger.info(
            "Workflow completed successfully."
        )

        return final_state

    except Exception as e:

        system_logger.exception(
            "Workflow execution failed."
        )

        return {

            "final_output":
                f"Agent execution failed.\n\n{str(e)}",

            "plan": [],

            "completed_tasks": [],

            "tool_outputs": []
        }

    
    