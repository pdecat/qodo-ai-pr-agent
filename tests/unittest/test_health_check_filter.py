import logging
import unittest
from unittest.mock import MagicMock

from pr_agent.servers.health_check_filter import HealthCheckFilter, configure_health_check_logging


class TestHealthCheckFilter(unittest.TestCase):
    """Test cases for the HealthCheckFilter class"""

    def setUp(self):
        """Set up test fixtures"""
        self.filter = HealthCheckFilter()

    def test_filter_blocks_successful_health_check(self):
        """Test that successful health check requests are filtered out"""
        # Create a mock log record with a successful health check message
        record = MagicMock(spec=logging.LogRecord)
        record.getMessage.return_value = 'INFO:     172.23.129.125:41456 - "GET / HTTP/1.1" 200 OK'

        # The filter should return False to block this log
        self.assertFalse(self.filter.filter(record))

    def test_filter_allows_failed_health_check(self):
        """Test that failed health check requests are NOT filtered out"""
        # Create a mock log record with a failed health check message
        record = MagicMock(spec=logging.LogRecord)
        record.getMessage.return_value = 'INFO:     172.23.129.125:41456 - "GET / HTTP/1.1" 404 Not Found'

        # The filter should return True to allow this log
        self.assertTrue(self.filter.filter(record))

    def test_filter_allows_other_get_requests(self):
        """Test that other GET requests are NOT filtered out"""
        # Create a mock log record with a different GET request
        record = MagicMock(spec=logging.LogRecord)
        record.getMessage.return_value = 'INFO:     172.23.129.125:41456 - "GET /webhook HTTP/1.1" 200 OK'

        # The filter should return True to allow this log
        self.assertTrue(self.filter.filter(record))

    def test_filter_allows_post_requests(self):
        """Test that POST requests are NOT filtered out"""
        # Create a mock log record with a POST request
        record = MagicMock(spec=logging.LogRecord)
        record.getMessage.return_value = 'INFO:     172.23.129.125:41456 - "POST /webhook HTTP/1.1" 200 OK'

        # The filter should return True to allow this log
        self.assertTrue(self.filter.filter(record))

    def test_filter_allows_root_post_request(self):
        """Test that POST requests to root are NOT filtered out"""
        # Create a mock log record with a POST request to root
        record = MagicMock(spec=logging.LogRecord)
        record.getMessage.return_value = 'INFO:     172.23.129.125:41456 - "POST / HTTP/1.1" 200 OK'

        # The filter should return True to allow this log
        self.assertTrue(self.filter.filter(record))

    def test_filter_allows_error_logs(self):
        """Test that error logs are NOT filtered out"""
        # Create a mock log record with an error message
        record = MagicMock(spec=logging.LogRecord)
        record.getMessage.return_value = "ERROR:    Failed to process webhook"

        # The filter should return True to allow this log
        self.assertTrue(self.filter.filter(record))

    def test_filter_blocks_multiple_health_check_formats(self):
        """Test that health checks with different IP addresses are filtered"""
        test_cases = [
            'INFO:     172.23.129.125:41456 - "GET / HTTP/1.1" 200 OK',
            'INFO:     10.0.0.1:12345 - "GET / HTTP/1.1" 200 OK',
            'INFO:     192.168.1.100:54898 - "GET / HTTP/1.1" 200 OK',
            'INFO:     127.0.0.1:8080 - "GET / HTTP/1.1" 200 OK',
        ]

        for message in test_cases:
            with self.subTest(message=message):
                record = MagicMock(spec=logging.LogRecord)
                record.getMessage.return_value = message
                self.assertFalse(self.filter.filter(record), f"Should filter out: {message}")

    def test_configure_health_check_logging(self):
        """Test that configure_health_check_logging adds the filter to uvicorn.access logger"""
        # Get the uvicorn.access logger
        logger = logging.getLogger("uvicorn.access")

        # Clear any existing filters
        logger.filters.clear()

        # Configure health check logging
        configure_health_check_logging()

        # Check that a HealthCheckFilter was added
        self.assertEqual(len(logger.filters), 1)
        self.assertIsInstance(logger.filters[0], HealthCheckFilter)

        # Clean up
        logger.filters.clear()

    def test_filter_with_http_1_1(self):
        """Test that health checks with HTTP/1.1 are filtered"""
        test_cases = [
            'INFO:     172.23.129.125:41456 - "GET / HTTP/1.1" 200 OK',
            'INFO:     10.0.0.1:12345 - "GET / HTTP/1.1" 200 OK',
        ]

        for message in test_cases:
            with self.subTest(message=message):
                record = MagicMock(spec=logging.LogRecord)
                record.getMessage.return_value = message
                self.assertFalse(self.filter.filter(record), f"Should filter out: {message}")


if __name__ == "__main__":
    unittest.main()
