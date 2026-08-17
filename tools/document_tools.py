import os
import re
import json
import base64
from typing import Dict, Any, Optional

from pydantic import BaseModel, Field

from tools.base import BaseHealthcareTool
from config.settings import settings
from config.logging_config import system_logger

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage


# ==========================================================
# OPTIONAL PDF SUPPORT
# ==========================================================

try:
    import pdfplumber
except ImportError:
    pdfplumber = None


# ==========================================================
# OPTIONAL TESSERACT OCR SUPPORT
# ==========================================================

try:
    import pytesseract
    from PIL import Image as PILImage
except ImportError:
    pytesseract = None
    PILImage = None


# ==========================================================
# MEDICAL REPORT PARSER
# ==========================================================

class MedicalReportParserSchema(BaseModel):

    file_path: str = Field(
        ...,
        description="The absolute file path of the PDF or Image document on disk."
    )


class MedicalReportParserTool(BaseHealthcareTool):

    name = "medical_report_parser"

    description = (
        "Parses PDF files, text files, or medical report images. "
        "Images are processed with Tesseract OCR when available and "
        "OpenAI Vision when Tesseract is unavailable."
    )

    args_schema = MedicalReportParserSchema

    # ------------------------------------------------------
    # MAIN EXECUTION
    # ------------------------------------------------------

    def execute(self, arguments: Dict[str, Any]) -> Any:

        file_path = arguments["file_path"]

        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"File not found at: {file_path}"
            )

        file_ext = os.path.splitext(file_path)[1].lower()

        extracted_text = ""

        # --------------------------------------------------
        # PDF
        # --------------------------------------------------

        if file_ext == ".pdf":

            extracted_text = self._parse_pdf(
                file_path
            )

        # --------------------------------------------------
        # IMAGE
        # --------------------------------------------------

        elif file_ext in (
            ".png",
            ".jpg",
            ".jpeg",
            ".bmp",
            ".tiff",
            ".webp"
        ):

            extracted_text = self._parse_image_ocr(
                file_path
            )

        # --------------------------------------------------
        # TEXT
        # --------------------------------------------------

        elif file_ext in (
            ".txt",
            ".csv"
        ):

            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as f:

                extracted_text = f.read()

        else:

            raise ValueError(
                f"Unsupported file format: {file_ext}"
            )

        # --------------------------------------------------
        # VALIDATE EXTRACTION
        # --------------------------------------------------

        if not extracted_text.strip():

            return {
                "file_name": os.path.basename(file_path),
                "file_size_bytes": os.path.getsize(file_path),
                "extracted_text_snippet": "",
                "total_character_count": 0,
                "raw_text": ""
            }

        return {

            "file_name":
                os.path.basename(file_path),

            "file_size_bytes":
                os.path.getsize(file_path),

            "extracted_text_snippet":
                extracted_text[:1500],

            "total_character_count":
                len(extracted_text),

            "raw_text":
                extracted_text
        }

    # ======================================================
    # PDF PARSER
    # ======================================================

    def _parse_pdf(
        self,
        file_path: str
    ) -> str:

        if not pdfplumber:

            return (
                "[Error: pdfplumber library not installed.]"
            )

        text_content = []

        try:

            with pdfplumber.open(file_path) as pdf:

                for page in pdf.pages:

                    text = page.extract_text()

                    if text:

                        text_content.append(
                            text
                        )

            return "\n".join(
                text_content
            )

        except Exception as e:

            system_logger.error(
                f"Error parsing PDF: {e}"
            )

            return (
                f"[Error parsing PDF file: {e}]"
            )

    # ======================================================
    # IMAGE PARSER
    # ======================================================

    def _parse_image_ocr(
        self,
        file_path: str
    ) -> str:

        # --------------------------------------------------
        # FIRST: TRY LOCAL TESSERACT
        # --------------------------------------------------

        if pytesseract and PILImage:

            try:

                if settings.TESSERACT_CMD:

                    pytesseract.pytesseract.tesseract_cmd = (
                        settings.TESSERACT_CMD
                    )

                img = PILImage.open(
                    file_path
                )

                text = pytesseract.image_to_string(
                    img
                )

                if text and text.strip():

                    system_logger.info(
                        "Medical image successfully processed using Tesseract OCR."
                    )

                    return text

            except Exception as e:

                system_logger.warning(
                    f"Tesseract OCR unavailable or failed: {e}"
                )

        # --------------------------------------------------
        # SECOND: OPENAI VISION FALLBACK
        # --------------------------------------------------

        try:

            vision_text = self._parse_image_with_openai_vision(
                file_path
            )

            if vision_text and vision_text.strip():

                system_logger.info(
                    "Medical image successfully processed using OpenAI Vision."
                )

                return vision_text

        except Exception as e:

            system_logger.error(
                f"OpenAI Vision image extraction failed: {e}"
            )

        # --------------------------------------------------
        # LAST RESORT
        # --------------------------------------------------

        return (
            "[OCR unavailable] "
            "The uploaded image could not be read. "
            "Please configure Tesseract OCR or a valid OpenAI API key."
        )

    # ======================================================
    # OPENAI VISION IMAGE EXTRACTION
    # ======================================================

    def _parse_image_with_openai_vision(
        self,
        file_path: str
    ) -> str:

        api_key = getattr(
            settings,
            "OPENAI_API_KEY",
            None
        )

        if not api_key:

            raise RuntimeError(
                "OPENAI_API_KEY is not configured."
            )

        if (
            "mock" in str(api_key).lower()
            or "your_openai" in str(api_key).lower()
        ):

            raise RuntimeError(
                "A valid OpenAI API key is required for image analysis."
            )

        # --------------------------------------------------
        # READ IMAGE
        # --------------------------------------------------

        with open(
            file_path,
            "rb"
        ) as image_file:

            image_bytes = image_file.read()

        encoded_image = base64.b64encode(
            image_bytes
        ).decode("utf-8")

        extension = (
            os.path.splitext(file_path)[1]
            .lower()
        )

        mime_types = {

            ".png": "image/png",

            ".jpg": "image/jpeg",

            ".jpeg": "image/jpeg",

            ".bmp": "image/bmp",

            ".tiff": "image/tiff",

            ".webp": "image/webp"
        }

        mime_type = mime_types.get(
            extension,
            "image/jpeg"
        )

        image_data_url = (
            f"data:{mime_type};base64,{encoded_image}"
        )

        # --------------------------------------------------
        # VISION MODEL
        # --------------------------------------------------

        model = ChatOpenAI(

            model="gpt-4o-mini",

            openai_api_key=api_key,

            temperature=0
        )

        # --------------------------------------------------
        # MEDICAL REPORT EXTRACTION PROMPT
        # --------------------------------------------------

        prompt = """
You are extracting text from a medical laboratory report image.

Read the uploaded image carefully.

Extract the actual visible medical information from the report.

Focus especially on:

- Patient name if visible
- Test names
- Biomarker names
- Measured values
- Units
- Reference ranges
- High / Low indicators
- Hemoglobin
- Glucose
- Cholesterol
- LDL
- HDL
- Triglycerides
- Blood pressure
- HbA1c
- Creatinine
- Urea
- WBC
- RBC
- Platelets
- Other laboratory parameters

Do NOT invent values.

Do NOT diagnose the patient.

Do NOT assume missing information.

Return the extracted report as clean plain text.

Preserve the numerical values and units exactly as visible.

If a value is unclear, write [UNCLEAR] rather than guessing.

The output will be passed to another laboratory-analysis component.
"""

        message = HumanMessage(
            content=[

                {
                    "type": "text",
                    "text": prompt
                },

                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_data_url
                    }
                }
            ]
        )

        response = model.invoke(
            [message]
        )

        # --------------------------------------------------
        # EXTRACT RESPONSE TEXT
        # --------------------------------------------------

        content = response.content

        if isinstance(
            content,
            str
        ):

            return content.strip()

        if isinstance(
            content,
            list
        ):

            parts = []

            for item in content:

                if isinstance(
                    item,
                    dict
                ):

                    text = item.get(
                        "text"
                    )

                    if text:

                        parts.append(
                            text
                        )

            return "\n".join(
                parts
            ).strip()

        return str(
            content
        ).strip()


# ==========================================================
# LAB REPORT ANALYZER
# ==========================================================

class LabReportAnalyzerSchema(BaseModel):

    report_text: str = Field(
        ...,
        description=(
            "The full extracted text of the medical report "
            "or laboratory panel."
        )
    )


class LabReportAnalyzerTool(BaseHealthcareTool):

    name = "lab_report_analyzer"
    args_schema = LabReportAnalyzerSchema

    description = (
        "Analyzes laboratory report text, identifies biomarkers, "
        "detects abnormal readings, and provides clinical review guidance."
    )

    BIOMARKERS_REF = {
        "cholesterol": {
            "min": 0,
            "max": 200,
            "unit": "mg/dL"
        },
        "ldl": {
            "min": 0,
            "max": 130,
            "unit": "mg/dL"
        },
        "hdl": {
            "min": 40,
            "max": 1000,
            "unit": "mg/dL"
        },
        "triglycerides": {
            "min": 0,
            "max": 150,
            "unit": "mg/dL"
        },
        "glucose": {
            "min": 70,
            "max": 99,
            "unit": "mg/dL"
        },
        "hemoglobin": {
            "min": 12.0,
            "max": 17.5,
            "unit": "g/dL"
        },

        "wbc": {
            "min": 4000,
            "max": 11000,
            "unit": "cells/mcL"
        },

        "platelets": {
            "min": 1.50,
            "max": 4.50,
            "unit": "lakh/uL"
        },

        "creatinine": {
            "min": 0.70,
            "max": 4.30,
            "unit": "mg/dL"
        },

        "uric_acid": {
            "min": 3.5,
            "max": 7.2,
            "unit": "mg/dL"
        },

        "alt": {
            "min": 0,
            "max": 41,
            "unit": "U/L"
        },

        "ast": {
            "min": 0,
            "max": 40,
            "unit": "U/L"
        }
    }

    def __init__(self):

        super().__init__()

        if (
            not settings.OPENAI_API_KEY
            or "mock" in settings.OPENAI_API_KEY.lower()
            or "your_openai" in settings.OPENAI_API_KEY.lower()
        ):
            self.model = None

        else:
            self.model = ChatOpenAI(
                model="gpt-4o-mini",
                openai_api_key=settings.OPENAI_API_KEY,
                temperature=0.0
            )

    # ======================================================
    # ANALYZER EXECUTION
    # ======================================================

    def execute(
        self,
        arguments: Dict[str, Any]
    ) -> Any:

        report_text = arguments.get(
            "report_text",
            ""
        )

        if (
            not report_text
            or not report_text.strip()
            or report_text.lower().startswith("[ocr unavailable]")
        ):

            return {
                "biomarkers_found": [],
                "abnormalities_count": 0,
                "summary": "The report could not be read successfully.",
                "recommendations": (
                    "Please upload a clearer medical report image "
                    "or configure a valid OCR/Vision provider."
                )
            }

        # --------------------------------------------------
        # Try LLM analysis first when a valid API key exists
        # --------------------------------------------------

        if self.model:

            result = self._run_llm_analysis(
                report_text
            )

            if result and result.get("biomarkers_found"):
                return result

        # --------------------------------------------------
        # Robust OCR-aware local parser
        # --------------------------------------------------

        return self._run_regex_fallback_analysis(
            report_text
        )

    # ======================================================
    # LLM ANALYSIS
    # ======================================================

    def _run_llm_analysis(
        self,
        text: str
    ) -> Optional[Dict[str, Any]]:

        prompt_template = """
You are a clinical laboratory report extraction system.

Read the OCR text below and extract laboratory biomarkers.

Important:
- OCR may contain broken spaces, pipes, brackets, or spelling mistakes.
- "LOL Cholesterol" may actually mean "LDL Cholesterol".
- "Hb" means Hemoglobin.
- "Fasting Blood Sugar" means Glucose.
- Preserve the reference range shown in the report whenever available.
- Do not invent biomarkers that are not present.
- Do not diagnose the patient.

Return ONLY valid JSON:

{
  "biomarkers_found": [
    {
      "biomarker": "Hemoglobin",
      "value": 13.6,
      "reference_range": "13.0-17.0 g/dL",
      "status": "Normal"
    }
  ],
  "abnormalities_count": 0,
  "summary": "Short factual laboratory summary.",
  "recommendations": "Short clinical review recommendation."
}

LAB REPORT:
{text}
"""

        try:

            prompt = PromptTemplate.from_template(
                prompt_template
            )

            chain = prompt | self.model

            result = chain.invoke(
                {
                    "text": text
                }
            )

            content = result.content

            if not isinstance(content, str):
                content = str(content)

            clean_res = re.sub(
                r"```json\s*",
                "",
                content,
                flags=re.IGNORECASE
            )

            clean_res = re.sub(
                r"\s*```",
                "",
                clean_res
            ).strip()

            import json

            data = json.loads(
                clean_res
            )

            if not isinstance(data, dict):
                return None

            return data

        except Exception as e:

            system_logger.error(
                f"LLM lab report analysis failed: {e}. "
                "Using OCR-aware local parser."
            )

            return None

    # ======================================================
    # OCR-AWARE LOCAL ANALYZER
    # ======================================================

    def _run_regex_fallback_analysis(
        self,
        text: str
    ) -> Dict[str, Any]:

        original_text = text

        # ----------------------------------------------
        # Normalize OCR text
        # ----------------------------------------------

        normalized = text.replace(
            "\r",
            "\n"
        )

        normalized = normalized.replace(
            "\u201c",
            '"'
        ).replace(
            "\u201d",
            '"'
        )

        normalized = normalized.replace(
            "\u2013",
            "-"
        ).replace(
            "\u2014",
            "-"
        )

        normalized_lower = normalized.lower()

        # OCR commonly confuses these characters.
        normalized_lower = re.sub(
            r"\blol\b",
            "ldl",
            normalized_lower
        )

        normalized_lower = re.sub(
            r"\bldl\b",
            "ldl",
            normalized_lower
        )

        normalized_lower = re.sub(
            r"\bhb\b",
            "hemoglobin",
            normalized_lower
        )

        # Make OCR table separators easier to search.
        searchable = re.sub(
            r"[|¦]+",
            " ",
            normalized_lower
        )

        searchable = re.sub(
            r"\s+",
            " ",
            searchable
        )

        biomarkers = []

        # ==================================================
        # HELPER FUNCTIONS
        # ==================================================

        def add_biomarker(
            name,
            value,
            reference_range,
            unit,
            status
        ):

            biomarkers.append(
                {
                    "biomarker": name,
                    "value": value,
                    "reference_range": reference_range,
                    "status": status
                }
            )

        def status_from_value(
            value,
            minimum,
            maximum
        ):

            if value < minimum:
                return "Low"

            if value > maximum:
                return "High"

            return "Normal"

        def extract_range(
            source,
            start_position,
            default_min,
            default_max,
            unit
        ):
            # Look only at the text immediately following the value.
            # OCR tables often contain several later reference ranges,
            # so a large search window can accidentally select another
            # biomarker's range.

            section = source[
                start_position:start_position + 90
            ]

            # --------------------------------------------------
            # PRIORITY 1: inequality references
            # Examples:
            #   <200
            #   >40
            #   <130
            #   <150
            # --------------------------------------------------

            less_than = re.search(
                r"<\s*(\d+(?:\.\d+)?)",
                section
            )

            if less_than:

                maximum = float(
                    less_than.group(1)
                )

                maximum_text = (
                    str(int(maximum))
                    if maximum.is_integer()
                    else str(maximum)
                )

                return (
                    default_min,
                    maximum,
                    f"<{maximum_text} {unit}"
                )

            greater_than = re.search(
                r">\s*(\d+(?:\.\d+)?)",
                section
            )

            if greater_than:

                minimum = float(
                    greater_than.group(1)
                )

                minimum_text = (
                    str(int(minimum))
                    if minimum.is_integer()
                    else str(minimum)
                )

                return (
                    minimum,
                    default_max,
                    f">{minimum_text} {unit}"
                )

            # --------------------------------------------------
            # PRIORITY 2: explicit numeric range
            # Examples:
            #   13.0 - 17.0
            #   70-99
            #   0.70-4.30
            # --------------------------------------------------

            range_match = re.search(
                r"(\d[\d,]*(?:\.\d+)?)\s*[-–]\s*(\d[\d,]*(?:\.\d+)?)",
                section
            )

            if range_match:

                minimum = float(
                    range_match.group(1).replace(",", "")
                )

                maximum = float(
                    range_match.group(2).replace(",", "")
                )

                minimum_text = (
                    str(int(minimum))
                    if minimum.is_integer()
                    else str(minimum)
                )

                maximum_text = (
                    str(int(maximum))
                    if maximum.is_integer()
                    else str(maximum)
                )

                return (
                    minimum,
                    maximum,
                    f"{minimum_text}-{maximum_text} {unit}"
                )

            # --------------------------------------------------
            # PRIORITY 3: configured fallback
            # --------------------------------------------------

            minimum_text = (
                str(int(default_min))
                if float(default_min).is_integer()
                else str(default_min)
            )

            maximum_text = (
                str(int(default_max))
                if float(default_max).is_integer()
                else str(default_max)
            )

            return (
                default_min,
                default_max,
                f"{minimum_text}-{maximum_text} {unit}"
            )

        def find_value_after(
            patterns
        ):

            for pattern in patterns:

                match = re.search(
                    pattern,
                    searchable,
                    re.IGNORECASE
                )

                if match:

                    try:
                        return (
                            float(match.group(1)),
                            match.start(),
                            match.end()
                        )
                    except Exception:
                        pass

            return None, None, None

        # ==================================================
        # HEMOGLOBIN
        # ==================================================

        value, position, value_end = find_value_after(
            [
                r"\bhemoglobin\b(?:\s*\(?.*?\)?)?"
                r"\s*(?:[:\-]|\s)+"
                r"(\d+(?:\.\d+)?)",

                r"\bhemoglobin\b\s+"
                r"(\d+(?:\.\d+)?)"
            ]
        )

        if value is not None:

            ref = self.BIOMARKERS_REF[
                "hemoglobin"
            ]

            minimum, maximum, reference = extract_range(
                searchable,
                value_end,
                ref["min"],
                ref["max"],
                ref["unit"]
            )

            status = status_from_value(
                value,
                minimum,
                maximum
            )

            add_biomarker(
                "Hemoglobin",
                value,
                reference,
                ref["unit"],
                status
            )

        # ==================================================
        # FASTING BLOOD SUGAR / GLUCOSE
        # ==================================================

        value, position, value_end = find_value_after(
            [
                r"fasting\s+blood\s+sugar"
                r"[^0-9]{0,20}"
                r"(\d+(?:\.\d+)?)",

                r"\bglucose\b"
                r"[^0-9]{0,20}"
                r"(\d+(?:\.\d+)?)"
            ]
        )

        if value is not None:

            ref = self.BIOMARKERS_REF[
                "glucose"
            ]

            minimum, maximum, reference = extract_range(
                searchable,
                value_end,
                ref["min"],
                ref["max"],
                ref["unit"]
            )

            status = status_from_value(
                value,
                minimum,
                maximum
            )

            add_biomarker(
                "Fasting Blood Sugar",
                value,
                reference,
                ref["unit"],
                status
            )

        # ==================================================
        # TOTAL CHOLESTEROL
        # ==================================================

        value, position, value_end = find_value_after(
            [
                r"total\s+cholesterol"
                r"\s*(?:[:\-]|\s)+"
                r"(\d+(?:\.\d+)?)",

                r"\bcholesterol\b"
                r"\s*(?:[:\-]|\s)+"
                r"(\d+(?:\.\d+)?)"
            ]
        )

        if value is not None:

            ref = self.BIOMARKERS_REF[
                "cholesterol"
            ]

            minimum, maximum, reference = extract_range(
                searchable,
                value_end,
                ref["min"],
                ref["max"],
                ref["unit"]
            )

            status = status_from_value(
                value,
                minimum,
                maximum
            )

            add_biomarker(
                "Total Cholesterol",
                value,
                reference,
                ref["unit"],
                status
            )

        # ==================================================
        # HDL CHOLESTEROL
        # ==================================================

        value, position, value_end = find_value_after(
            [
                r"hdl\s+cholesterol"
                r"\s*(?:[:\-]|\s)+"
                r"(\d+(?:\.\d+)?)",

                r"\bhdl\b"
                r"\s*(?:[:\-]|\s)+"
                r"(\d+(?:\.\d+)?)"
            ]
        )

        if value is not None:

            ref = self.BIOMARKERS_REF[
                "hdl"
            ]

            hdl_section = searchable[
                value_end:value_end + 70
            ]

            hdl_range = re.search(
                r">\s*(\d+(?:\.\d+)?)",
                hdl_section
            )

            if hdl_range:
                minimum = float(hdl_range.group(1))
                maximum = ref["max"]
                reference = (
                    f">{int(minimum) if minimum.is_integer() else minimum} "
                    f"{ref['unit']}"
                )
            else:
                minimum, maximum, reference = extract_range(
                    searchable,
                    value_end,
                    ref["min"],
                    ref["max"],
                    ref["unit"]
                )

            status = status_from_value(
                value,
                minimum,
                maximum
            )

            add_biomarker(
                "HDL Cholesterol",
                value,
                reference,
                ref["unit"],
                status
            )

        # ==================================================
        # LDL CHOLESTEROL
        # OCR: LDL -> LOL
        # ==================================================

        value, position, value_end = find_value_after(
            [
                r"ldl\s+cholesterol"
                r"\s*(?:[:\-]|\s)+"
                r"(\d+(?:\.\d+)?)",

                r"\blol\s+cholesterol"
                r"\s*(?:[:\-]|\s)+"
                r"(\d+(?:\.\d+)?)",

                r"\bldl\b"
                r"\s*(?:[:\-]|\s)+"
                r"(\d+(?:\.\d+)?)"
            ]
        )

        if value is not None:

            ref = self.BIOMARKERS_REF[
                "ldl"
            ]

            minimum, maximum, reference = extract_range(
                searchable,
                value_end,
                ref["min"],
                ref["max"],
                ref["unit"]
            )

            status = status_from_value(
                value,
                minimum,
                maximum
            )

            add_biomarker(
                "LDL Cholesterol",
                value,
                reference,
                ref["unit"],
                status
            )

        # ==================================================
        # TRIGLYCERIDES
        # ==================================================

        value, position, value_end = find_value_after(
            [
                r"triglycerides"
                r"\s*(?:[:\-]|\s)+"
                r"(\d+(?:\.\d+)?)"
            ]
        )

        if value is not None:

            ref = self.BIOMARKERS_REF[
                "triglycerides"
            ]

            minimum, maximum, reference = extract_range(
                searchable,
                value_end,
                ref["min"],
                ref["max"],
                ref["unit"]
            )

            status = status_from_value(
                value,
                minimum,
                maximum
            )

            add_biomarker(
                "Triglycerides",
                value,
                reference,
                ref["unit"],
                status
            )

        # ==================================================
        # TOTAL WBC COUNT
        # ==================================================

        value, position, value_end = find_value_after(
            [
                r"total\s+wbc\s+count"
                r"[^0-9]{0,20}"
                r"(\d+(?:\.\d+)?)",

                r"\bwbc\s+count"
                r"[^0-9]{0,20}"
                r"(\d+(?:\.\d+)?)",

                r"\bwbc\b"
                r"[^0-9]{0,20}"
                r"(\d+(?:\.\d+)?)"
            ]
        )

        if value is not None:

            ref = self.BIOMARKERS_REF["wbc"]

            minimum, maximum, reference = extract_range(
                searchable,
                value_end,
                ref["min"],
                ref["max"],
                ref["unit"]
            )

            status = status_from_value(
                value,
                minimum,
                maximum
            )

            add_biomarker(
                "Total WBC Count",
                value,
                reference,
                ref["unit"],
                status
            )

        # ==================================================
        # PLATELET COUNT
        # ==================================================

        value, position, value_end = find_value_after(
            [
                r"platelet\s+count"
                r"\s*(?:[:\-]|\s)+"
                r"(\d+(?:\.\d+)?)",

                r"\bplatelets?\b"
                r"\s*(?:[:\-]|\s)+"
                r"(\d+(?:\.\d+)?)"
            ]
        )

        if value is not None:

            ref = self.BIOMARKERS_REF["platelets"]

            minimum, maximum, reference = extract_range(
                searchable,
                value_end,
                ref["min"],
                ref["max"],
                ref["unit"]
            )

            status = status_from_value(
                value,
                minimum,
                maximum
            )

            add_biomarker(
                "Platelet Count",
                value,
                reference,
                ref["unit"],
                status
            )

        # ==================================================
        # CREATININE
        # ==================================================

        value, position, value_end = find_value_after(
            [
                r"creatinine"
                r"\s*(?:[:\-]|\s)+"
                r"(\d+(?:\.\d+)?)"
            ]
        )

        if value is not None:

            ref = self.BIOMARKERS_REF["creatinine"]

            minimum, maximum, reference = extract_range(
                searchable,
                value_end,
                ref["min"],
                ref["max"],
                ref["unit"]
            )

            status = status_from_value(
                value,
                minimum,
                maximum
            )

            add_biomarker(
                "Serum Creatinine",
                value,
                reference,
                ref["unit"],
                status
            )

        # ==================================================
        # URIC ACID
        # ==================================================

        value, position, value_end = find_value_after(
            [
                r"serum\s+uric\s+acid"
                r"\s*(?:[:\-]|\s)+"
                r"(\d+(?:\.\d+)?)",

                r"uric\s+acid"
                r"\s*(?:[:\-]|\s)+"
                r"(\d+(?:\.\d+)?)"
            ]
        )

        if value is not None:

            ref = self.BIOMARKERS_REF["uric_acid"]

            uric_section = searchable[
                value_end:value_end + 80
            ]

            uric_range = re.search(
                r"(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)",
                uric_section
            )

            if uric_range:
                minimum = float(uric_range.group(1))
                maximum = float(uric_range.group(2))
                reference = (
                    f"{minimum:g}-{maximum:g} "
                    f"{ref['unit']}"
                )
            else:
                minimum, maximum, reference = extract_range(
                    searchable,
                    value_end,
                    ref["min"],
                    ref["max"],
                    ref["unit"]
                )

            status = status_from_value(
                value,
                minimum,
                maximum
            )

            add_biomarker(
                "Serum Uric Acid",
                value,
                reference,
                ref["unit"],
                status
            )

        # ==================================================
        # SGPT / ALT
        # ==================================================

        value, position, value_end = find_value_after(
            [
                r"sgpt\s*\(\s*alt\s*\)"
                r"\s*(?:[:\-]|\s)+"
                r"(\d+(?:\.\d+)?)",

                r"sgpt"
                r"\s*(?:[:\-]|\s)+"
                r"(\d+(?:\.\d+)?)",

                r"\balt\b"
                r"\s*(?:[:\-]|\s)+"
                r"(\d+(?:\.\d+)?)"
            ]
        )

        if value is not None:

            ref = self.BIOMARKERS_REF["alt"]

            minimum, maximum, reference = extract_range(
                searchable,
                value_end,
                ref["min"],
                ref["max"],
                ref["unit"]
            )

            status = status_from_value(
                value,
                minimum,
                maximum
            )

            add_biomarker(
                "SGPT (ALT)",
                value,
                reference,
                ref["unit"],
                status
            )

        # ==================================================
        # SGOT / AST
        # ==================================================

        value, position, value_end = find_value_after(
            [
                r"sgot\s*\(\s*ast\s*\)"
                r"\s*(?:[:\-]|\s)+"
                r"(\d+(?:\.\d+)?)",

                r"sgot"
                r"\s*(?:[:\-]|\s)+"
                r"(\d+(?:\.\d+)?)",

                r"\bast\b"
                r"\s*(?:[:\-]|\s)+"
                r"(\d+(?:\.\d+)?)"
            ]
        )

        if value is not None:

            ref = self.BIOMARKERS_REF["ast"]

            minimum, maximum, reference = extract_range(
                searchable,
                value_end,
                ref["min"],
                ref["max"],
                ref["unit"]
            )

            status = status_from_value(
                value,
                minimum,
                maximum
            )

            add_biomarker(
                "SGOT (AST)",
                value,
                reference,
                ref["unit"],
                status
            )

        # ==================================================
        # REMOVE DUPLICATES
        # ==================================================

        unique = {}

        for item in biomarkers:

            unique[
                item["biomarker"]
            ] = item

        biomarkers = list(
            unique.values()
        )

        # ==================================================
        # SUMMARY
        # ==================================================

        abnormal_count = sum(
            1
            for item in biomarkers
            if item["status"] in ("High", "Low")
        )

        if biomarkers:

            if abnormal_count == 0:

                summary = (
                    f"Parsed laboratory report. "
                    f"Identified {len(biomarkers)} "
                    f"biomarker(s). All detected biomarkers "
                    f"fall within the configured reference limits."
                )

                recommendations = (
                    "All detected biomarkers fall within the "
                    "No laboratory abnormalities were identified in the analyzed parameters. "
                    "Continue routine health monitoring, maintain a balanced diet, adequate hydration, "
                    "regular physical activity, and appropriate sleep. Follow the treating physician's "
                    "recommendations and seek medical review if symptoms persist or worsen."
                )

            else:

                abnormal_names = ", ".join(
                    item["biomarker"]
                    for item in biomarkers
                    if item["status"] in ("High", "Low")
                )

                summary = (
                    f"Parsed laboratory report. "
                    f"Identified {len(biomarkers)} biomarker(s). "
                    f"{abnormal_count} value(s) are outside the "
                    f"configured reference limits: "
                    f"{abnormal_names}."
                )

                recommendations = (
                    f"Clinical review is recommended for the "
                    f"following out-of-range result(s): "
                    f"{abnormal_names}. This automated analysis "
                    f"is not a diagnosis."
                )

        else:

            summary = (
                "The report text was successfully extracted, "
                "but no supported biomarkers could be identified."
            )

            recommendations = (
                "Review the extracted report text and consult "
                "a qualified healthcare professional if needed."
            )

        return {
            "biomarkers_found": biomarkers,
            "abnormalities_count": abnormal_count,
            "summary": summary,
            "recommendations": recommendations
        }

