import re
from logging import DEBUG, INFO, WARNING, Formatter, LogRecord
from traceback import format_exc
from unittest.mock import MagicMock, patch

import pytest

from syslogformat.formatter import SyslogFormatter


@patch.object(Formatter, "__init__")
def test___init__(mock_base___init__: MagicMock) -> None:
    formatter = SyslogFormatter(
        fmt="foo",
        datefmt="bar",
        style="$",
        validate=True,
        defaults={"a": 1},
        facility=8,
        line_break_repl=" ",
        detail_threshold=10,
        prepend_level_name=False,
    )
    assert formatter._facility == 8
    assert formatter._line_break_repl == " "
    assert formatter._detail_threshold == 10
    assert formatter._prepend_level_name is False
    assert formatter._custom_fmt is True
    mock_base___init__.assert_called_once_with(
        fmt="foo",
        datefmt="bar",
        style="$",
        validate=True,
        defaults={"a": 1},
    )
    with pytest.raises(ValueError):
        SyslogFormatter(facility=-1)
    with pytest.raises(ValueError):
        SyslogFormatter(facility=25)
    formatter = SyslogFormatter(validate=False, facility=25)
    assert formatter._facility == 25
    assert formatter._custom_fmt is False


@patch("syslogformat.formatter.log_level_severity")
def test_format(mock_log_level_severity: MagicMock) -> None:
    mock_log_level_severity.return_value = severity = 0

    formatter = SyslogFormatter()
    formatter._facility = facility = 10
    formatter._line_break_repl = "🧵"
    formatter._detail_threshold = WARNING
    formatter._prepend_level_name = False
    formatter._custom_fmt = False
    msg = "abc\n  xyz"

    # Base case:
    log_record = LogRecord("test", INFO, __file__, 0, msg, None, None, "f")
    pri = f"<{facility * 8 + severity}>"
    output = formatter.format(log_record)
    assert output == f"{pri}abc🧵xyz"
    mock_log_level_severity.assert_called_once_with(INFO)
    mock_log_level_severity.reset_mock()

    # Should append expected additional details:
    formatter._detail_threshold = INFO
    detail = f"{log_record.module}.{log_record.funcName}.{log_record.lineno}"
    output = formatter.format(log_record)
    assert output == f"{pri}abc🧵xyz | {detail}"
    mock_log_level_severity.assert_called_once_with(INFO)
    mock_log_level_severity.reset_mock()

    # Should prepend level name:
    formatter._prepend_level_name = True
    level_prefix = "INFO    "
    output = formatter.format(log_record)
    assert output == f"{pri}{level_prefix}| abc🧵xyz | {detail}"
    mock_log_level_severity.assert_called_once_with(INFO)
    mock_log_level_severity.reset_mock()

    # Check that spacing for level name prefix is fixed:
    log_record = LogRecord("test", DEBUG, __file__, 0, msg, None, None, "f")
    level_prefix = "DEBUG   "
    output = formatter.format(log_record)
    assert output == f"{pri}{level_prefix}| abc🧵xyz"
    mock_log_level_severity.assert_called_once_with(DEBUG)
    mock_log_level_severity.reset_mock()

    # Check that exception info is also reformatted and appended:
    try:
        raise ValueError("foo")
    except Exception as e:
        exc_info = type(e), e, e.__traceback__
        exc_text = format_exc().strip()
    log_record = LogRecord("test", DEBUG, __file__, 0, msg, None, exc_info)
    detail = f"{log_record.module}.{log_record.funcName}.{log_record.lineno}"
    exc_text_fmt = re.sub(r"(?:\r\n|\r|\n)\s*", "🧵", exc_text)
    output = formatter.format(log_record)
    assert output == f"{pri}{level_prefix}| abc🧵xyz🧵{exc_text_fmt}"
    assert log_record.exc_text == exc_text
    mock_log_level_severity.assert_called_once_with(DEBUG)
    mock_log_level_severity.reset_mock()

    # Check that detail comes before exception text:
    formatter._prepend_level_name = False
    formatter._detail_threshold = DEBUG
    output = formatter.format(log_record)
    assert output == f"{pri}abc🧵xyz | {detail}🧵{exc_text_fmt}"
    mock_log_level_severity.assert_called_once_with(DEBUG)
    mock_log_level_severity.reset_mock()

    # With custom formatting enabled, check that no details are appended and no
    # level name is prepended, but exception text is still appended:
    formatter._custom_fmt = True
    formatter._prepend_level_name = True
    output = formatter.format(log_record)
    assert output == f"{pri}abc🧵xyz🧵{exc_text_fmt}"
    mock_log_level_severity.assert_called_once_with(DEBUG)
    mock_log_level_severity.reset_mock()

    # Disable line-break replacement:
    formatter._line_break_repl = None
    output = formatter.format(log_record)
    assert "🧵" not in output
    assert "\n" in output
    assert output.startswith(pri)
    assert output.endswith(exc_text)
    mock_log_level_severity.assert_called_once_with(DEBUG)
    mock_log_level_severity.reset_mock()
