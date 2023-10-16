"""Definition of the central `SyslogFormatter` class."""

from logging import Formatter, LogRecord

__all__ = ["SyslogFormatter"]


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
    def __init__(self, *args, **kwargs):
        """Validates the formatter construction arguments."""
        raise NotImplementedError

    def formatException(self, exc_info) -> str:
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
