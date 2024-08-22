"""Logging helper functions."""

from __future__ import annotations

import structlog

LOGGER = structlog.get_logger()


def log_and_raise_error(message: str):
    """Log a response and raise an error.

    Args:
         message: plain error text message.

    Raises:
        ValueError: Reraise with the error message.
    """
    LOGGER.info(message)
    raise ValueError(message)


def log(message: str):
    """Log a response.

    Args:
         message: plain error text message.
    """
    LOGGER.info(message)
