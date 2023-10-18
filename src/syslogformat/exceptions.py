"""Exception classes specific to `syslogformat`."""


class SyslogFormatError(Exception):
    """Base class for all exceptions in the `syslogformat` package."""


class NonStandardSyslogFacility(ValueError, SyslogFormatError):
    """Used when a `syslog` facility code does not pass standard validation."""

    def __init__(self, facility: int) -> None:
        """Initialized with the wrong `facility` code that was used."""
        super().__init__(f"Syslog facility code invalid: {facility}")


class CodeShouldBeUnreachable(AssertionError, SyslogFormatError):
    """Convenience for marking lines of code as presumably unreachable."""