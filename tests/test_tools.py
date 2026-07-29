import pytest
from tools.clinical_tools import BMICalculatorTool, HealthRiskCalculatorTool, DrugInteractionCheckerTool, SymptomAssessmentTool

def test_bmi_calculator():
    tool = BMICalculatorTool()
    res = tool.run(weight=70.0, weight_unit="kg", height=175.0, height_unit="cm")
    assert res["success"] is True
    assert res["data"]["bmi"] == 22.86
    assert res["data"]["classification"] == "Normal weight"

def test_health_risk_calculator():
    tool = HealthRiskCalculatorTool()
    res = tool.run(age=55, systolic_bp=145, diastolic_bp=95, smoker=True, cholesterol=250.0)
    assert res["success"] is True
    assert res["data"]["cardiovascular_risk_level"] == "High Risk"

def test_drug_interaction_checker():
    tool = DrugInteractionCheckerTool()
    res = tool.run(drugs=["aspirin", "warfarin"])
    assert res["success"] is True
    assert res["data"]["status"] == "Interactions found"
    assert res["data"]["interactions_count"] == 1
    assert "Contraindicated" in res["data"]["details"][0]["severity"]

def test_symptom_assessment_emergency():
    tool = SymptomAssessmentTool()
    res = tool.run(symptoms=["Severe chest pain and difficulty breathing"])
    assert res["success"] is True
    assert res["data"]["emergency_alert"] is True
    assert res["data"]["urgency_level"] == "CRITICAL EMERGENCY"
    assert "Cardiology / Emergency Medicine" in res["data"]["recommended_specialists"]
