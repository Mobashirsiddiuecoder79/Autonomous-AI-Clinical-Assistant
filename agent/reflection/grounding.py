import json
from typing import Any, Dict

from config.llm import get_llm
from agent.state import AgentState
from agent.reflection.prompts import ReflectionPrompts


class GroundingVerifier:
    """
    Uses the LLM to verify that the draft answer is
    grounded in the available tool outputs.
    """

    def __init__(self):

        self.llm = get_llm()

    # =====================================================
    # Verify Grounding
    # =====================================================

    def verify(
        self,
        state: AgentState,
    ) -> Dict[str, Any]:

        prompt = ReflectionPrompts.grounding_prompt(

            question=state["messages"][-1]["content"],

            intent=state.get(
                "intent",
                ""
            ),

            reasoning=state.get(
                "reasoning",
                ""
            ),

            tool_outputs=json.dumps(
                state.get(
                    "tool_outputs",
                    []
                ),
                indent=2
            ),

            draft_answer=str(
                state.get(
                    "final_output",
                    ""
                )
            )
        )

        return self.llm.generate_json(
            prompt
        )


grounding_verifier = GroundingVerifier()