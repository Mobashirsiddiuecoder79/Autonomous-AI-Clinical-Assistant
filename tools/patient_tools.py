from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from tools.base import BaseHealthcareTool
from database.connection import get_db
from database.operations import get_patient, create_patient, list_patients, update_patient_history

# 1. Patient Lookup Tool
class PatientLookupSchema(BaseModel):
    patient_id: Optional[int] = Field(None, description="The unique integer ID of the patient.")
    email: Optional[str] = Field(None, description="The email address of the patient.")
    name_query: Optional[str] = Field(None, description="Part of the patient's first or last name.")

class PatientLookupTool(BaseHealthcareTool):
    name = "patient_lookup"
    description = "Searches the database for patient demographic and profile information by ID, email, or name."
    args_schema = PatientLookupSchema

    def execute(self, arguments: Dict[str, Any]) -> Any:
        patient_id = arguments.get("patient_id")
        email = arguments.get("email")
        name_query = arguments.get("name_query")

        with get_db() as db:
            if patient_id:
                p = get_patient(db, patient_id)
                patients = [p] if p else []
            else:
                all_patients = list_patients(db)
                patients = all_patients
                if email:
                    patients = [p for p in patients if email.lower() in p.email.lower()]
                if name_query:
                    q = name_query.lower()
                    patients = [p for p in patients if q in p.first_name.lower() or q in p.last_name.lower()]

            if not patients:
                return "No patients matched the query criteria."

            res = []
            for p in patients:
                res.append({
                    "id": p.id,
                    "name": f"{p.first_name} {p.last_name}",
                    "email": p.email,
                    "date_of_birth": p.date_of_birth.strftime("%Y-%m-%d"),
                    "gender": p.gender,
                    "medical_history": p.medical_history or "None recorded"
                })
            return res

# 2. Patient Registration Tool
class PatientRegistrationSchema(BaseModel):
    first_name: str = Field(..., description="First name of the patient.")
    last_name: str = Field(..., description="Last name of the patient.")
    email: str = Field(..., description="Unique email address.")
    date_of_birth: str = Field(..., description="Birth date in YYYY-MM-DD format.")
    gender: str = Field(..., description="Gender (e.g. Male, Female, Other).")
    ssn: Optional[str] = Field(None, description="Social security number (optional, will be stored encrypted).")
    medical_history: Optional[str] = Field(None, description="Baseline medical conditions or notes.")

class PatientRegistrationTool(BaseHealthcareTool):
    name = "patient_registration"
    description = "Registers a new patient in the relational database catalog."
    args_schema = PatientRegistrationSchema

    def execute(self, arguments: Dict[str, Any]) -> Any:
        with get_db() as db:
            # Check duplicate email
            all_p = list_patients(db)
            if any(p.email.lower() == arguments["email"].lower() for p in all_p):
                raise ValueError(f"Patient with email {arguments['email']} already exists.")

            patient = create_patient(
                db=db,
                first_name=arguments["first_name"],
                last_name=arguments["last_name"],
                email=arguments["email"],
                date_of_birth=arguments["date_of_birth"],
                gender=arguments["gender"],
                ssn=arguments.get("ssn"),
                medical_history=arguments.get("medical_history"),
                operator="agent"
            )
            return {
                "message": "Patient registered successfully.",
                "patient_id": patient.id,
                "email": patient.email
            }

# 3. Patient History Update Tool
class PatientHistoryUpdateSchema(BaseModel):
    patient_id: int = Field(..., description="Integer ID of the patient to update.")
    medical_history: str = Field(..., description="The complete, updated baseline medical history string.")

class PatientHistoryUpdateTool(BaseHealthcareTool):
    name = "patient_history_update"
    description = "Updates the baseline clinical profile history of a registered patient."
    args_schema = PatientHistoryUpdateSchema

    def execute(self, arguments: Dict[str, Any]) -> Any:
        patient_id = arguments["patient_id"]
        history = arguments["medical_history"]

        with get_db() as db:
            patient = update_patient_history(db, patient_id, history, operator="agent")
            if not patient:
                raise ValueError(f"Patient with ID {patient_id} not found.")
            return f"Medical history updated successfully for Patient ID {patient_id}."
