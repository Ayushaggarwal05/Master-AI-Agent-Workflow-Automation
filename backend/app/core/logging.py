import logging
import sys
from typing import Optional

class CustomFormatter(logging.Formatter):
    """Clean, structured console logging formatter with optional ANSI colors."""
    
    GREY = "\x1b[38;20m"
    BLUE = "\x1b[34;20m"
    GREEN = "\x1b[32;20m"
    YELLOW = "\x1b[33;20m"
    RED = "\x1b[31;20m"
    BOLD_RED = "\x1b[31;1m"
    RESET = "\x1b[0m"
    
    FORMAT_STR = "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"

    FORMATS = {
        logging.DEBUG: GREY + FORMAT_STR + RESET,
        logging.INFO: GREEN + FORMAT_STR + RESET,
        logging.WARNING: YELLOW + FORMAT_STR + RESET,
        logging.ERROR: RED + FORMAT_STR + RESET,
        logging.CRITICAL: BOLD_RED + FORMAT_STR + RESET
    }

    def format(self, record: logging.LogRecord) -> str:
        log_fmt = self.FORMATS.get(record.levelno, self.FORMAT_STR)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)

def setup_logging(log_level: str = "INFO") -> None:
    """Configures root and application loggers."""
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Remove existing handlers to avoid duplicates
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
        
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(numeric_level)
    handler.setFormatter(CustomFormatter())
    
    root_logger.addHandler(handler)
    
    # Silence overly noisy external loggers if necessary
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Returns a named logger instance."""
    return logging.getLogger(name or "webvory.app")
