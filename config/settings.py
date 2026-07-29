import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from cryptography.fernet import Fernet

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    OPENAI_API_KEY: str = "mock-openai-key-for-testing"
    DATABASE_URL: str = "sqlite:///./healthcare_agent.db"
    ENCRYPTION_KEY: str = "zP84b3FmXqY6W9J1k8D3vN4g8L0x1c2vB3n4m5a6s7d="
    LOG_LEVEL: str = "INFO"
    AUDIT_LOG_FILE: str = "logs/audit.log"
    SYSTEM_LOG_FILE: str = "logs/system.log"
    TESSERACT_CMD: str = ""

    # Property to get a cryptography cipher suite
    @property
    def cipher_suite(self) -> Fernet:
        try:
            return Fernet(self.ENCRYPTION_KEY.encode())
        except Exception as e:
            # Fallback for dynamic generation in case of key error
            fallback_key = Fernet.generate_key()
            return Fernet(fallback_key)

# Global settings instance
settings = Settings()

# Ensure log directory exists
os.makedirs("logs", exist_ok=True)
