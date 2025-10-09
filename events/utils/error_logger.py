import logging
from typing import Any, Dict


logger = logging.getLogger('events')


class ErrorLogger:
    @staticmethod
    def log_purchase_flow(stage: str, data: Dict[str, Any]) -> None:
        try:
            logger.info(f"PURCHASE_FLOW | {stage} | {data}")
        except Exception:
            pass

    @staticmethod
    def log_object_state(obj: Any, tag: str) -> None:
        try:
            model = obj.__class__.__name__
            payload = {
                'model': model,
                'tag': tag,
                'state': getattr(obj, '__dict__', {})
            }
            logger.info(f"OBJECT_STATE | {payload}")
        except Exception:
            pass

    @staticmethod
    def log_ticket_error(exc: Exception, context: Dict[str, Any]) -> None:
        try:
            logger.error(f"TICKET_ERROR | {exc} | {context}")
        except Exception:
            pass