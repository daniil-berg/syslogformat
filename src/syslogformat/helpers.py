"""A few helper functions for dealing with log levels, severities and so on."""

from logging import getLevelNamesMapping

from .exceptions import InvalidLogLevelThreshold
from .facility import USER
from .severity import log_level_severity


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
        `InvalidLogLevelThreshold`:
            If `level` is a string that is not present in the keys of the
            level-name-mapping of the `logging` module.
    """
    if isinstance(level, int):
        return level
    level_num = getLevelNamesMapping().get(level)
    if level_num is None:
        raise InvalidLogLevelThreshold(level)
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
            be determined and used to calculate the PRI value.
        facility (optional):
            The `syslog` facility code.
            Defaults to `syslogformat.facility.USER`.

    Returns:
        A string of the PRI value enclosed in angle brackets.
    """
    return f"<{facility * 8 + log_level_severity(log_level)}>"
