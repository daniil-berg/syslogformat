import logging
import logging.config
from io import StringIO
from pathlib import Path
from typing import Any, Dict

from syslogformat import SyslogFormatter

THIS_MODULE = Path(__file__).stem

log = logging.getLogger()


def test_formatter_default() -> None:
    log_stream = StringIO()
    stream_handler = logging.StreamHandler(stream=log_stream)
    syslog_formatter = SyslogFormatter()
    stream_handler.setFormatter(syslog_formatter)
    stream_handler.setLevel(logging.NOTSET)
    log.addHandler(stream_handler)
    log.setLevel(logging.NOTSET)

    log.debug("foo")
    log.info("bar")
    log.warning("baz")
    try:
        raise ValueError("this is bad")
    except ValueError:
        log.exception("oof")

    output_lines = log_stream.getvalue().splitlines()
    assert output_lines[0] == "<15>foo | root"
    assert output_lines[1] == "<14>bar | root"
    assert output_lines[2] == "<12>baz | root"
    assert output_lines[3].startswith("<11>oof | root --> ")
    assert "Traceback" in output_lines[3]
    assert output_lines[3].endswith(" --> ValueError: this is bad")


def test_formatter_with_config() -> None:
    facility = 16
    log_stream = StringIO()
    log_config: Dict[str, Any] = {
        "version": 1,
        "formatters": {
            "syslog_test": {
                "()": "syslogformat.SyslogFormatter",
                "fmt": "{message}",
                "style": "{",
                "facility": facility,
                "line_break_repl": "🤡",
                "level_formats": {
                    "WARNING": "{message} | {module}",
                    "ERROR": "{message} | {module}.{lineno}",
                },
            }
        },
        "handlers": {
            "stdout_syslog": {
                "class": "logging.StreamHandler",
                "formatter": "syslog_test",
                "stream": log_stream,
            }
        },
        "root": {"handlers": ["stdout_syslog"], "level": "DEBUG"},
    }
    logging.config.dictConfig(log_config)

    log.debug("foo")
    log.info("bar")
    log.warning("baz")
    try:
        raise ValueError("this is bad")
    except ValueError:
        log.exception("oh no")

    output_lines = log_stream.getvalue().splitlines()
    fac = facility * 8
    assert output_lines[0] == f"<{fac + 7}>foo"
    assert output_lines[1] == f"<{fac + 6}>bar"
    assert output_lines[2] == f"<{fac + 4}>baz | {THIS_MODULE}"
    assert output_lines[3].startswith(f"<{fac + 3}>oh no | {THIS_MODULE}.75🤡")
    assert "Traceback" in output_lines[3]
    assert output_lines[3].endswith("🤡ValueError: this is bad")
