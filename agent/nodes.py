import json
import re
from typing import Dict, Any, Optional

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

from config.settings import settings
from config.logging_config import system_logger

from agent.state import AgentState

from agent.prompts import (
    INTENT_DETECTOR_PROMPT,
    PLANNER_PROMPT,
    REASONING_PROMPT,
    REFLECTOR_PROMPT,
    FINAL_SUMMARIZER_PROMPT
)

from database.connection import get_db
from database.operations import (
    list_patients,
    add_tool_execution
)

from tools.registry import tool_registry

from memory.manager import MemoryManager


# ==========================================================
# GLOBALS
# ==========================================================

memory_manager = MemoryManager()


# ==========================================================
# LLM
# ==========================================================

def get_llm(
    temperature: float = 0.0
):

    key = settings.OPENAI_API_KEY

    if (
        not key
        or "mock" in key.lower()
        or "your_openai" in key.lower()
    ):
        return None

    return ChatOpenAI(
        model="gpt-4o-mini",
        openai_api_key=key,
        temperature=temperature
    )


# ==========================================================
# PATIENT CONTEXT
# ==========================================================

def get_patient_profile_context(
    patient_id: int
) -> str:

    if patient_id <= 0:
        return "No patient selected."

    with get_db() as db:

        return memory_manager.get_patient_context(
            db=db,
            patient_id=patient_id,
            query="demographics history"
        )


# ==========================================================
# PATIENT RESOLUTION
# ==========================================================

def resolve_patient(
    patient_id: int,
    email: Optional[str] = None,
    name: Optional[str] = None
) -> int:

    if patient_id > 0:
        return patient_id

    with get_db() as db:

        patients = list_patients(db)

    if not patients:
        return 0

    if email:

        for p in patients:

            if p.email.lower() == email.lower():

                return p.id

    if name:

        q = name.lower()

        for p in patients:

            if (
                q in p.first_name.lower()
                or
                q in p.last_name.lower()
            ):
                return p.id

    return patients[0].id


# ==========================================================
# RULE BASED INTENT DETECTOR
# ==========================================================

def detect_intent(
    text: str
) -> str:

    t = text.lower()

    if any(x in t for x in [
        "bmi",
        "body mass",
        "weight",
        "height"
    ]):
        return "bmi"

    if any(x in t for x in [
        "appointment",
        "book",
        "schedule",
        "doctor"
    ]):
        return "appointment"

    if any(x in t for x in [
        "drug",
        "interaction",
        "medicine",
        "tablet"
    ]):
        return "drug"

    if any(x in t for x in [
        "symptom",
        "pain",
        "fever",
        "cough",
        "headache",
        "breathing",
        "chest"
    ]):
        return "symptom"

    if any(x in t for x in [
        "cholesterol",
        "hdl",
        "ldl",
        "glucose",
        "hemoglobin",
        "lab"
    ]):
        return "lab"

    if any(x in t for x in [
        "report",
        "pdf",
        "ocr",
        "scan"
    ]):
        return "report"

    if any(x in t for x in [
        "search",
        "guideline",
        "research",
        "who",
        "what is"
    ]):
        return "search"

    return "general"


# ==========================================================
# NODE 1
# INTENT DETECTOR
# ==========================================================

def intent_detector_node(
    state: AgentState
) -> Dict[str, Any]:

    system_logger.info("Intent Detector")

    messages = state.get("messages", [])

    if not messages:

        return {
            "next_step": "end"
        }

    user_text = messages[-1]["content"]

    patient_id = state.get(
        "patient_id",
        0
    )

    email_match = re.search(
        r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b",
        user_text
    )

    email = (
        email_match.group(0)
        if email_match
        else None
    )

    patient_id = resolve_patient(
        patient_id=patient_id,
        email=email
    )

    intent = detect_intent(
        user_text
    )

    system_logger.info(
        f"Intent={intent} Patient={patient_id}"
    )

    return {

        "intent": intent,

        "patient_id": patient_id,

        "next_step": "planner"

    }
# ==========================================================
# HELPER
# ==========================================================

def build_plan(intent: str) -> list[str]:
    """
    Builds a workflow plan according to detected intent.
    """

    plans = {

        "bmi": [
            "Calculate Body Mass Index",
            "Generate BMI interpretation"
        ],

        "appointment": [
            "Book appointment",
            "Generate appointment confirmation"
        ],

        "drug": [
            "Check drug interaction",
            "Generate medication advice"
        ],

        "symptom": [
            "Assess symptoms",
            "Generate clinical recommendation"
        ],

        "lab": [
            "Analyze laboratory report",
            "Generate laboratory findings"
        ],

        "report": [
            "Parse uploaded report",
            "Analyze extracted report",
            "Generate report summary"
        ],

        "search": [
            "Search medical knowledge",
            "Generate research summary"
        ],

        "general": [
            "Answer healthcare question"
        ]
    }

    return plans.get(intent, plans["general"])


# ==========================================================
# NODE 2
# TASK PLANNER
# ==========================================================

def planner_node(
    state: AgentState
) -> Dict[str, Any]:

    system_logger.info("Planner Node")

    # Already planned
    if state.get("plan"):
        return {
            "next_step": "reasoner"
        }

    intent = state.get(
        "intent",
        "general"
    )

    messages = state.get(
        "messages",
        []
    )

    objective = ""

    if messages:
        objective = messages[-1]["content"]

    patient_context = get_patient_profile_context(
        state.get("patient_id", 0)
    )

    llm = get_llm(
        temperature=0.2
    )

    # ------------------------------------------------------
    # LLM Planner
    # ------------------------------------------------------

    if llm:

        try:

            prompt = PromptTemplate.from_template(
                PLANNER_PROMPT
            )

            chain = prompt | llm

            result = chain.invoke(
                {
                    "patient_context": patient_context,
                    "objective": objective
                }
            )

            raw = result.content.strip()

            raw = re.sub(
                r"```json",
                "",
                raw
            )

            raw = raw.replace(
                "```",
                ""
            ).strip()

            plan = json.loads(raw)

            if isinstance(plan, list) and len(plan) > 0:

                system_logger.info(
                    f"Planner created {len(plan)} tasks."
                )

                return {

                    "plan": plan,

                    "completed_tasks": [],

                    "next_step": "reasoner"

                }

        except Exception as e:

            system_logger.warning(
                f"Planner LLM failed: {e}"
            )

    # ------------------------------------------------------
    # Rule-based Planner
    # ------------------------------------------------------

    plan = build_plan(
        intent
    )

    system_logger.info(
        f"Rule planner selected intent '{intent}'"
    )

    return {

        "plan": plan,

        "completed_tasks": [],

        "next_step": "reasoner"

    }

# ==========================================================
# HELPER
# BUILD TOOL CALL
# ==========================================================

def build_tool_call(
    intent: str,
    user_text: str,
    patient_id: int
) -> Optional[Dict[str, Any]]:

    text = user_text.lower()

    # ------------------------------------------------------
    # BMI
    # ------------------------------------------------------

    if intent == "bmi":

        weight = 70.0
        height = 170.0

        w = re.search(r"(\d+(?:\.\d+)?)\s*kg", text)
        if w:
            weight = float(w.group(1))

        h = re.search(r"(\d+(?:\.\d+)?)\s*cm", text)
        if h:
            height = float(h.group(1))

        return {

            "name": "bmi_calculator",

            "arguments": {

                "weight": weight,
                "weight_unit": "kg",
                "height": height,
                "height_unit": "cm"

            }

        }

    # ------------------------------------------------------
    # Appointment
    # ------------------------------------------------------

    if intent == "appointment":

        specialty = "General Practice"

        if "cardio" in text:
            specialty = "Cardiology"

        elif "derma" in text:
            specialty = "Dermatology"

        elif "neuro" in text:
            specialty = "Neurology"

        elif "ortho" in text:
            specialty = "Orthopedics"

        date = "2026-12-01"

        d = re.search(r"\d{4}-\d{2}-\d{2}", text)

        if d:
            date = d.group()

        return {

            "name": "appointment_scheduler",

            "arguments": {

                "patient_id": patient_id,

                "specialty": specialty,

                "appointment_date": date,

                "time_slot": "10:00 AM"

            }

        }

    # ------------------------------------------------------
    # Drug Interaction
    # ------------------------------------------------------

    if intent == "drug":

        drugs = []

        if "aspirin" in text:
            drugs.append("aspirin")

        if "warfarin" in text:
            drugs.append("warfarin")

        if "ibuprofen" in text:
            drugs.append("ibuprofen")

        if "lisinopril" in text:
            drugs.append("lisinopril")

        if "metformin" in text:
            drugs.append("metformin")

        if "contrast" in text:
            drugs.append("contrast dye")

        if len(drugs) < 2:
            drugs = [
                "aspirin",
                "warfarin"
            ]

        return {

            "name": "drug_interaction_checker",

            "arguments": {

                "drugs": drugs

            }

        }

    # ------------------------------------------------------
    # Symptoms
    # ------------------------------------------------------

    if intent == "symptom":

        symptoms = []

        if "chest pain" in text:
            symptoms.append("chest pain")

        if "fever" in text:
            symptoms.append("fever")

        if "headache" in text:
            symptoms.append("headache")

        if "cough" in text:
            symptoms.append("cough")

        if "rash" in text:
            symptoms.append("rash")

        if not symptoms:
            symptoms.append(text)

        return {

            "name": "symptom_assessment",

            "arguments": {

                "symptoms": symptoms

            }

        }

    # ------------------------------------------------------
    # Lab Report
    # ------------------------------------------------------

    if intent == "lab":

        return {

            "name": "lab_report_analyzer",

            "arguments": {

                "report_text": user_text

            }

        }

    # ------------------------------------------------------
    # Medical Report
    # ------------------------------------------------------

    if intent == "report":

        return {

            "name": "medical_report_parser",

            "arguments": {

                "file_path": "logs/mock_report.txt"

            }

        }

    # ------------------------------------------------------
    # Web Search
    # ------------------------------------------------------

    if intent == "search":

        return {

            "name": "web_search",

            "arguments": {

                "query": user_text

            }

        }

    return None


# ==========================================================
# NODE 3
# REASONER
# ==========================================================

def reasoner_node(
    state: AgentState
) -> Dict[str, Any]:

    system_logger.info("Reasoner Node")

    completed = state.get(
        "completed_tasks",
        []
    )

    plan = state.get(
        "plan",
        []
    )

    if len(completed) >= len(plan):

        return {

            "next_step": "reflector"

        }

    current_task = plan[
        len(completed)
    ]

    intent = state.get(
        "intent",
        "general"
    )

    user_text = state["messages"][-1]["content"]

    patient_id = state.get(
        "patient_id",
        0
    )

    tool_call = build_tool_call(

        intent=intent,

        user_text=user_text,

        patient_id=patient_id

    )

    # ----------------------------------------------

    if tool_call:

        system_logger.info(

            f"Selected tool {tool_call['name']}"

        )

        return {

            "current_task": current_task,

            "next_tool_call": tool_call,

            "next_step": "tool_executor"

        }

    # ----------------------------------------------

    completed.append(
        current_task
    )

    outputs = state.get(
        "tool_outputs",
        []
    )

    outputs.append({

        "task": current_task,

        "tool": None,

        "success": True,

        "outcome": "Completed without external tool."

    })

    return {

        "completed_tasks": completed,

        "tool_outputs": outputs,

        "next_step": "reasoner"

    }

# ==========================================================
# NODE 4
# TOOL EXECUTOR
# ==========================================================

def tool_executor_node(
    state: AgentState
) -> Dict[str, Any]:

    system_logger.info("Tool Executor Node")

    tool_call = state.get("next_tool_call")

    if not tool_call:

        return {
            "next_step": "reasoner"
        }

    tool_name = tool_call["name"]

    arguments = tool_call["arguments"]

    current_task = state.get(
        "current_task",
        "Unknown Task"
    )

    outputs = state.get(
        "tool_outputs",
        []
    )

    completed = state.get(
        "completed_tasks",
        []
    )

    # ----------------------------------------------------
    # Fetch Tool
    # ----------------------------------------------------

    tool = tool_registry.get_tool(tool_name)

    if tool is None:

        error = f"Tool '{tool_name}' not found."

        system_logger.error(error)

        outputs.append({

            "task": current_task,

            "tool": tool_name,

            "success": False,

            "error": error

        })

        if current_task not in completed:
            completed.append(current_task)

        return {

            "tool_outputs": outputs,

            "completed_tasks": completed,

            "next_step": "reasoner"

        }

    # ----------------------------------------------------
    # Execute Tool
    # ----------------------------------------------------

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

    # ----------------------------------------------------
    # Save Tool History
    # ----------------------------------------------------

    try:

        with get_db() as db:

            add_tool_execution(

                db=db,

                session_id=state.get(
                    "session_id",
                    "unknown"
                ),

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
                    else "failure"
                ),

                duration_ms=result.get(
                    "duration_ms",
                    0
                )

            )

    except Exception as e:

        system_logger.warning(

            f"Unable to log tool history: {e}"

        )

    # ----------------------------------------------------
    # Store Output
    # ----------------------------------------------------

    outputs.append({

        "task": current_task,

        "tool": tool_name,

        "success": result["success"],

        "data": result.get("data"),

        "error": result.get("error")

    })

    if current_task not in completed:

        completed.append(
            current_task
        )

    system_logger.info(

        f"Finished tool {tool_name}"

    )

    return {

        "tool_outputs": outputs,

        "completed_tasks": completed,

        "next_step": "reasoner"

    }

# ==========================================================
# NODE 5
# REFLECTOR
# ==========================================================

def reflector_node(
    state: AgentState
) -> Dict[str, Any]:

    system_logger.info("Reflector Node")

    plan = state.get(
        "plan",
        []
    )

    completed = state.get(
        "completed_tasks",
        []
    )

    outputs = state.get(
        "tool_outputs",
        []
    )

    # ----------------------------------------------------
    # Safety check
    # ----------------------------------------------------

    if not plan:

        system_logger.warning(
            "Planner returned an empty execution plan."
        )

        return {
            "next_step": "final_answer"
        }

    # ----------------------------------------------------
    # Determine unfinished tasks
    # ----------------------------------------------------

    remaining = [

        task

        for task in plan

        if task not in completed

    ]

    if remaining:

        system_logger.info(

            f"{len(remaining)} task(s) remaining."

        )

        return {

            "next_step": "reasoner"

        }

    # ----------------------------------------------------
    # Optional LLM Reflection
    # ----------------------------------------------------

    llm = get_llm(
        temperature=0.0
    )

    if llm:

        try:

            prompt = PromptTemplate.from_template(
                REFLECTOR_PROMPT
            )

            chain = prompt | llm

            result = chain.invoke({

                "active_plan": json.dumps(plan),

                "completed_tasks": json.dumps(completed),

                "last_tool_outputs": json.dumps(

                    outputs[-3:],

                    default=str

                )

            })

            raw = result.content.strip()

            raw = raw.replace(
                "```json",
                ""
            )

            raw = raw.replace(
                "```",
                ""
            ).strip()

            decision = json.loads(raw)

            if decision.get(
                "replan_needed",
                False
            ):

                new_plan = decision.get(
                    "new_plan",
                    []
                )

                if new_plan:

                    system_logger.info(

                        "Reflector requested replanning."

                    )

                    return {

                        "plan": new_plan,

                        "completed_tasks": [],

                        "next_step": "reasoner"

                    }

        except Exception as e:

            system_logger.warning(

                f"Reflection skipped: {e}"

            )

    # ----------------------------------------------------
    # Workflow Complete
    # ----------------------------------------------------

    system_logger.info(

        "Workflow completed successfully."

    )

    return {

        "next_step": "final_answer"

    }
# ==========================================================
# NODE 6
# FINAL ANSWER
# ==========================================================

def final_answer_node(
    state: AgentState
) -> Dict[str, Any]:

    system_logger.info("Final Answer Node")

    patient_id = state.get(
        "patient_id",
        0
    )

    session_id = state.get(
        "session_id",
        ""
    )

    intent = state.get(
        "intent",
        "general"
    )

    outputs = state.get(
        "tool_outputs",
        []
    )

    answer = ""

    # --------------------------------------------------
    # No tool executed
    # --------------------------------------------------

    if not outputs:

        answer = (
            "I couldn't identify a healthcare action to perform. "
            "Please provide more details."
        )

    else:

        latest = outputs[-1]

        success = latest.get(
            "success",
            False
        )

        data = latest.get(
            "data"
        )

        error = latest.get(
            "error"
        )

        # ----------------------------------------------
        # Tool Failed
        # ----------------------------------------------

        if not success:

            answer = f"""
### Operation Failed

Error:

{error}
"""

        # ----------------------------------------------
        # BMI
        # ----------------------------------------------

        elif intent == "bmi":

            answer = f"""
## BMI Result

**BMI:** {data['bmi']}

**Classification:** {data['classification']}

{data['details']}

---
This result is informational only.
"""

        # ----------------------------------------------
        # Drug
        # ----------------------------------------------

        elif intent == "drug":

            if data["interactions_count"] == 0:

                answer = """
## Drug Interaction Report

No significant drug interactions were found.
"""

            else:

                answer = "## Drug Interaction Report\n\n"

                for item in data["details"]:

                    answer += (
                        f"### {' + '.join(item['drugs'])}\n"
                        f"Severity: {item['severity']}\n\n"
                        f"{item['description']}\n\n"
                    )

        # ----------------------------------------------
        # Symptoms
        # ----------------------------------------------

        elif intent == "symptom":

            answer = f"""
## Symptom Assessment

Urgency Level:

**{data['urgency_level']}**

Recommended Specialists:

"""

            for s in data["recommended_specialists"]:

                answer += f"- {s}\n"

            answer += "\n### Findings\n"

            for f in data["findings"]:

                answer += (
                    f"- {f['assessment']}\n"
                )

        # ----------------------------------------------
        # Appointment
        # ----------------------------------------------

        elif intent == "appointment":

            answer = f"""
## Appointment Status

✅ {data['message']}
"""

        # ----------------------------------------------
        # Lab Report
        # ----------------------------------------------

        elif intent == "lab":

            answer = f"""
## Laboratory Report

Summary

{data['summary']}

Abnormal Findings:

{data['abnormalities_count']}

Recommendations

{data['recommendations']}
"""

        # ----------------------------------------------
        # Medical Report
        # ----------------------------------------------

        elif intent == "report":

            answer = f"""
## Medical Report Parsed

File:

{data['file_name']}

Characters Extracted:

{data['total_character_count']}

Preview
"""

        # ----------------------------------------------
        # Web Search
        # ----------------------------------------------

        elif intent == "search":

            answer = f"""
## Medical Search Results

{data['results']}
"""

        # ----------------------------------------------
        # Default
        # ----------------------------------------------

        else:

            answer = json.dumps(
                data,
                indent=2
            )

    # --------------------------------------------------
    # Store Conversation
    # --------------------------------------------------

    try:

        with get_db() as db:

            memory_manager.store_interaction(

                db=db,

                session_id=session_id,

                patient_id=patient_id,

                role="assistant",

                message=answer

            )

    except Exception as e:

        system_logger.warning(

            f"Unable to save assistant message: {e}"

        )

    # --------------------------------------------------
    # Return
    # --------------------------------------------------

    return {

        "final_output": answer,

        "next_step": "end"

    }