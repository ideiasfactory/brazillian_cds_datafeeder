"""Logging utilities for the Brazilian CDS application."""
import sys
import logging
from typing import Optional

from loguru import logger

from config import settings


def _build_ingest_url(host: str) -> str:
    """Return a proper HTTPS URL for Logtail ingestion based on provided host.

    Accepts either full URL (https://example) or bare host (example). Ensures
    we return an https URL without trailing slash.
    
    Args:
        host: The host URL or hostname
        
    Returns:
        Properly formatted HTTPS URL
    """
    if not host:
        return "https://in.logtail.com"
    h = host.strip()
    if not h.startswith("http://") and not h.startswith("https://"):
        h = f"https://{h}"
    return h.rstrip("/")


def setup_logging() -> bool:
    """Configure loguru to log to console and forward to BetterStack when configured.
    
    Returns:
        True if BetterStack integration was successful, False otherwise
    """
    # Reset sinks and add console sink
    logger.remove()
    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        enqueue=True,
        backtrace=False,
        diagnose=False,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
    )

    # Try lazy import of BetterStack (logtail) and set flag
    has_betterstack = False
    try:
        from logtail import LogtailHandler
        has_betterstack = True
    except ImportError:
        logger.debug("BetterStack library not installed (pip install logtail-python)")
        return False

    # BetterStack forwarding
    if has_betterstack and settings.BETTERSTACK_SOURCE_TOKEN:
        try:
            ingest_url = _build_ingest_url(settings.BETTERSTACK_INGESTING_HOST)
            logtail_handler = LogtailHandler(
                source_token=settings.BETTERSTACK_SOURCE_TOKEN,
                host=ingest_url,
            )

            level_map = {
                "TRACE": logging.DEBUG,
                "DEBUG": logging.DEBUG,
                "INFO": logging.INFO,
                "SUCCESS": logging.INFO,
                "WARNING": logging.WARNING,
                "ERROR": logging.ERROR,
                "CRITICAL": logging.CRITICAL,
            }

            def betterstack_sink(message):
                rec = message.record
                lvl = level_map.get(rec["level"].name, logging.INFO)
                try:
                    log_record = logging.LogRecord(
                        name="loguru",
                        level=lvl,
                        pathname=rec["file"].path,
                        lineno=rec["line"],
                        msg=rec["message"],
                        args=(),
                        exc_info=None,
                    )
                    # Set created timestamp
                    log_record.created = rec["time"].timestamp()
                    log_record.funcName = rec["function"]
                    logtail_handler.emit(log_record)
                except Exception:
                    # Never break the app due to logging failure
                    pass

            logger.add(betterstack_sink, level="INFO")
            logger.info(f"BetterStack forwarding enabled -> {ingest_url}")
            return True
        except Exception as e:
            logger.warning(f"BetterStack setup failed: {e}")
            return False
    else:
        if not settings.BETTERSTACK_SOURCE_TOKEN:
            logger.debug("BetterStack not configured (BETTERSTACK_SOURCE_TOKEN not set)")
        return False


def get_logger():
    """Get the configured logger instance.
    
    Returns:
        The loguru logger instance
    """
    return logger
