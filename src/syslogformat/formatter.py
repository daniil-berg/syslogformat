"""Definition of the central `SyslogFormatter` class."""

from __future__ import annotations

from logging import WARNING, Formatter, LogRecord
from types import TracebackType
from typing import Any, Mapping, Optional, Tuple, Type
from typing_extensions import Literal

from .facility import USER

__all__ = ["SyslogFormatter"]

ExcInfo = Tuple[Type[BaseException], BaseException, Optional[TracebackType]]

DEFAULT_TRACEBACK_LINE_SEP = " --> "


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
        facility: int = USER,
        traceback_line_sep: str = DEFAULT_TRACEBACK_LINE_SEP,
        detail_threshold: int = WARNING,
        prepend_level_name: bool = True,
    ) -> None:
        """
        Validates the added formatter constructor arguments.

        For details about the base class' constructor parameters, the official
        [docs](https://docs.python.org/3/library/logging.html#logging.Formatter)
        provide full explanations.

        Args:
            fmt (optional):
                A format string in the given `style` for the logged output as a
                whole. The possible mapping keys are drawn from the
                `logging.LogRecord` object’s
                [attributes]((https://docs.python.org/3/library/logging.html#logrecord-attributes).
                If not specified, `%(message)s | %(name)s` will be used and
                passed to the parent `__init__`. If any custom string is passed,
                the `detail_threshold` and `prepend_level_name` arguments will
                be ignored and that string is passed through unchanged to the
                parent `__init__`.
            datefmt (optional):
                Passed through to the parent `__init__`.
            style (optional):
                Passed through to the parent `__init__`.
            validate (optional):
                If `True` (default), incorrect or mismatched `fmt` and `style`
                will raise a `ValueError`; for example,
                `logging.Formatter('%(asctime)s - %(message)s', style='{')`.
                Also, if `True`, a non-standard `facility` value (i.e. not
                between 0 and 24) will raise a `ValueError`.
                The argument is always passed through to the parent `__init__`.
            defaults (optional):
                Passed through to the parent `__init__`.
            facility (optional):
                Used to calculate the number in the PRI part at the very start
                of each log message. This argument should be an integer between
                0 and 24. The `facility` value is multiplied by 8 and added
                to the numerical value of the severity that corresponds to the
                log level of the message.
                Details about accepted numerical values can be found in
                [section 4.1.1](https://datatracker.ietf.org/doc/html/rfc3164#section-4.1.1)
                of RFC 3164.
                Defaults to `syslogformat.facility.USER`.
            traceback_line_sep (optional):
                Log records that include exception information normally result
                in the multi-line traceback being included in the log message.
                To prevent a single log message taking up more than one line,
                every line-break (and consecutive whitespace) in the exception
                traceback will be replaced with the string provided here.
                Defaults to `syslogformat.formatter.DEFAULT_TRACEBACK_LINE_SEP`.
            detail_threshold (optional):
                Any log message with log level greater or equal to this value
                will have information appended to it about the module, function
                and line number, where the log record was made. The suffix will
                have the form ` | {module}.{function}.{line}`.
                Defaults to `logging.WARNING`.
                If `fmt` is passed, this argument will be ignored.
            prepend_level_name (optional):
                If `True`, the log level name will be prepended to every log
                message (but _after_ the `syslog` PRI part). The prefix will
                have the form `{levelname} | ` (with a fixed width of 9
                characters of the part before the `|`).
                Defaults to `True`.
                If `fmt` is passed, this argument will be ignored.
        """
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
