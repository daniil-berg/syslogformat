import re
from logging import DEBUG, INFO, WARNING, Formatter, LogRecord
from traceback import format_exc
from types import TracebackType
from typing import Callable, Optional, Protocol, Tuple, Type
from unittest.mock import MagicMock, patch

import pytest

from syslogformat.formatter import SyslogFormatter

ExcInfo = Tuple[Type[BaseException], BaseException, Optional[TracebackType]]


@patch.object(Formatter, "__init__")
def test___init__(mock_base___init__: MagicMock) -> None:
    facility = 8
    detail_threshold = 10
    formatter = SyslogFormatter(
        fmt="foo",
        datefmt="bar",
        style="$",
        validate=True,
        defaults={"a": 1},
        facility=facility,
        line_break_repl=" ",
        detail_threshold=detail_threshold,
        prepend_level_name=False,
    )
    assert formatter._facility == facility
    assert formatter._line_break_repl == " "
    assert formatter._detail_threshold == detail_threshold
    assert formatter._prepend_level_name is False
    assert formatter._custom_fmt is True
    mock_base___init__.assert_called_once_with(
        fmt="foo",
        datefmt="bar",
        style="$",
        validate=True,
        defaults={"a": 1},
    )
    facility = -1
    with pytest.raises(ValueError):
        SyslogFormatter(facility=facility)
    facility = 25
    with pytest.raises(ValueError):
        SyslogFormatter(facility=facility)
    formatter = SyslogFormatter(validate=False, facility=facility)
    assert formatter._facility == facility
    assert formatter._custom_fmt is False


TEST_FACILITY_VALUE = 10
TEST_SEVERITY_VALUE = 1
TEST_PRI = f"<{TEST_FACILITY_VALUE * 8 + TEST_SEVERITY_VALUE}>"


@pytest.fixture
def mock_log_level_severity() -> MagicMock:
    patcher = patch("syslogformat.formatter.log_level_severity")
    mock_function = patcher.start()
    mock_function.return_value = TEST_SEVERITY_VALUE
    yield mock_function
    patcher.stop()


@pytest.fixture
def make_syslog_formatter() -> Callable[[str], SyslogFormatter]:
    def _make_syslog_formatter(line_break_repl: str) -> SyslogFormatter:
        formatter = SyslogFormatter()
        formatter._facility = TEST_FACILITY_VALUE
        formatter._line_break_repl = line_break_repl
        formatter._detail_threshold = WARNING
        formatter._prepend_level_name = False
        formatter._custom_fmt = False
        return formatter

    return _make_syslog_formatter


class LogRecordFixture(Protocol):
    def __call__(
        self,
        level: int,
        msg: str,
        exc_info: ExcInfo | None = None,
        sinfo: str | None = None,
    ) -> LogRecord:
        ...


@pytest.fixture
def make_log_record() -> LogRecordFixture:
    def _make_log_record(
        level: int,
        msg: str,
        exc_info: ExcInfo | None = None,
        sinfo: str | None = None,
    ) -> LogRecord:
        return LogRecord(
            "test",
            level,
            __file__,
            0,
            msg,
            None,
            exc_info,
            func="f",
            sinfo=sinfo,
        )

    return _make_log_record


@pytest.fixture
def exc_info_and_text() -> Tuple[ExcInfo, str]:
    try:
        raise ValueError("foo")
    except Exception as e:
        return (type(e), e, e.__traceback__), format_exc().strip()


def test_format__base_case(
    mock_log_level_severity: MagicMock,
    make_syslog_formatter: Callable[[str], SyslogFormatter],
    make_log_record: LogRecordFixture,
) -> None:
    formatter = make_syslog_formatter("🧵")
    msg = "abc\n  xyz"
    log_record = make_log_record(INFO, msg)

    output = formatter.format(log_record)
    assert output == f"{TEST_PRI}abc🧵xyz"
    mock_log_level_severity.assert_called_once_with(INFO)


def test_format__threshold_exceeded(
    mock_log_level_severity: MagicMock,
    make_syslog_formatter: Callable[[str], SyslogFormatter],
    make_log_record: LogRecordFixture,
) -> None:
    formatter = make_syslog_formatter("🌐")
    msg = "abc\n  xyz"
    log_record = make_log_record(INFO, msg)
    formatter._detail_threshold = INFO
    detail = f"{log_record.module}.{log_record.funcName}.{log_record.lineno}"

    output = formatter.format(log_record)
    assert output == f"{TEST_PRI}abc🌐xyz | {detail}"
    mock_log_level_severity.assert_called_once_with(INFO)


def test_format__prepend_level_name(
    mock_log_level_severity: MagicMock,
    make_syslog_formatter: Callable[[str], SyslogFormatter],
    make_log_record: LogRecordFixture,
) -> None:
    formatter = make_syslog_formatter("💡")
    msg = "abc\n  xyz"
    log_record = make_log_record(INFO, msg)
    formatter._prepend_level_name = True

    output = formatter.format(log_record)
    assert output == f"{TEST_PRI}INFO    | abc💡xyz"
    mock_log_level_severity.assert_called_once_with(INFO)
    mock_log_level_severity.reset_mock()

    # Check that spacing for level name prefix is fixed:
    log_record = make_log_record(DEBUG, msg)

    output = formatter.format(log_record)
    assert output == f"{TEST_PRI}DEBUG   | abc💡xyz"
    mock_log_level_severity.assert_called_once_with(DEBUG)


def test_format__with_exception(
    mock_log_level_severity: MagicMock,
    make_syslog_formatter: Callable[[str], SyslogFormatter],
    make_log_record: LogRecordFixture,
    exc_info_and_text: Tuple[ExcInfo, str],
) -> None:
    exc_info, exc_text = exc_info_and_text
    formatter = make_syslog_formatter("💥")
    exc_text_fmt = re.sub(r"(?:\r\n|\r|\n)\s*", "💥", exc_text)
    msg = "abc\n  xyz"
    log_record = make_log_record(DEBUG, msg, exc_info=exc_info)

    output = formatter.format(log_record)
    assert output == f"{TEST_PRI}abc💥xyz💥{exc_text_fmt}"
    assert log_record.exc_text == exc_text
    mock_log_level_severity.assert_called_once_with(DEBUG)
    mock_log_level_severity.reset_mock()

    # Check that detail comes before exception text:
    formatter._prepend_level_name = False
    formatter._detail_threshold = DEBUG
    detail = f"{log_record.module}.{log_record.funcName}.{log_record.lineno}"

    output = formatter.format(log_record)
    assert output == f"{TEST_PRI}abc💥xyz | {detail}💥{exc_text_fmt}"
    mock_log_level_severity.assert_called_once_with(DEBUG)


def test_format__custom_formatting_override(
    mock_log_level_severity: MagicMock,
    make_syslog_formatter: Callable[[str], SyslogFormatter],
    make_log_record: LogRecordFixture,
    exc_info_and_text: Tuple[ExcInfo, str],
) -> None:
    exc_info, exc_text = exc_info_and_text
    formatter = make_syslog_formatter("🧱")
    formatter._custom_fmt = True
    formatter._prepend_level_name = True
    formatter._detail_threshold = WARNING
    exc_text_fmt = re.sub(r"(?:\r\n|\r|\n)\s*", "🧱", exc_text)
    msg = "abc\n  xyz"
    log_record = make_log_record(WARNING, msg, exc_info=exc_info)

    output = formatter.format(log_record)
    assert output == f"{TEST_PRI}abc🧱xyz🧱{exc_text_fmt}"
    mock_log_level_severity.assert_called_once_with(WARNING)


def test_format__with_stack_info(
    mock_log_level_severity: MagicMock,
    make_syslog_formatter: Callable[[str], SyslogFormatter],
    make_log_record: LogRecordFixture,
) -> None:
    formatter = make_syslog_formatter("💥")
    msg = "abc\n  xyz"
    log_record = make_log_record(DEBUG, msg, sinfo="foo\n  bar\n ")

    output = formatter.format(log_record)
    assert output == f"{TEST_PRI}abc💥xyz💥foo💥bar"
    mock_log_level_severity.assert_called_once_with(DEBUG)


def test_format__no_line_break_replacement(
    mock_log_level_severity: MagicMock,
    make_syslog_formatter: Callable[[str], SyslogFormatter],
    make_log_record: LogRecordFixture,
    exc_info_and_text: Tuple[ExcInfo, str],
) -> None:
    exc_info, exc_text = exc_info_and_text
    formatter = make_syslog_formatter("🧵")
    formatter._line_break_repl = None
    msg = "abc\n  xyz"
    log_record = make_log_record(WARNING, msg, exc_info=exc_info)

    output = formatter.format(log_record)
    assert "🧵" not in output
    assert "\n" in output
    assert output.startswith(TEST_PRI + msg)
    assert output.endswith(exc_text)
    mock_log_level_severity.assert_called_once_with(WARNING)
