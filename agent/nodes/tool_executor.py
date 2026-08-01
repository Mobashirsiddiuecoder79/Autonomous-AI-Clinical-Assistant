import json
from typing import Dict, Any

from agent.state import AgentState

from config.logging_config import system_logger

from database.connection import get_db
from database.operations import add_tool_execution

from tools.registry import tool_registry


# ==========================================================
# TOOL EXECUTOR
# ==========================================================

def tool_executor_node(
    state: AgentState
) -> Dict[str, Any]:

    system_logger.info(
        "Tool Executor"
    )

    tool_call = state.get(
        "next_tool_call"
    )

    if not tool_call:

        return {

            "next_step": "reasoner"

        }

    tool_name = tool_call["name"]

    arguments = tool_call.get(
        "arguments",
        {}
    )

    outputs = state.get(
        "tool_outputs",
        []
    )

    completed = state.get(
        "completed_tasks",
        []
    )

    current_task = state.get(
        "current_task",
        tool_name
    )

    # ------------------------------------------------------
    # Lookup Tool
    # ------------------------------------------------------

    tool = tool_registry.get_tool(
        tool_name
    )

    if tool is None:

        outputs.append({

            "tool": tool_name,

            "success": False,

            "error": f"Unknown tool '{tool_name}'"

        })

        completed.append(
            tool_name
        )

        return {

            "tool_outputs": outputs,

            "completed_tasks": completed,

            "next_step": "reasoner"

        }

    # ------------------------------------------------------
    # Execute Tool
    # ------------------------------------------------------

    try:

        result = tool.run(
            **arguments
        )

    except Exception as e:

        system_logger.exception(e)

        result = {

            "success": False,

            "data": None,

            "error": str(e),

            "duration_ms": 0

        }

    # ------------------------------------------------------
    # Save Audit
    # ------------------------------------------------------

    try:

        with get_db() as db:

            add_tool_execution(

                db=db,

                session_id=state["session_id"],

                tool_name=tool_name,

                input_arguments=json.dumps(
                    arguments,
                    default=str
                ),

                output_data=json.dumps(
                    result,
                    default=str
                ),

                execution_status=(

                    "success"

                    if result["success"]

                    else

                    "failure"

                ),

                duration_ms=result.get(
                    "duration_ms",
                    0
                )

            )

    except Exception as e:

        system_logger.warning(

            f"Unable to log execution: {e}"

        )

    # ------------------------------------------------------
    # Store Output
    # ------------------------------------------------------

    outputs.append({

        "task": current_task,

        "tool": tool_name,

        "success": result["success"],

        "data": result.get(
            "data"
        ),

        "error": result.get(
            "error"
        )

    })

    completed.append(
        tool_name
    )

    return {

        "tool_outputs": outputs,

        "completed_tasks": completed,

        "next_step": "reasoner"

    }