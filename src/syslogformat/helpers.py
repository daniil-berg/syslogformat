"""A few helper functions for dealing with log levels, severities and so on."""

from __future__ import annotations

import logging
import sys
from typing import Dict

from .exceptions import InvalidLogLevel
from .facility import USER
from .severity import log_level_severity


def _get_level_name_mapping() -> Dict[str, int]:
    """Hack duplicating `logging.getLevelNamesMapping` for Python `<3.11`."""
    return logging._nameToLevel.copy()


get_level_name_mapping = _get_level_name_mapping
if sys.version_info >= (3, 11):
    get_level_name_mapping = logging.getLevelNamesMapping


def normalize_log_level(level: int | str) -> int:
    """
    Returns an integer that can be interpreted as a log level number.

    Args:
        level:
            If passed an integer, that value is returned unchanged.
            If passed a string, the corresponding level number is looked up in
            the level-name-mapping of the `logging` module; if the name is not
            found, an error is raised. Otherwise its level number is returned.

    Returns:
        Valid log level number.

    Raises:
        InvalidLogLevel:
            If `level` is a string that is not present in the keys of the
            level-name-mapping of the `logging` module.

    Examples:
        >>> normalize_log_level(42)
        42
        >>> normalize_log_level("WARNING")
        30
    """
    if isinstance(level, int):
        return level
    level_num = get_level_name_mapping().get(level.upper())
    if level_num is None:
        raise InvalidLogLevel(level)
    return level_num


def get_syslog_pri_part(log_level: int, facility: int = USER) -> str:
    """
    Returns a `syslog` PRI prefix from the provided log level and facility.

    See the relevant section of
    [RFC 3164](https://datatracker.ietf.org/doc/html/rfc3164#section-4.1)
    for details about `syslog` standard.

    Args:
        log_level:
            A **Python** log level number. The corresponding severity value will
            be determined via the
            [`log_level_severity`][syslogformat.severity.log_level_severity]
            function and used to calculate the PRI value.
        facility:
            The `syslog` facility code.
            Defaults to `syslogformat.facility.USER`.

    Returns:
        A string of the PRI value enclosed in angle brackets.

    Examples:
        >>> import logging
        >>> get_syslog_pri_part(logging.INFO)
        <14>
        >>> from syslogformat.facility import KERNEL
        >>> get_syslog_pri_part(logging.DEBUG, KERNEL)
        <7>
    """
    return f"<{facility * 8 + log_level_severity(log_level)}>"
