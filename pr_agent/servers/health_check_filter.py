import logging
import re


class HealthCheckFilter(logging.Filter):
    """Filter out successful health check requests from access logs

    This filter silences successful health requests from appearing
    in uvicorn access logs to reduce log spam.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter out GET / requests (health checks)

        Args:
            record: The log record to filter

        Returns:
            False if the record is a successful health check request, True otherwise
        """
        # Get the message and strip ANSI color codes
        message = record.getMessage()
        clean_message = re.sub(r"\x1b\[[0-9;]*m", "", message)

        # Filter out health check requests
        return '"GET / HTTP/1.1" 200' not in clean_message


def configure_health_check_logging():
    """Configure uvicorn access logger to filter out health check requests"""
    logging.getLogger("uvicorn.access").addFilter(HealthCheckFilter())
