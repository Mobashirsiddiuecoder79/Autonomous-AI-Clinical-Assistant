from tools.registry import tool_registry
from tools.patient_tools import PatientLookupTool, PatientRegistrationTool, PatientHistoryUpdateTool
from tools.clinical_tools import BMICalculatorTool, HealthRiskCalculatorTool, DrugInteractionCheckerTool, SymptomAssessmentTool
from tools.document_tools import MedicalReportParserTool, LabReportAnalyzerTool
from tools.external_tools import WebSearchTool, AppointmentSchedulerTool, EmailNotificationTool, ReminderTool

# Instantiate and register all tools
tool_registry.register(PatientLookupTool())
tool_registry.register(PatientRegistrationTool())
tool_registry.register(PatientHistoryUpdateTool())
tool_registry.register(BMICalculatorTool())
tool_registry.register(HealthRiskCalculatorTool())
tool_registry.register(DrugInteractionCheckerTool())
tool_registry.register(SymptomAssessmentTool())
tool_registry.register(MedicalReportParserTool())
tool_registry.register(LabReportAnalyzerTool())
tool_registry.register(WebSearchTool())
tool_registry.register(AppointmentSchedulerTool())
tool_registry.register(EmailNotificationTool())
tool_registry.register(ReminderTool())
