"""Definition of the central `SyslogFormatter` class."""

from __future__ import annotations

import re
from logging import WARNING, Formatter, LogRecord
from types import TracebackType
from typing import TYPE_CHECKING, Any, Mapping, Optional, Tuple, Type

from .exceptions import NonStandardSyslogFacility
from .facility import USER
from .severity import log_level_severity

if TYPE_CHECKING:
    from typing_extensions import Literal

__all__ = ["SyslogFormatter"]

ExcInfo = Tuple[Type[BaseException], BaseException, Optional[TracebackType]]

LINE_BREAK_PATTERN = re.compile(r"(?:\r\n|\r|\n)\s*")
DEFAULT_LINE_BREAK_REPL = " --> "


class SyslogFormatter(Formatter):
    """
    Log formatter class for `syslog`-style log messages.

    It ensures that a `syslog` PRI part is prepended to every log message.
    The PRI code is calculated as the facility value (provided in the
    constructor) multiplied by 8 plus the severity value, which is derived from
    the level of each log record.
    See the relevant section of
    [RFC 3164](https://datatracker.ietf.org/doc/html/rfc3164#section-4.1)
    for details about `syslog` standard.

    The formatter is also equipped by default to format log messages into
    one-liners, such that for example exception messages and stack traces
    included in a log record do not result in the message spanning multiple
    lines in the final output.

    It also makes it possible to automatically append additional details to a
    log message, if the log record exceeds a specified level.
    """

    def __init__(  # noqa: PLR0913
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        style: Literal["%", "{", "$"] = "%",
        validate: bool = True,
        *,
        defaults: Mapping[str, Any] | None = None,
        facility: int = USER,
        line_break_repl: str | None = DEFAULT_LINE_BREAK_REPL,
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
                `logging.LogRecord` object's
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
            line_break_repl (optional):
                To prevent a single log message taking up more than one line,
                every line-break (and consecutive whitespace) in the final log
                message will be replaced with the string provided here. This is
                useful because log records that include exception information
                for example normally result in the multi-line traceback being
                included in the log message.
                Passing `None` disables this behavior. This means the default
                (multi-line) exception formatting will be used.
                Defaults to `syslogformat.formatter.DEFAULT_LINE_BREAK_REPL`.
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
        if validate and facility not in range(24):
            raise NonStandardSyslogFacility(facility)
        self._facility = facility
        self._line_break_repl = line_break_repl
        self._detail_threshold = detail_threshold
        self._prepend_level_name = prepend_level_name
        self._custom_fmt = fmt is not None
        super().__init__(
            fmt=fmt,
            datefmt=datefmt,
            style=style,
            validate=validate,
            defaults=defaults,
        )

    def format(self, record: LogRecord) -> str:
        """
        Formats a record to be compliant with syslog PRI (log level/severity).

        Ensures that line-breaks in the exception message are replaced to ensure
        it fits into a single line, unless this behavior was disabled.

        Depending on the constructor arguments used when creating the instance,
        additional information may be added to the message.
        """
        record.message = record.getMessage()

        # Prepend syslog PRI:
        severity = log_level_severity(record.levelno)
        message = f"<{self._facility * 8 + severity}>"
        if not self._custom_fmt and self._prepend_level_name:
            message += f"{record.levelname:<8}| "
        message += self.formatMessage(record)

        # If record level exceeds the threshold, append additional details
        if not self._custom_fmt and record.levelno >= self._detail_threshold:
            message += f" | {record.module}.{record.funcName}.{record.lineno}"

        # Add exception/stack info:
        if record.exc_info and not record.exc_text:
            record.exc_text = self.formatException(record.exc_info).strip()
        if record.exc_text:
            message += f"\n{record.exc_text}"
        if record.stack_info:
            message += f"\n{self.formatStack(record.stack_info)}"

        # Replace line-breaks, if necessary:
        if self._line_break_repl is None:
            return message
        return re.sub(LINE_BREAK_PATTERN, self._line_break_repl, message)


# We must violate those because they are violated in the base `Formatter` class:
# ruff: noqa: FBT001, FBT002, A003
