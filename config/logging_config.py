import logging
import os
import json
from datetime import datetime
from config.settings import settings

# Create logs directory if not exists
os.makedirs("logs", exist_ok=True)

# System logging setup
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(settings.SYSTEM_LOG_FILE),
        logging.StreamHandler()
    ]
)

system_logger = logging.getLogger("healthcare_system")

# Audit logging setup (Structured logs for security compliance)
audit_logger = logging.getLogger("healthcare_audit")
audit_logger.setLevel(logging.INFO)
audit_logger.propagate = False  # Avoid printing audit logs to normal output streams

# Custom formatter for JSON audit logging
class JSONAuditFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage()
        }
        # Add custom audit context if present
        if hasattr(record, "audit_context"):
            log_entry.update(record.audit_context)
        return json.dumps(log_entry)

audit_handler = logging.FileHandler(settings.AUDIT_LOG_FILE)
audit_handler.setFormatter(JSONAuditFormatter())
audit_logger.addHandler(audit_handler)

def log_audit_event(action: str, target: str, user: str, details: dict):
    """
    Structured audit logging helper.
    """
    context = {
        "action": action,
        "target": target,
        "performed_by": user,
        "details": details
    }
    audit_logger.info(
        f"Audit Event: {action} on {target} by {user}",
        extra={"audit_context": context}
    )
