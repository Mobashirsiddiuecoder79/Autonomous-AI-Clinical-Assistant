from typing import Dict, Any, List
from pydantic import BaseModel, Field
from tools.base import BaseHealthcareTool

# 1. BMI Calculator Tool
class BMICalculatorSchema(BaseModel):
    weight: float = Field(..., description="Weight value.")
    weight_unit: str = Field("kg", description="Unit of weight: 'kg' or 'lbs'.")
    height: float = Field(..., description="Height value.")
    height_unit: str = Field("cm", description="Unit of height: 'cm' or 'in'.")

class BMICalculatorTool(BaseHealthcareTool):
    name = "bmi_calculator"
    description = "Calculates Body Mass Index (BMI) and provides classification."
    args_schema = BMICalculatorSchema

    def execute(self, arguments: Dict[str, Any]) -> Any:
        weight = arguments["weight"]
        weight_unit = arguments["weight_unit"].lower()
        height = arguments["height"]
        height_unit = arguments["height_unit"].lower()

        # Convert to metric (kg and meters)
        if weight_unit == "lbs":
            kg = weight * 0.45359237
        else:
            kg = weight

        if height_unit == "in":
            meters = height * 0.0254
        elif height_unit == "cm":
            meters = height / 100.0
        else:
            meters = height

        if meters <= 0:
            raise ValueError("Height must be greater than zero.")

        bmi = kg / (meters ** 2)
        bmi = round(bmi, 2)

        # Classification
        if bmi < 18.5:
            classification = "Underweight"
        elif 18.5 <= bmi < 25.0:
            classification = "Normal weight"
        elif 25.0 <= bmi < 30.0:
            classification = "Overweight"
        else:
            classification = "Obese"

        return {
            "bmi": bmi,
            "classification": classification,
            "details": f"A BMI of {bmi} is classified as {classification}."
        }

# 2. Health Risk Calculator Tool
class HealthRiskSchema(BaseModel):
    age: int = Field(..., description="Age in years.")
    systolic_bp: int = Field(..., description="Systolic blood pressure (mmHg).")
    diastolic_bp: int = Field(..., description="Diastolic blood pressure (mmHg).")
    smoker: bool = Field(..., description="True if the patient is a smoker.")
    cholesterol: float = Field(..., description="Total cholesterol level (mg/dL).")

class HealthRiskCalculatorTool(BaseHealthcareTool):
    name = "health_risk_calculator"
    description = "Evaluates basic cardiovascular health risk index based on patient clinical indicators."
    args_schema = HealthRiskSchema

    def execute(self, arguments: Dict[str, Any]) -> Any:
        age = arguments["age"]
        sys_bp = arguments["systolic_bp"]
        dia_bp = arguments["diastolic_bp"]
        smoker = arguments["smoker"]
        chol = arguments["cholesterol"]

        # Simple weighted risk scoring system (mock Framingham calculation)
        score = 0
        if age > 50:
            score += 2
        if sys_bp >= 140 or dia_bp >= 90:
            score += 3  # Hypertension
        elif sys_bp >= 130 or dia_bp >= 80:
            score += 1  # Prehypertension
        if smoker:
            score += 2
        if chol >= 240:
            score += 2  # High cholesterol
        elif chol >= 200:
            score += 1  # Borderline

        if score >= 6:
            risk = "High Risk"
            recs = "High probability of cardiovascular complications. Schedule physician assessment immediately."
        elif 3 <= score < 6:
            risk = "Moderate Risk"
            recs = "Lifestyle adjustments recommended (diet, exercise). Follow up with primary physician."
        else:
            risk = "Low Risk"
            recs = "Maintain healthy habits. Routine checks as scheduled."

        return {
            "score": score,
            "cardiovascular_risk_level": risk,
            "recommendations": recs
        }

# 3. Drug Interaction Checker Tool
class DrugInteractionSchema(BaseModel):
    drugs: List[str] = Field(..., description="List of generic or brand drug names to check.")

class DrugInteractionCheckerTool(BaseHealthcareTool):
    name = "drug_interaction_checker"
    description = "Checks for potential drug-drug interactions from an internal clinical index."
    args_schema = DrugInteractionSchema

    # Internal database of common clinical interactions
    INTERACTION_DB = {
        frozenset({"aspirin", "warfarin"}): ("Contraindicated / Major", "Increases bleeding risk significantly."),
        frozenset({"ibuprofen", "lisinopril"}): ("Moderate", "Can decrease effectiveness of lisinopril and risk kidney strain."),
        frozenset({"sildenafil", "nitroglycerin"}): ("Contraindicated / Fatal", "May cause severe, life-threatening blood pressure drops."),
        frozenset({"metformin", "contrast dye"}): ("Major", "Risk of lactic acidosis. Temporarily withhold metformin before contrast imaging."),
        frozenset({"simvastatin", "amiodarone"}): ("Moderate", "Increases risk of myopathy (muscle pain/damage). Limit simvastatin dose.")
    }

    def execute(self, arguments: Dict[str, Any]) -> Any:
        drugs = [d.strip().lower() for d in arguments["drugs"]]
        interactions = []

        # Compare pairs of drugs
        for i in range(len(drugs)):
            for j in range(i + 1, len(drugs)):
                pair = frozenset({drugs[i], drugs[j]})
                if pair in self.INTERACTION_DB:
                    severity, desc = self.INTERACTION_DB[pair]
                    interactions.append({
                        "drugs": list(pair),
                        "severity": severity,
                        "description": desc
                    })

        if not interactions:
            return {"status": "No interactions found", "interactions_count": 0, "details": []}

        return {
            "status": "Interactions found",
            "interactions_count": len(interactions),
            "details": interactions
        }

# 4. Symptom Assessment Tool
class SymptomAssessmentSchema(BaseModel):
    symptoms: List[str] = Field(..., description="List of active physical symptoms.")

class SymptomAssessmentTool(BaseHealthcareTool):
    name = "symptom_assessment"
    description = "Evaluates symptom descriptions, marks emergency indicators, and lists recommended specialists."
    args_schema = SymptomAssessmentSchema

    # Map of keywords to critical alerts
    EMERGENCY_KEYWORDS = ["chest pain", "shortness of breath", "difficulty breathing", "severe chest pressure", "stroke", "numbness one side"]

    SYMPTOM_MAP = {
        "chest pain": ("Cardiology / Emergency Medicine", "CRITICAL: Potential cardiac event. Go to the nearest Emergency Room immediately."),
        "cough": ("General Practice / Pulmonology", "Common cold or mild airway congestion. Monitor temperature and stay hydrated."),
        "fever": ("General Practice / Pediatrics", "Indicates immune response. Monitor if fever exceeds 102F (38.9C) or persists > 3 days."),
        "headache": ("Neurology / General Practice", "Migraine, tension, or fatigue. Rest. If accompanied by blurred vision or numbness, seek emergency care."),
        "rash": ("Dermatology", "Allergic reaction or skin irritation. Avoid scratching, antihistamines may help."),
        "numbness": ("Neurology", "Potential nerve impingement or cardiovascular warning. Seek professional analysis.")
    }

    def execute(self, arguments: Dict[str, Any]) -> Any:
        symptoms = [s.strip().lower() for s in arguments["symptoms"]]
        is_emergency = False
        findings = []
        specialists = set()

        for symptom in symptoms:
            # Check emergency triggers
            if any(key in symptom for key in self.EMERGENCY_KEYWORDS):
                is_emergency = True
                
            # Match mapping
            matched = False
            for key, (specialist, text) in self.SYMPTOM_MAP.items():
                if key in symptom:
                    findings.append({"symptom": symptom, "assessment": text})
                    specialists.add(specialist)
                    matched = True
                    break
            
            if not matched:
                findings.append({"symptom": symptom, "assessment": "Non-specific symptom. Recommend starting with a Primary Care Physician."})
                specialists.add("General Practice / Primary Care")

        return {
            "emergency_alert": is_emergency,
            "findings": findings,
            "recommended_specialists": list(specialists),
            "urgency_level": "CRITICAL EMERGENCY" if is_emergency else "Standard Clinical Appointment"
        }
