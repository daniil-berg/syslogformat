"""Definition of the central `SyslogFormatter` class."""

from __future__ import annotations

from logging import Formatter, LogRecord
from types import TracebackType
from typing import Any, Mapping, Optional, Tuple, Type
from typing_extensions import Literal

__all__ = ["SyslogFormatter"]

ExcInfo = Tuple[Type[BaseException], BaseException, Optional[TracebackType]]


class SyslogFormatter(Formatter):
    """
    Log formatter class for `syslog`-style log messages.

    It does three things to every log message:
    1) Prepends a `syslog` PRI part depending on the log level.
    2) Formats exception log messages into one-liners.
    3) Appends additional details, when a specified level is exceeded.

    See the relevant section of
    [RFC 3164](https://datatracker.ietf.org/doc/html/rfc3164#section-4.1)
    for details about `syslog` standard.
    """
    def __init__(
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        style: Literal["%", "{", "$"] = "%",
        validate: bool = True,
        *,
        defaults: Mapping[str, Any] | None = None,
    ):
        """Validates the formatter construction arguments."""
        raise NotImplementedError

    def formatException(self, ei: ExcInfo | Tuple[None, None, None]) -> str:
        """Ensures that an exception message prints as a single line."""
        raise NotImplementedError

    def format(self, record: LogRecord) -> str:
        """
        Formats a record to be compliant with syslog PRI (log level/severity).

        Removes the line-breaks with.
        The entire message format is hard-coded here, so that no format needs to
        be specified in the usual config.
        """
        raise NotImplementedError
