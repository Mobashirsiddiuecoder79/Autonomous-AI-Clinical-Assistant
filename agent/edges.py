from typing import Literal
from agent.state import AgentState
from config.logging_config import system_logger

def route_after_intent(state: AgentState) -> str:
    # Router for Intent Detector node
    next_step = state.get("next_step", "planner")
    system_logger.info(f"Routing edge from intent detector -> {next_step}")
    return next_step

def route_after_reasoner(state: AgentState) -> str:
    # Router for Reasoner node
    next_step = state.get("next_step", "reasoner")
    system_logger.info(f"Routing edge from reasoner -> {next_step}")
    return next_step

def route_after_reflector(state: AgentState) -> str:
    # Router for Reflector node
    next_step = state.get("next_step", "final_answer")
    system_logger.info(f"Routing edge from reflector -> {next_step}")
    return next_step
