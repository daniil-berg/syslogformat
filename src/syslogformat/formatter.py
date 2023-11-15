"""Definition of the central `SyslogFormatter` class."""

from __future__ import annotations

import re
import sys
from logging import (
    Formatter,
    LogRecord,
    PercentStyle,
    StrFormatStyle,
    StringTemplateStyle,
)
from typing import Dict

from .exceptions import NonStandardSyslogFacility
from .facility import USER
from .helpers import get_syslog_pri_part, normalize_log_level
from .types import (
    AnyMap,
    FormatterKwargs,
    LevelFmtMap,
    Style,
    StyleKey,
    StyleKwargs,
)

__all__ = ["SyslogFormatter"]


LINE_BREAK_PATTERN = re.compile(r"(?:\r\n|\r|\n)\s*")
STYLES_DEFAULT_FORMATS = {
    "%": (PercentStyle, "%(message)s | %(name)s"),
    "{": (StrFormatStyle, "{message} | {name}"),
    "$": (StringTemplateStyle, "${message} | ${name}"),
}


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
        style: StyleKey = "%",
        validate: bool = True,
        *,
        defaults: AnyMap | None = None,
        facility: int = USER,
        line_break_repl: str | None = " --> ",
        level_formats: LevelFmtMap | None = None,
    ) -> None:
        """
        Validates the added formatter constructor arguments.

        For details about the base class' constructor parameters, the official
        [docs](https://docs.python.org/3/library/logging.html#logging.Formatter)
        provide full explanations.

        Args:
            fmt:
                A format string in the given `style` for the logged output as a
                whole. The possible mapping keys are drawn from the
                `logging.LogRecord` object's
                [attributes](https://docs.python.org/3/library/logging.html#logrecord-attributes).

                By default `%(message)s | %(name)s` will be used and passed to
                the parent [`__init__`][logging.Formatter]. If any custom string
                is passed, that string is passed through unchanged to the parent
                [`__init__`][logging.Formatter].
            datefmt:
                Passed through to the parent [`__init__`][logging.Formatter].
            style:
                Passed through to the parent [`__init__`][logging.Formatter].
            validate:
                If `True` (default), incorrect or mismatched `fmt` and `style`
                will raise a `ValueError`; for example,
                `logging.Formatter('%(asctime)s - %(message)s', style='{')`.

                Also, if `True`, a non-standard `facility` value (i.e. not
                between 0 and 24) will raise a
                [`NonStandardSyslogFacility`][syslogformat.exceptions.NonStandardSyslogFacility]
                error. The argument is always passed through to the parent
                [`__init__`][logging.Formatter].
            defaults:
                Passed through to the parent [`__init__`][logging.Formatter]
                on Python `>=3.10`. Ignored on Python `<3.10`.
            facility:
                Used to calculate the number in the PRI part at the very start
                of each log message. This argument should be an integer between
                0 and 24. The `facility` value is multiplied by 8 and added
                to the numerical value of the severity that corresponds to the
                log level of the message.

                Details about accepted numerical values can be found in
                [section 4.1.1](https://datatracker.ietf.org/doc/html/rfc3164#section-4.1.1)
                of RFC 3164.
                Defaults to [`USER`][syslogformat.facility.USER].
            line_break_repl:
                To prevent a single log message taking up more than one line,
                every line-break (and consecutive whitespace) in the final log
                message will be replaced with the string provided here. This is
                useful because log records that include exception information
                for example normally result in the multi-line traceback being
                included in the log message.

                Passing `None` disables this behavior. This means the default
                (multi-line) exception formatting will be used.

                Defaults to `' --> '`.
            level_formats:
                If provided a mapping of log level thresholds to format strings,
                the formatter will prioritize the format with the highest level
                threshold for all log records at or above that level.

                For example, say you pass the following dictionary:
                ```python
                {"WARNING": "foo %(message)s",
                 "ERROR":   "bar %(message)s"}
                ```
                Log records with the level `ERROR` or higher will be formatted
                with the `bar %(message)s` format; records with a level of
                `WARNING` or higher but below `ERROR` will be formatted with the
                `foo %(message)s` format; those with a level below `WARNING`
                will use the normal format provided via the `fmt` argument.

                The order of the provided mapping is irrelevant.
                If such a mapping is passed, the formats _should_ conform to the
                specified `style`, just like the `fmt` argument; if any of them
                does not **and** `validate` is `True`, a `ValueError` is raised.

                If passed `None` (default) or an empty mapping, the formatter
                will use the normal provided `fmt` for all log messages.

        Raises:
            NonStandardSyslogFacility:
                If `validate` was set to `True` and the `facility` passed was
                not an integer between 0 and 23.
            ValueError:
                If `validate` was set to `True` and the provided `fmt` or any of
                the values in the `level_formats` mapping (if provided) do not
                match the specified `style`.
        """
        if validate and facility not in range(24):
            raise NonStandardSyslogFacility(facility)
        self._style_cls, default_format = STYLES_DEFAULT_FORMATS[style]
        if fmt is None:
            fmt = default_format
        self._validate = validate
        self._defaults = defaults
        self._facility = facility
        self._line_break_repl = line_break_repl
        kwargs = FormatterKwargs(
            fmt=fmt,
            datefmt=datefmt,
            style=style,
            validate=validate,
        )
        if sys.version_info >= (3, 10):
            kwargs["defaults"] = defaults
        super().__init__(**kwargs)
        self._level_styles = self._get_level_styles(level_formats or {})

    def _get_style(self, fmt: str) -> Style:
        """Constructs a style instance from a format string."""
        style_kwargs = StyleKwargs(fmt=fmt)
        if sys.version_info >= (3, 10):
            style_kwargs["defaults"] = self._defaults
        style_obj = self._style_cls(**style_kwargs)
        if self._validate:
            style_obj.validate()
        return style_obj

    def _get_level_styles(self, level_formats: LevelFmtMap) -> Dict[int, Style]:
        """Constructs a sorted (desc.) dictionary of level => format style."""
        level_styles = (
            (normalize_log_level(level), self._get_style(level_fmt))
            for level, level_fmt in level_formats.items()
        )
        return dict(sorted(level_styles, reverse=True))

    def formatMessage(self, record: LogRecord) -> str:
        """
        Takes a log record and produces a formatted message from it.

        If different level styles have been set, the one mapped to the highest
        level at or below that of the `record` will be used to format it.

        Otherwise the parent method is called.

        Args:
            record: The log record to format

        Returns:
            The formatted log message as text
        """
        for level_bound, style in self._level_styles.items():
            if record.levelno >= level_bound:
                return style.format(record)
        return super().formatMessage(record)

    def format(self, record: LogRecord) -> str:
        """
        Formats a record to be compliant with syslog PRI (log level/severity).

        Ensures that line-breaks in the exception message are replaced to ensure
        it fits into a single line, unless this behavior was disabled.

        The rest of the logic is the same as in the
        [parent method][logging.Formatter.format].
        The record's attribute dictionary is used as the operand to a string
        formatting operation which yields the returned string. Before formatting
        the dictionary, a couple of preparatory steps are carried out. The
        `message` attribute of the record is computed using
        [LogRecord.getMessage][logging.LogRecord.getMessage]. If the formatting
        string uses the time (as determined by a call to `usesTime`),
        [formatTime][logging.Formatter.formatTime] is called to format the event
        time.
        If there is exception information, it is formatted using
        [formatException][logging.Formatter.formatException] and appended to the
        message.
        If stack information is available, it is appended after the exception
        information, using [formatStack][logging.Formatter.formatStack]
        to transform it if necessary.

        Args:
            record: The [`logging.LogRecord`][] to format as text

        Returns:
            The final log message constructed from the log record
        """
        record.message = record.getMessage()

        # Prepend syslog PRI:
        message = get_syslog_pri_part(record.levelno, self._facility)
        message += self.formatMessage(record)

        # Add exception/stack info:
        if record.exc_info and not record.exc_text:
            record.exc_text = self.formatException(record.exc_info).strip()
        if record.exc_text:
            message += f"\n{record.exc_text}"
        if record.stack_info:
            message += f"\n{self.formatStack(record.stack_info).strip()}"

        # Replace line-breaks, if necessary:
        if self._line_break_repl is None:
            return message
        return re.sub(LINE_BREAK_PATTERN, self._line_break_repl, message)


# We must violate those because they are violated in the base `Formatter` class:
# ruff: noqa: FBT001, FBT002, A003, N802
