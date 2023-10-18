"""
Numerical codes for `syslog` severities.

These constants in this module correspond to those defined in section 4.1.1 of
[RFC 3164](https://datatracker.ietf.org/doc/html/rfc3164#section-4.1.1).
"""

import logging
import syslog
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
    "LOG_LEVEL_BOUND_SEVERITY",
    "NOTICE",
    "WARNING",
    "log_level_severity",
]

EMERGENCY = syslog.LOG_EMERG
ALERT = syslog.LOG_ALERT
CRITICAL = syslog.LOG_CRIT
ERROR = syslog.LOG_ERR
WARNING = syslog.LOG_WARNING
NOTICE = syslog.LOG_NOTICE
INFORMATIONAL = syslog.LOG_INFO
DEBUG = syslog.LOG_DEBUG


LOG_LEVEL_BOUND_SEVERITY: Tuple[Tuple[float, int], ...] = (
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
    Even though there are more codes available to syslog, the `EMERGENCY` (0)
    and `NOTICE` (5) codes are never returned here, i.e. it goes straight from
    `INFO` (6) to `WARNING` (4) because there is no equivalent log level in the
    Python logging module to `NOTICE`, and `EMERGENCY` is unnecessary because no
    Python script should be able to cause such severe problems.
    """
    for level_bound, severity in LOG_LEVEL_BOUND_SEVERITY:
        if level_num <= level_bound:
            return severity
    raise CodeShouldBeUnreachable
