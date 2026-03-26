"""Library-wide control for goblintools log verbosity."""
import logging
from typing import Any, Optional

_suppress_warnings: bool = False


def configure(*, suppress_warnings: Optional[bool] = None) -> None:
    """
    App-level setup (call once at startup, e.g. next to logging configuration).

    Example:
        import goblintools
        goblintools.configure(suppress_warnings=True)
    """
    if suppress_warnings is not None:
        _set_suppress_warnings(suppress_warnings)


def _set_suppress_warnings(suppress: bool) -> None:
    global _suppress_warnings
    _suppress_warnings = bool(suppress)


def _warnings_suppressed() -> bool:
    return _suppress_warnings


def log_warning(logger: logging.Logger, msg: str, *args: Any, **kwargs: Any) -> None:
    if not _warnings_suppressed():
        logger.warning(msg, *args, **kwargs)
