import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from tools.base import BaseHealthcareTool
from config.logging_config import system_logger
from security.audit import log_security_event

# Ensure logs folder exists
os.makedirs("logs", exist_ok=True)

# Helper to save json data to files
def append_to_json_file(file_path: str, data: dict):
    records = []
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                records = json.load(f)
        except Exception:
            records = []
    records.append(data)
    with open(file_path, "w") as f:
        json.dump(records, f, indent=4)

# 1. Web Search Tool
class WebSearchSchema(BaseModel):
    query: str = Field(..., description="The query to search the medical web indexing for.")

class WebSearchTool(BaseHealthcareTool):
    name = "web_search"
    description = "Searches the web for clinical research, drug descriptions, or hospital services."
    args_schema = WebSearchSchema

    def execute(self, arguments: Dict[str, Any]) -> Any:
        query = arguments["query"].lower()
        system_logger.info(f"Running web search for: '{query}'")

        # Try DuckDuckGoSearch if internet is available and library works
        try:
            from langchain_community.tools import DuckDuckGoSearchRun
            search = DuckDuckGoSearchRun()
            res = search.run(query)
            return {"results": res, "source": "DuckDuckGo"}
        except Exception as e:
            system_logger.info(f"DuckDuckGoSearch failed: {e}. Falling back to internal medical index.")

        # Local mock index of common medical searches
        mock_web_index = {
            "lipid panel": "A lipid panel measures cholesterol levels: LDL, HDL, Triglycerides. Normal: LDL < 100, HDL > 40, Total < 200.",
            "hypertension": "Hypertension is defined as BP >= 130/80 mmHg. Lifestyle shifts, reduced salt, and ACE inhibitors (Lisinopril) are common treatments.",
            "cardiology": "Cardiology specializes in heart health. Consult a cardiologist for chest tightness, high risk, or family history of heart disease.",
            "metformin": "Metformin is a first-line medication for type 2 diabetes. It improves insulin sensitivity. Major side effect: GI distress.",
            "simvastatin": "Simvastatin is a statin medication used to lower cholesterol. Side effects include myopathy; contraindicated with strong CYP3A4 inhibitors."
        }

        # Check keyword matches
        matches = []
        for key, value in mock_web_index.items():
            if key in query:
                matches.append(value)
        
        if not matches:
            matches.append(f"Search results for '{query}': Found recent articles outlining diagnostic protocols and patient management studies.")

        return {
            "results": "\n".join(matches),
            "source": "Healthcare Mock Web Index"
        }

# 2. Appointment Scheduler Tool
class AppointmentSchedulerSchema(BaseModel):
    patient_id: int = Field(..., description="ID of the patient booking the appointment.")
    specialty: str = Field(..., description="Specialty of doctor (e.g., Cardiology, General Practice).")
    appointment_date: str = Field(..., description="Requested date in YYYY-MM-DD format.")
    time_slot: str = Field(..., description="Requested time (e.g. 10:00 AM, 2:30 PM).")

class AppointmentSchedulerTool(BaseHealthcareTool):
    name = "appointment_scheduler"
    description = "Books clinical appointments and logs them in the calendar system."
    args_schema = AppointmentSchedulerSchema

    def execute(self, arguments: Dict[str, Any]) -> Any:
        appt = {
            "patient_id": arguments["patient_id"],
            "specialty": arguments["specialty"],
            "date": arguments["appointment_date"],
            "time": arguments["time_slot"],
            "created_at": datetime.utcnow().isoformat()
        }

        # Save to local calendar file
        append_to_json_file("logs/appointments.json", appt)

        log_security_event(
            action="SCHEDULE_APPOINTMENT",
            performed_by="agent",
            change_summary=f"Booked {arguments['specialty']} appointment on {arguments['appointment_date']} at {arguments['time_slot']}",
            record_id=arguments["patient_id"],
            table="patients"
        )

        return {
            "status": "success",
            "message": f"Appointment booked successfully with {arguments['specialty']} on {arguments['appointment_date']} at {arguments['time_slot']}."
        }

# 3. Notification & Email Tool
class EmailNotificationSchema(BaseModel):
    recipient_email: str = Field(..., description="Recipient email address.")
    subject: str = Field(..., description="Subject of the email.")
    body: str = Field(..., description="Body of the email message.")

class EmailNotificationTool(BaseHealthcareTool):
    name = "email_notification"
    description = "Sends emails notifications to patients or practitioners."
    args_schema = EmailNotificationSchema

    def execute(self, arguments: Dict[str, Any]) -> Any:
        log_entry = (
            f"--- EMAIL SENT ---\n"
            f"Date: {datetime.utcnow().isoformat()}\n"
            f"To: {arguments['recipient_email']}\n"
            f"Subject: {arguments['subject']}\n"
            f"Body:\n{arguments['body']}\n"
            f"------------------\n\n"
        )
        # Write to emails log
        with open("logs/emails.txt", "a") as f:
            f.write(log_entry)

        log_security_event(
            action="SEND_EMAIL",
            performed_by="agent",
            change_summary=f"Sent email to {arguments['recipient_email']} with subject: '{arguments['subject']}'"
        )

        return {
            "status": "success",
            "message": f"Email successfully dispatched to {arguments['recipient_email']}."
        }

# 4. Reminder Tool
class ReminderSchema(BaseModel):
    patient_id: int = Field(..., description="ID of the patient the reminder is for.")
    reminder_text: str = Field(..., description="Description of the reminder (e.g. take Metformin).")
    due_time: str = Field(..., description="When the reminder is due (e.g. Daily at 8:00 AM, 2026-10-12).")

class ReminderTool(BaseHealthcareTool):
    name = "reminder_scheduler"
    description = "Schedules patient reminders (medication dosage, checkups)."
    args_schema = ReminderSchema

    def execute(self, arguments: Dict[str, Any]) -> Any:
        reminder = {
            "patient_id": arguments["patient_id"],
            "reminder_text": arguments["reminder_text"],
            "due_time": arguments["due_time"],
            "status": "Active",
            "created_at": datetime.utcnow().isoformat()
        }

        append_to_json_file("logs/reminders.json", reminder)

        return {
            "status": "success",
            "message": f"Reminder scheduled: '{arguments['reminder_text']}' at {arguments['due_time']}."
        }
