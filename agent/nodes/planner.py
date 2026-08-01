import json
from typing import Dict, Any

from config.llm import get_llm
from config.logging_config import system_logger

from tools.registry import tool_registry

from agent.state import AgentState


class AIPlanner:

    def __init__(self):

        self.llm = get_llm()

    # =====================================================
    # Build Tool Description
    # =====================================================

    def build_tool_catalog(self) -> str:

        catalog = ""

        for tool in tool_registry.list_tools():

            schema = tool.args_schema.model_json_schema()

            catalog += f"""

Tool Name:
{tool.name}

Description:
{tool.description}

Arguments:
{json.dumps(schema, indent=2)}

---------------------------------------

"""

        return catalog

    # =====================================================
    # Planner Prompt
    # =====================================================

    def build_prompt(self, question: str) -> str:

        return f"""
You are the planning engine of an Autonomous Clinical AI Assistant.

Available tools:

{self.build_tool_catalog()}

Your job:

1. Decide whether a tool is needed.
2. If needed, choose the correct tool.
3. Extract all arguments.
4. Never invent tool names.
5. Never invent arguments.

Return ONLY valid JSON.

Schema

{{
    "intent":"",

    "requires_tool":true,

    "tool_calls":[
        {{
            "tool_name":"",
            "arguments":{{}}
        }}
    ],

    "direct_answer":null,

    "follow_up_question":null,

    "reasoning":""
}}

User Question

{question}
"""

    # =====================================================
    # Generate Plan
    # =====================================================

    def generate_plan(self, question: str):

        prompt = self.build_prompt(question)

        return self.llm.generate_json(prompt)


planner = AIPlanner()


# =====================================================
# LangGraph Node
# =====================================================


def planner_node(state: AgentState) -> Dict[str, Any]:

    system_logger.info("Gemini Planner")

    question = state["messages"][-1]["content"]

    result = planner.generate_plan(question)
    print("\n" + "=" * 80)
    print("PLANNER OUTPUT")
    print(json.dumps(result, indent=2))
    print("=" * 80 + "\n")

    return {
        "intent": result.get("intent", "general"),
        "reasoning": result.get("reasoning"),
        "requires_tool": result.get("requires_tool", False),
        "tool_calls": result.get("tool_calls", []),
        "follow_up_question": result.get("follow_up_question"),
        "plan": [call["tool_name"] for call in result.get("tool_calls", [])],
        "completed_tasks": [],
        "final_output": result.get("direct_answer"),
        "next_step": (
            "reasoner" if result.get("requires_tool", False) else "final_answer"
        ),
    }
