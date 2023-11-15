from __future__ import annotations

import re
import sys
from logging import DEBUG, INFO, WARNING, Formatter, LogRecord, PercentStyle
from traceback import format_exc
from types import TracebackType
from typing import Callable, Iterator, Optional, Protocol, Tuple, Type
from unittest.mock import MagicMock, call, patch

import pytest

from syslogformat.formatter import SyslogFormatter

ExcInfo = Tuple[Type[BaseException], BaseException, Optional[TracebackType]]


@patch.object(SyslogFormatter, "_get_level_styles")
@patch.object(Formatter, "__init__")
def test___init__(
    mock_base___init__: MagicMock,
    mock__get_level_styles: MagicMock,
) -> None:
    fmt = "foo"
    datefmt = "bar"
    defaults = {"a": 1}
    facility = 8
    line_break_repl = "###"
    formatter = SyslogFormatter(
        fmt=fmt,
        datefmt=datefmt,
        style="%",
        validate=True,
        defaults=defaults,
        facility=facility,
        line_break_repl=line_break_repl,
        level_formats={WARNING: "test"},
    )
    assert formatter._style_cls is PercentStyle
    assert formatter._validate is True
    assert formatter._facility == facility
    assert formatter._line_break_repl == line_break_repl
    if sys.version_info >= (3, 10):
        mock_base___init__.assert_called_once_with(
            fmt=fmt,
            datefmt=datefmt,
            style="%",
            validate=True,
            defaults=defaults,
        )
    else:
        mock_base___init__.assert_called_once_with(
            fmt=fmt,
            datefmt=datefmt,
            style="%",
            validate=True,
        )
    mock__get_level_styles.assert_called_once_with({WARNING: "test"})
    facility = -1
    with pytest.raises(ValueError):
        SyslogFormatter(facility=facility)
    facility = 25
    with pytest.raises(ValueError):
        SyslogFormatter(facility=facility)
    formatter = SyslogFormatter(validate=False, facility=facility)
    assert formatter._facility == facility


TEST_FACILITY = 10
TEST_PRI = "<42>"


@pytest.fixture
def mock_get_syslog_pri_part() -> Iterator[MagicMock]:
    patcher = patch("syslogformat.formatter.get_syslog_pri_part")
    mock_function = patcher.start()
    mock_function.return_value = TEST_PRI
    yield mock_function
    patcher.stop()


@pytest.fixture
def make_syslog_formatter() -> Callable[[str], SyslogFormatter]:
    def _make_syslog_formatter(line_break_repl: str) -> SyslogFormatter:
        formatter = SyslogFormatter("{message}", style="{")
        formatter._facility = TEST_FACILITY
        formatter._line_break_repl = line_break_repl
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


def test__get_style(
    make_syslog_formatter: Callable[[str], SyslogFormatter],
    make_log_record: LogRecordFixture,
) -> None:
    formatter = make_syslog_formatter("...")
    formatter._defaults = {"foo": "bar"}
    formatter._style_cls = PercentStyle
    formatter._validate = False
    output = formatter._get_style("%(foo)s %(msg)s")
    assert isinstance(output, PercentStyle)

    log_record = make_log_record(DEBUG, "baz")
    if sys.version_info >= (3, 10):
        message = output.format(log_record)
        assert message == "bar baz"
    else:
        log_record.foo = "bla"
        message = output.format(log_record)
        assert message == "bla baz"

    formatter._validate = True
    with pytest.raises(ValueError):
        formatter._get_style("{foo} {msg}")


@patch("syslogformat.formatter.normalize_log_level")
@patch.object(SyslogFormatter, "_get_style")
def test__get_level_styles(
    mock_get_style: MagicMock,
    mock_normalize_log_level: MagicMock,
    make_syslog_formatter: Callable[[str], SyslogFormatter],
) -> None:
    mock_level_1, mock_level_2 = DEBUG, INFO
    mock_normalize_log_level.side_effect = [mock_level_1, mock_level_2]
    mock_style_1, mock_style_2 = object(), object()
    mock_get_style.side_effect = [mock_style_1, mock_style_2]

    formatter = make_syslog_formatter("~")

    key1, key2 = "foo", "bar"
    fmt1, fmt2 = "x", "y"
    output = formatter._get_level_styles({key1: fmt1, key2: fmt2})
    assert output == {mock_level_1: mock_style_1, mock_level_2: mock_style_2}

    assert mock_normalize_log_level.call_args_list == [call(key1), call(key2)]
    assert mock_get_style.call_args_list == [call(fmt1), call(fmt2)]


def test_format_message(
    make_syslog_formatter: Callable[[str], SyslogFormatter],
    make_log_record: LogRecordFixture,
) -> None:
    formatter = make_syslog_formatter("🌐")
    formatter._level_styles = {
        INFO: PercentStyle("%(message)s | %(module)s.%(lineno)d")
    }
    msg = "abc"
    # Record with a level less than INFO:
    log_record = make_log_record(DEBUG, msg)
    log_record.message = log_record.getMessage()
    output = formatter.formatMessage(log_record)
    assert output == msg

    # Record with INFO level:
    log_record = make_log_record(INFO, msg)
    log_record.message = log_record.getMessage()
    output = formatter.formatMessage(log_record)
    assert output == f"{msg} | {log_record.module}.{log_record.lineno}"

    # Record with a level above INFO: (should yield the same output)
    log_record = make_log_record(WARNING, msg)
    log_record.message = log_record.getMessage()
    output = formatter.formatMessage(log_record)
    assert output == f"{msg} | {log_record.module}.{log_record.lineno}"


def test_format__base_case(
    mock_get_syslog_pri_part: MagicMock,
    make_syslog_formatter: Callable[[str], SyslogFormatter],
    make_log_record: LogRecordFixture,
) -> None:
    formatter = make_syslog_formatter("🧵")
    msg = "abc\n  xyz"
    log_record = make_log_record(INFO, msg)

    output = formatter.format(log_record)
    assert output == f"{TEST_PRI}abc🧵xyz"
    mock_get_syslog_pri_part.assert_called_once_with(INFO, TEST_FACILITY)


def test_format__with_exception(
    mock_get_syslog_pri_part: MagicMock,
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
    mock_get_syslog_pri_part.assert_called_once_with(DEBUG, TEST_FACILITY)


def test_format__with_stack_info(
    mock_get_syslog_pri_part: MagicMock,
    make_syslog_formatter: Callable[[str], SyslogFormatter],
    make_log_record: LogRecordFixture,
) -> None:
    formatter = make_syslog_formatter("🧱")
    msg = "abc\n  xyz"
    log_record = make_log_record(DEBUG, msg, sinfo="foo\n  bar\n ")

    output = formatter.format(log_record)
    assert output == f"{TEST_PRI}abc🧱xyz🧱foo🧱bar"
    mock_get_syslog_pri_part.assert_called_once_with(DEBUG, TEST_FACILITY)


def test_format__no_line_break_replacement(
    mock_get_syslog_pri_part: MagicMock,
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
    mock_get_syslog_pri_part.assert_called_once_with(WARNING, TEST_FACILITY)
