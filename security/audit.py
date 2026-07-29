from database.operations import add_audit_log
from database.connection import get_db
from config.logging_config import system_logger

def log_security_event(
    action: str,
    performed_by: str,
    change_summary: str,
    record_id: int = None,
    table: str = None
):
    """
    Direct security auditing helper. Instantiates a transient database session 
    to log structural changes or unauthorized event blocks.
    """
    try:
        with get_db() as db:
            add_audit_log(
                db=db,
                user_action=action,
                target_table=table,
                record_id=record_id,
                performed_by=performed_by,
                change_summary=change_summary
            )
    except Exception as e:
        system_logger.critical(f"FATAL: Failed to write to audit log in DB: {e}. Event Action: {action}")
