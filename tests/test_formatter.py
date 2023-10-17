import logging
from typing import TYPE_CHECKING

from syslogformat.formatter import SyslogFormatter

if TYPE_CHECKING:
    from _pytest.logging import LogCaptureFixture


def test_formatter_default(caplog: "LogCaptureFixture") -> None:
    this_module_function = f"{__name__}.{test_formatter_default.__name__}"
    log = logging.getLogger()
    hdl = logging.StreamHandler()
    fmt = SyslogFormatter()
    hdl.setFormatter(fmt)
    hdl.setLevel(logging.NOTSET)
    log.addHandler(hdl)
    log.setLevel(logging.NOTSET)

    log.debug("foo")
    log.info("bar")
    log.warning("baz")
    try:
        raise ValueError("this is bad")
    except ValueError:
        log.exception("oh no")

    output_lines = caplog.text.splitlines()
    assert output_lines[0] == "<15>DEBUG    | foo"
    assert output_lines[1] == "<14>INFO     | bar"
    assert output_lines[2] == f"<12>WARNING  | baz | {this_module_function}.22"
    assert output_lines[3].startswith(
        f"<11>ERROR    | oh no | {this_module_function}.26 | "
    )
    assert output_lines[3].endswith("ValueError: this is bad'")
