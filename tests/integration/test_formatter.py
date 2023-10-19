import logging
import logging.config
from io import StringIO
from pathlib import Path
from typing import Any, Dict

from syslogformat import SyslogFormatter

THIS_MODULE = Path(__file__).stem

log = logging.getLogger()


def test_formatter_default() -> None:
    module_function = f"{THIS_MODULE}.{test_formatter_default.__name__}"
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
        log.exception("oh no")

    output_lines = log_stream.getvalue().splitlines()
    assert output_lines[0] == "<15>DEBUG   | foo"
    assert output_lines[1] == "<14>INFO    | bar"
    assert output_lines[2] == f"<12>WARNING | baz | {module_function}.26"
    assert output_lines[3].startswith(
        f"<11>ERROR   | oh no | {module_function}.30 --> "
    )
    assert "Traceback" in output_lines[3]
    assert output_lines[3].endswith(" --> ValueError: this is bad")


def test_formatter_with_config() -> None:
    module_function = f"{THIS_MODULE}.{test_formatter_with_config.__name__}"
    facility = 16
    log_stream = StringIO()
    log_config: Dict[str, Any] = {
        "version": 1,
        "formatters": {
            "syslog_test": {
                "()": "syslogformat.SyslogFormatter",
                "facility": facility,
                "line_break_repl": "🤡",
                "detail_threshold": "INFO",
                "prepend_level_name": False,
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
    assert output_lines[0] == f"<{facility * 8 + 7}>foo"
    assert output_lines[1] == f"<{facility * 8 + 6}>bar | {module_function}.70"
    assert output_lines[2] == f"<{facility * 8 + 4}>baz | {module_function}.71"
    assert output_lines[3].startswith(
        f"<{facility * 8 + 3}>oh no | {module_function}.75🤡"
    )
    assert "Traceback" in output_lines[3]
    assert output_lines[3].endswith("🤡ValueError: this is bad")

    # Now with a custom format override:
    log_stream.seek(0)
    log_config["formatters"]["syslog_test"][
        "format"
    ] = "%(message)s🤡%(levelname)s"
    logging.config.dictConfig(log_config)

    log.debug("foo")
    log.info("bar")
    log.warning("baz")
    try:
        raise ValueError("this is bad")
    except ValueError:
        log.exception("oh no")

    output_lines = log_stream.getvalue().splitlines()
    assert output_lines[0] == f"<{facility * 8 + 7}>foo🤡DEBUG"
    assert output_lines[1] == f"<{facility * 8 + 6}>bar🤡INFO"
    assert output_lines[2] == f"<{facility * 8 + 4}>baz🤡WARNING"
    assert output_lines[3].startswith(f"<{facility * 8 + 3}>oh no🤡ERROR🤡")
    assert "Traceback" in output_lines[3]
    assert output_lines[3].endswith("🤡ValueError: this is bad")
