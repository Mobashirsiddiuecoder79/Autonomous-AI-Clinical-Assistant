from agent.state import AgentState


class ReflectionValidator:

    # =====================================================
    # Reasoning Validation
    # =====================================================

    def validate_reasoning(
        self,
        state: AgentState,
    ) -> tuple[bool, str]:

        reasoning = state.get(
            "reasoning",
            ""
        )

        if not reasoning:

            return (
                False,
                "Reasoning is missing."
            )

        return (
            True,
            ""
        )

    # =====================================================
    # Tool Selection Validation
    # =====================================================

    def validate_tool_selection(
        self,
        state: AgentState,
    ) -> tuple[bool, str]:

        if not state.get(
            "requires_tool",
            False
        ):

            return (
                True,
                ""
            )

        tool_calls = state.get(
            "tool_calls",
            []
        )

        if not tool_calls:

            return (
                False,
                "Planner did not choose any tool."
            )

        tool_name = tool_calls[0].get(
            "tool_name",
            ""
        )

        if not tool_name:

            return (
                False,
                "Tool name missing."
            )

        return (
            True,
            ""
        )

    # =====================================================
    # Tool Output Validation
    # =====================================================

    def validate_tool_output(
        self,
        state: AgentState,
    ) -> tuple[bool, str]:

        if not state.get(
            "requires_tool",
            False
        ):

            return (
                True,
                ""
            )

        tool_outputs = state.get(
            "tool_outputs",
            []
        )

        if not tool_outputs:

            return (
                False,
                "No tool output found."
            )

        return (
            True,
            ""
        )

    # =====================================================
    # Final Answer Validation
    # =====================================================

    def validate_final_answer(
        self,
        state: AgentState,
    ) -> tuple[bool, str]:

        answer = state.get(
            "final_output"
        )

        if not answer:

            return (
                False,
                "Final answer missing."
            )

        return (
            True,
            ""
        )
