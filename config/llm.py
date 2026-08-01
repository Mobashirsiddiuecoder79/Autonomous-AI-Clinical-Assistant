import json
import re
from typing import Any, Dict, Optional

from langchain_google_genai import ChatGoogleGenerativeAI

from config.settings import settings
from config.logging_config import system_logger


class LLMProvider:
    """
    Centralized LLM Provider.
    """

    def __init__(self):

        if not settings.GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY is missing in .env"
            )

        self.model = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.2,
        )

    # =====================================================
    # Text Generation
    # =====================================================

    def generate(
        self,
        prompt: str,
    ) -> str:

        response = self.model.invoke(prompt)

        print(type(response.content))
        print(response.content)

        content = response.content

        if isinstance(content, str):
            return content.strip()

        if isinstance(content, list):

            parts = []

            for item in content:

                if isinstance(item, str):
                    parts.append(item)

                elif isinstance(item, dict):
                    if "text" in item:
                        parts.append(item["text"])

                elif hasattr(item, "text"):
                    parts.append(item.text)

                else:
                    parts.append(str(item))

            return "\n".join(parts).strip()

        return str(content).strip()

    # =====================================================
    # Extract JSON
    # =====================================================

    def _extract_json(
        self,
        text: str,
    ) -> str:

        text = text.strip()

        text = re.sub(
            r"^```json",
            "",
            text,
            flags=re.IGNORECASE,
        )

        text = re.sub(
            r"^```",
            "",
            text,
        )

        text = re.sub(
            r"```$",
            "",
            text,
        )

        text = text.strip()

        match = re.search(
            r"\{.*\}",
            text,
            flags=re.DOTALL,
        )

        if match:
            return match.group(0)

        raise ValueError(
            "No JSON object found."
        )

    # =====================================================
    # JSON Generation
    # =====================================================

    def generate_json(
        self,
        prompt: str,
        retries: int = 3,
    ) -> Dict[str, Any]:

        last_error = None

        for attempt in range(retries):

            try:

                raw = self.generate(prompt)

                json_text = self._extract_json(raw)

                return json.loads(json_text)

            except Exception as e:

                last_error = e

                system_logger.warning(
                    f"JSON parse failed (attempt {attempt + 1}/{retries}): {e}"
                )

        raise RuntimeError(
            f"Unable to obtain valid JSON from Gemini. {last_error}"
        )


_provider: Optional[LLMProvider] = None


def get_llm() -> LLMProvider:

    global _provider

    if _provider is None:
        _provider = LLMProvider()

    return _provider