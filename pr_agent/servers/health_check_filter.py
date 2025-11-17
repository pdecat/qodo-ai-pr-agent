import logging


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
        # Filter out health checks requests
        return '"GET / HTTP/1.1" 200 OK' not in record.getMessage()


def configure_health_check_logging():
    """Configure uvicorn access logger to filter out health check requests"""
    logging.getLogger("uvicorn.access").addFilter(HealthCheckFilter())
