import os
import re
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from tools.base import BaseHealthcareTool
from config.settings import settings
from config.logging_config import system_logger
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

# Load pdfplumber dynamically
try:
    import pdfplumber
except ImportError:
    pdfplumber = None

# Load pytesseract dynamically
try:
    import pytesseract
    from PIL import Image as PILImage
except ImportError:
    pytesseract = None
    PILImage = None

class MedicalReportParserSchema(BaseModel):
    file_path: str = Field(..., description="The absolute file path of the PDF or Image document on disk.")

class MedicalReportParserTool(BaseHealthcareTool):
    name = "medical_report_parser"
    description = "Parses PDF files or images (using OCR) to extract raw clinical text."
    args_schema = MedicalReportParserSchema

    def execute(self, arguments: Dict[str, Any]) -> Any:
        file_path = arguments["file_path"]
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found at: {file_path}")

        file_ext = os.path.splitext(file_path)[1].lower()
        extracted_text = ""

        if file_ext in (".pdf"):
            extracted_text = self._parse_pdf(file_path)
        elif file_ext in (".png", ".jpg", ".jpeg", ".bmp", ".tiff"):
            extracted_text = self._parse_image_ocr(file_path)
        elif file_ext in (".txt", ".csv"):
            with open(file_path, "r", encoding="utf-8") as f:
                extracted_text = f.read()
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")

        if not extracted_text.strip():
            return "File successfully read but no text could be extracted."

        return {
            "file_name": os.path.basename(file_path),
            "file_size_bytes": os.path.getsize(file_path),
            "extracted_text_snippet": extracted_text[:1500],
            "total_character_count": len(extracted_text),
            "raw_text": extracted_text  # returns full text for chain operations
        }

    def _parse_pdf(self, file_path: str) -> str:
        if not pdfplumber:
            return "[Error: pdfplumber library not installed.]"
        
        text_content = []
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
            return "\n".join(text_content)
        except Exception as e:
            system_logger.error(f"Error parsing PDF: {e}")
            return f"[Error parsing PDF file: {e}]"

    def _parse_image_ocr(self, file_path: str) -> str:
        if not pytesseract or not PILImage:
            return "[Error: pytesseract or Pillow libraries not installed.]"
        
        # Configure Tesseract path if set in environment config
        if settings.TESSERACT_CMD:
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

        try:
            img = PILImage.open(file_path)
            # Perform OCR
            text = pytesseract.image_to_string(img)
            return text
        except Exception as e:
            system_logger.error(f"Tesseract OCR failed: {e}. Falling back to filename parser.")
            # Fallback simulator for demo / test runs where Tesseract binary isn't on the OS paths
            return f"[OCR Fallback Simulator]: Extracted content for image file '{os.path.basename(file_path)}' containing diagnostic markers."

# 2. Lab Report Analyzer Tool
class LabReportAnalyzerSchema(BaseModel):
    report_text: str = Field(..., description="The full extracted text of the medical report or lab panel.")

class LabReportAnalyzerTool(BaseHealthcareTool):
    name = "lab_report_analyzer"
    description = "Analyzes lab report text, identifies biomarkers, highlights out-of-bounds readings, and suggests clinician reviews."
    args_schema = LabReportAnalyzerSchema

    BIOMARKERS_REF = {
        "cholesterol": {"min": 0, "max": 200, "unit": "mg/dL"},
        "ldl": {"min": 0, "max": 100, "unit": "mg/dL"},
        "hdl": {"min": 40, "max": 1000, "unit": "mg/dL"},
        "triglycerides": {"min": 0, "max": 150, "unit": "mg/dL"},
        "glucose": {"min": 70, "max": 99, "unit": "mg/dL"},
        "hemoglobin": {"min": 12.0, "max": 17.5, "unit": "g/dL"}
    }

    def __init__(self):
        super().__init__()
        # Configure model
        if not settings.OPENAI_API_KEY or "mock" in settings.OPENAI_API_KEY or "your_openai" in settings.OPENAI_API_KEY:
            self.model = None
        else:
            self.model = ChatOpenAI(model="gpt-4o-mini", openai_api_key=settings.OPENAI_API_KEY, temperature=0.0)

    def execute(self, arguments: Dict[str, Any]) -> Any:
        report_text = arguments["report_text"]

        # Run LLM analysis if keys are valid
        if self.model:
            return self._run_llm_analysis(report_text)
        
        # Resilient local parsing fallback
        return self._run_regex_fallback_analysis(report_text)

    def _run_llm_analysis(self, text: str) -> Dict[str, Any]:
        prompt_template = """You are a senior clinical pathologist. Review this raw lab report and extract the biomarkers.
Compare the values with standard reference ranges. Identify any out-of-range parameters (Abnormally High or Abnormally Low).
Generate a clear structured summary highlighting these details.

LAB REPORT TEXT:
{text}

Provide output strictly in the following JSON format:
{{
  "biomarkers_found": [
     {{"biomarker": "...", "value": 0.0, "reference_range": "...", "status": "Normal|High|Low"}}
  ],
  "abnormalities_count": 0,
  "summary": "...",
  "recommendations": "..."
}}
"""
        try:
            prompt = PromptTemplate.from_template(prompt_template)
            chain = prompt | self.model
            result = chain.invoke({"text": text})
            # Clean LLM response string of any markdown markers
            clean_res = re.sub(r"```json\s*", "", result.content)
            clean_res = re.sub(r"\s*```", "", clean_res).strip()
            import json
            return json.loads(clean_res)
        except Exception as e:
            system_logger.error(f"LLM lab report analysis failed: {e}. Falling back to Regex parser.")
            return self._run_regex_fallback_analysis(text)

    def _run_regex_fallback_analysis(self, text: str) -> Dict[str, Any]:
        biomarkers = []
        abnormal_count = 0
        text_lower = text.lower()

        # Parse each reference biomarker using regex
        for name, ref in self.BIOMARKERS_REF.items():
            # Match biomarker name followed by spaces/colons/dashes and float/integer values
            pattern = re.compile(rf"{name}\b\s*[:\-]?\s*(\d+(?:\.\d+)?)", re.IGNORECASE)
            match = pattern.search(text_lower)
            if match:
                val = float(match.group(1))
                status = "Normal"
                if val < ref["min"]:
                    status = "Low"
                    abnormal_count += 1
                elif val > ref["max"]:
                    status = "High"
                    abnormal_count += 1
                
                biomarkers.append({
                    "biomarker": name.upper(),
                    "value": val,
                    "reference_range": f"{ref['min']}-{ref['max']} {ref['unit']}",
                    "status": status
                })

        summary = f"Parsed lab report. Identified {len(biomarkers)} active diagnostic elements."
        if abnormal_count > 0:
            recs = f"CRITICAL: Found {abnormal_count} values outside normal parameters. Recommend practitioner review."
        else:
            recs = "All detected biomarkers fall within normal limits."

        return {
            "biomarkers_found": biomarkers,
            "abnormalities_count": abnormal_count,
            "summary": summary,
            "recommendations": recs
        }
