from logging import CRITICAL, DEBUG
from unittest.mock import MagicMock, patch

import pytest

from syslogformat import helpers
from syslogformat.exceptions import InvalidLogLevel


def test__get_level_name_mapping() -> None:
    mock_name_to_level_map = {"foo": 1, "bar": 2}
    with patch("logging._nameToLevel", new=mock_name_to_level_map):
        assert helpers._get_level_name_mapping() == mock_name_to_level_map
        assert helpers._get_level_name_mapping() is not mock_name_to_level_map


def test_normalize_log_level() -> None:
    assert helpers.normalize_log_level(1) == 1
    assert helpers.normalize_log_level(1000) == 1000  # noqa: PLR2004
    assert helpers.normalize_log_level(-1000) == -1000  # noqa: PLR2004
    assert helpers.normalize_log_level("DEBUG") == DEBUG
    assert helpers.normalize_log_level("CRITICAL") == CRITICAL
    with pytest.raises(InvalidLogLevel) as exc_info:
        helpers.normalize_log_level("💩")
    assert exc_info.match("💩")


@patch.object(helpers, "log_level_severity")
def test_get_syslog_pri_part(mock_log_level_severity: MagicMock) -> None:
    mock_log_level_severity.return_value = mock_severity = 69
    test_level = 15
    test_facility = 420
    expected_pri = test_facility * 8 + mock_severity
    output = helpers.get_syslog_pri_part(test_level, test_facility)
    assert output == f"<{expected_pri}>"
    mock_log_level_severity.assert_called_once_with(test_level)
