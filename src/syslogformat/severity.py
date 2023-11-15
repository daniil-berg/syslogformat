"""
Numerical codes for `syslog` severities.

These constants in this module correspond to those defined in section 4.1.1 of
[RFC 3164](https://datatracker.ietf.org/doc/html/rfc3164#section-4.1.1).
"""

import logging
from math import inf
from typing import Tuple

from .exceptions import CodeShouldBeUnreachable

__all__ = [
    "ALERT",
    "CRITICAL",
    "DEBUG",
    "EMERGENCY",
    "ERROR",
    "INFORMATIONAL",
    "NOTICE",
    "WARNING",
    "log_level_severity",
]

EMERGENCY = 0
"""System is unusable"""

ALERT = 1
"""Action must be taken immediately"""

CRITICAL = 2
"""Critical conditions"""

ERROR = 3
"""Error conditions"""

WARNING = 4
"""Warning conditions"""

NOTICE = 5
"""Normal but significant condition"""

INFORMATIONAL = 6
"""Informational messages"""

DEBUG = 7
"""Debug-level messages"""


_LOG_LEVEL_BOUND_SEVERITY: Tuple[Tuple[float, int], ...] = (
    (logging.DEBUG, DEBUG),
    (logging.INFO, INFORMATIONAL),
    (logging.WARNING, WARNING),
    (logging.ERROR, ERROR),
    (logging.CRITICAL, CRITICAL),
    (inf, ALERT),
)


def log_level_severity(level_num: int) -> int:
    """
    Returns corresponding the `syslog` severity for a given Python log level.

    Details about the meaning of the numerical severity values can be found in
    [section 4.1.1](https://datatracker.ietf.org/doc/html/rfc3164#section-4.1.1)
    of RFC 3164.
    Even though there are more codes available to syslog, the
    [`EMERGENCY`][syslogformat.severity.EMERGENCY] and
    [`NOTICE`][syslogformat.severity.NOTICE] codes are never returned here,
    i.e. it goes straight from
    [`INFORMATIONAL`][syslogformat.severity.INFORMATIONAL] to
    [`WARNING`][syslogformat.severity.WARNING] because there is no
    equivalent log level in the Python logging module to `NOTICE`, and
    `EMERGENCY` is unnecessary because no Python script should be able to cause
    such severe problems.
    Therefore any number above [logging.CRITICAL][] passed will result in
    [`ALERT`][syslogformat.severity.ALERT] being returned.

    Args:
        level_num: An integer representing a Python log level number

    Returns:
        One of the predefined severity codes that matches the given log level

    Examples:
        >>> import logging
        >>> log_level_severity(logging.DEBUG)
        7
        >>> log_level_severity(logging.CRITICAL)
        2
        >>> log_level_severity(logging.CRITICAL + 1)
        1
        >>> log_level_severity(999_999)
        1
    """
    for level_bound, severity in _LOG_LEVEL_BOUND_SEVERITY:
        if level_num <= level_bound:
            return severity
    raise CodeShouldBeUnreachable
