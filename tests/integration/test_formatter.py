import logging
from io import StringIO
from pathlib import Path

from syslogformat.formatter import SyslogFormatter


def test_formatter_default() -> None:
    this_module = Path(__file__).stem
    this_module_function = f"{this_module}.{test_formatter_default.__name__}"
    log = logging.getLogger()
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
    assert output_lines[2] == f"<12>WARNING | baz | {this_module_function}.22"
    assert output_lines[3].startswith(
        f"<11>ERROR   | oh no | {this_module_function}.26 --> "
    )
    assert output_lines[3].endswith(" --> ValueError: this is bad")
