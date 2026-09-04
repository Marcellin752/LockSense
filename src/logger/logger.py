#!/usr/bin/env python3
##
## PROJECT, 2026
## LockSense
## File description:
## Daily rotating file logger with configurable level and retention
##

import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
import sys


def setup_logger(name="locksense", config=None):
    """
    Sets up a daily rotating file logger.

    Configuration (config dict, optional):
        logging.level: DEBUG, INFO, WARNING, ERROR, CRITICAL
        logging.retention_days: number of days to keep rotated files

    Output:
        - logs/locksense.log (current day)
        - logs/locksense.log.YYYY-MM-DD (rotated files)
    """
    if config is None:
        config = {}

    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    log_config = config.get("logging", {})
    level_name = log_config.get("level", "INFO")
    level = getattr(logging, level_name.upper(), logging.INFO)
    retention_days = log_config.get("retention_days", 7)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Daily rotation at midnight, suffixed with date
    file_handler = TimedRotatingFileHandler(
        filename=str(log_dir / "locksense.log"),
        when="midnight",
        interval=1,
        backupCount=retention_days,
        encoding="utf-8",
        utc=False
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    file_handler.suffix = "%Y-%m-%d"

    # Console (stderr)
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    # Avoid duplicate handlers when called multiple times
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    logger.info("Logger initialized (level=%s, retention=%d days)", level_name, retention_days)
    return logger