import logging
import os
import functools
from datetime import datetime
from pathlib import Path


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output"""

    COLORS = {
        'DEBUG': '\033[36m',  # Cyan
        'INFO': '\033[32m',  # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',  # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)


def get_logger(name: str = __name__, level: str = "INFO") -> logging.Logger:
    """
    Create and configure logger with file and console handlers

    Args:
        name: Logger name (usually __name__)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance

    Example:
        log = get_logger(__name__)
        log.info("Test execution started")
    """
    logger = logging.getLogger(name)

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, level.upper()))
    logger.propagate = False  # Prevent duplicate logs

    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # === File Handler (Detailed logs) ===
    timestamp = datetime.now().strftime("%Y%m%d")
    file_handler = logging.FileHandler(
        log_dir / f"test_{timestamp}.log",
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)

    file_formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)

    # === Console Handler (Colored output) ===
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    console_formatter = ColoredFormatter(
        '%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)

    # === Error File Handler (Errors only) ===
    error_handler = logging.FileHandler(
        log_dir / f"errors_{timestamp}.log",
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)

    # Add all handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.addHandler(error_handler)

    return logger


def log_test_step(description: str):
    """
    Decorator to log test steps with execution time

    Args:
        description: Step description

    Example:
        @log_test_step("Navigate to login page")
        def navigate_to_login(page):
            page.goto("/login")
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            log = get_logger(func.__module__)
            log.info(f"▶ STEP: {description}")

            try:
                result = func(*args, **kwargs)
                log.info(f"✓ PASSED: {description}")
                return result
            except Exception as e:
                log.error(f"✗ FAILED: {description} | Error: {str(e)}")
                raise

        return wrapper

    return decorator


def log_api_request(method: str, url: str, status_code: int = None, response_time: float = None):
    """
    Log API request details

    Args:
        method: HTTP method (GET, POST, etc.)
        url: Request URL
        status_code: Response status code
        response_time: Response time in seconds
    """
    log = get_logger("api")
    msg = f"{method} {url}"

    if status_code:
        msg += f" | Status: {status_code}"
    if response_time:
        msg += f" | Time: {response_time:.2f}s"

    if status_code and status_code >= 400:
        log.error(msg)
    else:
        log.info(msg)


def log_screenshot(screenshot_path: str, reason: str = "Screenshot captured"):
    """
    Log screenshot capture

    Args:
        screenshot_path: Path to screenshot file
        reason: Reason for screenshot
    """
    log = get_logger("screenshot")
    log.info(f"📸 {reason} | Saved to: {screenshot_path}")


def cleanup_old_logs(days: int = 7):
    """
    Delete log files older than specified days

    Args:
        days: Number of days to keep logs
    """
    log_dir = Path("logs")
    if not log_dir.exists():
        return

    cutoff = datetime.now().timestamp() - (days * 86400)

    for log_file in log_dir.glob("*.log"):
        if log_file.stat().st_mtime < cutoff:
            log_file.unlink()
            print(f"Deleted old log: {log_file.name}")