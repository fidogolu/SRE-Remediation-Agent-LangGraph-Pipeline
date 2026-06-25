# utils/logger.py
"""Structured logging setup with console and file handlers."""
import logging
import os
import sys


def get_logger() -> logging.Logger:
    """
    Returns a logger with console and file handlers configured.

    Initializes a logger named "app". If already initialized, returns it.
    Otherwise, configures a console handler (stdout) and a file handler
    writing to 'logs/app.log'.

    The log level is defined by the LOG_LEVEL environment variable.
    Defaults to INFO.

    Returns:
        logging.Logger: The configured logger instance.
    """
    logger = logging.getLogger("app")

    if logger.handlers:
        return logger

    logger.propagate = False

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    logger.addHandler(console_handler)

    os.makedirs("logs", exist_ok=True)
    file_handler = logging.FileHandler("logs/app.log")
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(file_handler)

    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logger.setLevel(getattr(logging, log_level, logging.INFO))

    return logger


LOGGER = get_logger()
