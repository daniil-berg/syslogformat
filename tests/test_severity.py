import logging
from unittest.mock import patch

import pytest

from syslogformat import severity


def test_log_level_severity() -> None:
    assert severity.log_level_severity(0) == severity.DEBUG
    assert severity.log_level_severity(logging.DEBUG) == severity.DEBUG
    assert severity.log_level_severity(logging.INFO) == severity.INFORMATIONAL
    assert severity.log_level_severity(logging.WARNING) == severity.WARNING
    assert severity.log_level_severity(logging.ERROR) == severity.ERROR
    assert severity.log_level_severity(logging.CRITICAL) == severity.CRITICAL
    assert severity.log_level_severity(999_999_999) == severity.ALERT

    with patch.object(
        severity,
        "_LOG_LEVEL_BOUND_SEVERITY",
        new=[],
    ), pytest.raises(AssertionError):
        severity.log_level_severity(10)
