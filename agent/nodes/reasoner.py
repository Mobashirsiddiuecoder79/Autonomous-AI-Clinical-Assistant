from typing import Dict, Any

from agent.state import AgentState
from config.logging_config import system_logger
from tools.registry import tool_registry


# ==========================================================
# AI Reasoner
# ==========================================================

def reasoner_node(
    state: AgentState,
) -> Dict[str, Any]:

    system_logger.info(
        "Reasoner Node"
    )

    tool_calls = state.get(
        "tool_calls",
        []
    )

    completed = state.get(
        "completed_tasks",
        []
    )

    # ------------------------------------------------------
    # Nothing to execute
    # ------------------------------------------------------

    if not tool_calls:

        return {

            "next_step": "final_answer"

        }

    # ------------------------------------------------------
    # Finished
    # ------------------------------------------------------

    if len(completed) >= len(tool_calls):

        return {

            "next_step": "final_answer"

        }

    tool_call = tool_calls[
        len(completed)
    ]

    tool_name = tool_call.get(
        "tool_name"
    )

    # ------------------------------------------------------
    # Validate tool
    # ------------------------------------------------------

    tool = tool_registry.get_tool(
        tool_name
    )

    if tool is None:

        system_logger.error(

            f"Unknown tool requested: {tool_name}"

        )

        errors = state.get(
            "errors",
            []
        )

        errors.append(

            f"Unknown tool: {tool_name}"

        )

        completed.append(
            tool_name
        )

        return {

            "errors": errors,

            "completed_tasks": completed,

            "next_step": "reasoner"

        }

    # ------------------------------------------------------
    # Execute
    # ------------------------------------------------------

    return {

        "current_task":

            f"Execute {tool_name}",

        "next_tool_call": {

            "name": tool_name,

            "arguments": tool_call.get(
                "arguments",
                {}
            )

        },

        "next_step": "tool_executor"

    }
