"""
Logging utilities for financial data download operations.
Provides structured logging with file and console output.
"""

import logging
import os
from datetime import datetime
from typing import Optional

import platform

WINDOWS = platform.system() == "Windows"

def safe_symbol(symbol, fallback):
    return fallback if WINDOWS else symbol

class DataLogger:
    """
    Logger class for data download and processing operations.
    Provides colored console output and file logging.
    """

    # ANSI color codes for terminal output
    COLORS = {
        'RESET': '\033[0m',
        'GREEN': '\033[92m',
        'YELLOW': '\033[93m',
        'RED': '\033[91m',
        'BLUE': '\033[94m',
        'CYAN': '\033[96m',
    }

    def __init__(self, name: str = "data_logger",
                 log_dir: str = "../logs",
                 enable_file_logging: bool = True,
                 enable_console_colors: bool = True):
        """
        Initialize the logger.

        Parameters:
        -----------
        name : str, default="data_logger"
            Logger name
        log_dir : str, default="../logs"
            Directory for log files
        enable_file_logging : bool, default=True
            Whether to save logs to file
        enable_console_colors : bool, default=True
            Whether to use colored console output
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.enable_colors = enable_console_colors
        self.log_dir = log_dir

        # Remove existing handlers to avoid duplicates
        self.logger.handlers.clear()

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setStream(open(1, "w", encoding="utf-8", closefd=False))
        console_handler.setLevel(logging.DEBUG)
        console_format = self._get_formatter()
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)

        # File handler (optional)
        if enable_file_logging:
            self._setup_file_handler()

    def _get_formatter(self) -> logging.Formatter:
        """Get formatter for logging."""
        return logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    def _setup_file_handler(self) -> None:
        """Setup file handler for logging to file."""
        os.makedirs(self.log_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d")
        log_file = os.path.join(self.log_dir, f"data_download_{timestamp}.log")

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(self._get_formatter())
        self.logger.addHandler(file_handler)

    def _colorize(self, message: str, color: str) -> str:
        """Add color to console message."""
        if not self.enable_colors:
            return message
        return f"{self.COLORS[color]}{message}{self.COLORS['RESET']}"

    def info(self, message: str) -> None:
        """Log info message (green)."""
        symbol = safe_symbol("✓", "[OK]")
        colored_msg = self._colorize(f"{symbol} {message}", 'GREEN')
        self.logger.info(colored_msg)

    def success(self, message: str) -> None:
        """Log success message (green)."""
        symbol = safe_symbol("✓", "[OK]")
        colored_msg = self._colorize(f"{symbol} {message}", 'GREEN')
        self.logger.info(colored_msg)

    def warning(self, message: str) -> None:
        """Log warning message (yellow)."""
        symbol = safe_symbol("⚠", "[WARN]")
        colored_msg = self._colorize(f"{symbol} {message}", 'YELLOW')
        self.logger.warning(colored_msg)

    def error(self, message: str) -> None:
        """Log error message (red)."""
        symbol = safe_symbol("✗", "[ERR]")
        colored_msg = self._colorize(f"{symbol} {message}", 'RED')
        self.logger.error(colored_msg)

    def debug(self, message: str) -> None:
        """Log debug message (cyan)."""
        symbol = safe_symbol("⚙", "[DBG]")
        colored_msg = self._colorize(f"{symbol} {message}", 'CYAN')
        self.logger.debug(colored_msg)
    def separator(self) -> None:
        """Print a separator line."""
        separator = "-" * 50
        print(self._colorize(separator, 'BLUE'))


def setup_logging(name: str = "volatility_prediction",
                  log_dir: str = "../logs",
                  level: int = logging.INFO) -> logging.Logger:
    """
    Setup logging configuration for the project.

    Parameters:
    -----------
    name : str, default="volatility_prediction"
        Logger name
    log_dir : str, default="../logs"
        Directory for log files
    level : int, default=logging.INFO
        Logging level

    Returns:
    --------
    logging.Logger
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create logs directory
    os.makedirs(log_dir, exist_ok=True)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # File handler
    timestamp = datetime.now().strftime("%Y%m%d")
    log_file = os.path.join(log_dir, f"{name}_{timestamp}.log")
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    file_handler.setFormatter(console_format)
    logger.addHandler(file_handler)

    return logger


class DownloadLogger(DataLogger):
    """Specialized logger for download operations."""

    def __init__(self, log_dir: str = "../logs"):
        """Initialize download logger."""
        super().__init__(
            name="download_logger",
            log_dir=log_dir,
            enable_file_logging=True,
            enable_console_colors=True
        )

    def log_download_start(self, ticker: str, period: str, interval: str) -> None:
        """Log the start of a download operation."""
        msg = f"Starting download: {ticker} (period={period}, interval={interval})"
        self.info(msg)

    def log_download_complete(self, ticker: str, rows: int, filepath: str) -> None:
        """Log successful download completion."""
        msg = f"Download complete: {ticker} - {rows} rows saved to {filepath}"
        self.success(msg)

    def log_download_error(self, ticker: str, error: str) -> None:
        """Log download error."""
        msg = f"Download failed for {ticker}: {error}"
        self.error(msg)

    def log_data_stats(self, ticker: str, rows: int, columns: list) -> None:
        """Log data statistics."""
        col_str = ", ".join(columns)
        msg = f"{ticker} | Rows: {rows} | Columns: {col_str}"
        self.debug(msg)