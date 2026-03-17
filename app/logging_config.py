import logging
import json
from datetime import datetime


class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "service": "api-gateway",
            "message": record.getMessage(),
        }

        # Include request_id if present
        if hasattr(record, "request_id"):
            log_record["request_id"] = record.request_id

        return json.dumps(log_record)


def setup_logging():
    logger = logging.getLogger("api-gateway")
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())

    logger.handlers.clear()
    logger.addHandler(handler)

    return logger
