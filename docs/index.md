# syslogformat

**Python [`logging.Formatter`][1] class for [syslog][2] style messages**

[![GitHub last commit][github-last-commit-img]][github-last-commit]
[![License: Apache-2.0][apache2-img]][apache2]
[![PyPI version][pypi-latest-version-img]][pypi-latest-version]

[📑 Documentation][3] &nbsp; | &nbsp; [🧑‍💻 Source Code][4] &nbsp; | &nbsp; [🐛 Bug Tracker][5]

## Installation

`pip install syslogformat`

## Usage

### Basic configuration

As is the case with any logging formatter setup, you need to use the special `()` key to indicate the custom class to use.
(See the [Dictionary Schema Details][6] and [User-defined objects][7] sections in the official `logging.config` documentation.)

For example, you could use the following config dictionary, pass it to the [`logging.config.dictConfig`][8] function, and start logging like this:

```python hl_lines="7"
import logging.config

log_config = {
    "version": 1,
    "formatters": {
        "my_syslog_formatter": {
            "()": "syslogformat.SyslogFormatter",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "my_syslog_formatter",
            "stream": "ext://sys.stdout",
        }
    },
    "root": {"handlers": ["console"], "level": "DEBUG"},
}
logging.config.dictConfig(log_config)

logging.debug("foo")
logging.info("bar")
logging.warning("baz")
try:
    raise ValueError("this is bad")
except ValueError as e:
    logging.exception("oof")
```

This will send the following to your stdout:

```
<15>foo | root
<14>bar | root
<12>baz | root
<11>oof | root --> Traceback (most recent call last): --> File "/path/to/module.py", line 26, in <module> --> raise ValueError("this is bad") --> ValueError: this is bad
```

### The `PRI` prefix

To adhere to the `syslog` standard outlined in RFC 3164, every log message must begin with the so called [`PRI` part][9].
This is a code enclosed in angle brackets that indicates the **facility** generating the message and **severity** of the event.
The facility is encoded as an integer between 0 and 23 and the severity is encoded as an integer between 0 and 7.
The `PRI` code is calculated by multiplying the facility by 8 and adding the severity.

Programs like **`systemd-journald`** hide the `PRI` part in their output, but interpret it behind the scenes to allow things like highlighting messages of a certain level a different color and filtering by severity.

By default the facility code `1` is used, which indicates user-level messages, but this can be easily configured (see below).
Since a `DEBUG` log message corresponds to a severity of `7`, the resulting `PRI` part of the first log message in the example above is `<15>` (since `1 * 8 + 7 == 15`).
An `ERROR` has the severity `3`, so that message has the `PRI` part `<11>`.

### Default message format

By default the message format of the `SyslogFormatter` is `%(message)s | %(name)s` (and equivalent for `$` or `{` [styles][10]).

In addition, all line-breaks (including those in the exception traceback) are replaced with ` --> ` by default.

All of this can be easily changed and configured to fit your needs (see below).

### Configuration options

In addition to the usual [formatter options][11], the `SyslogFormatter` provides the following parameters:

| Parameter         | Description                                                                                                                                                                            | Default |
|-------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-------:|
| `facility`        | The facility value to use for every log message                                                                                                                                        |   `1`   |
| `line_break_repl` | To prevent a single log message taking up more than one line, every line-break (and consecutive whitespace) is replaced with this string. Passing `None` disables this behavior.       | ` --> ` |
| `level_formats`   | If provided a mapping of log level thresholds to format strings, the formatter will prioritize the format with the highest level threshold for all log records at or above that level. | `None`  |

For more details, check the API of the `SyslogFormatter` constructor in the [documentation][3].

### Extended configuration example

Here is an example using a [custom message format][12] and specifying a different facility and line break replacement:

```python hl_lines="8-11"
import logging.config

log_config = {
    "version": 1,
    "formatters": {
        "my_syslog_formatter": {
            "()": "syslogformat.SyslogFormatter",
            "format": "{levelname:<8}{message} [{name}]",
            "style": "{",
            "facility": 16,
            "line_break_repl": " 🚀 ",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "my_syslog_formatter",
            "stream": "ext://sys.stdout",
        }
    },
    "root": {"handlers": ["console"], "level": "DEBUG"},
}
logging.config.dictConfig(log_config)

logging.debug("foo")
logging.info("bar")
logging.warning("baz")
try:
    raise ValueError("this is bad")
except ValueError as e:
    logging.exception("oof")
```

Output:

```
<135>DEBUG   foo [root]
<134>INFO    bar [root]
<132>WARNING baz [root]
<131>ERROR   oof [root] 🚀 Traceback (most recent call last): 🚀 File "/path/to/module.py", line 30, in <module> 🚀 raise ValueError("this is bad") 🚀 ValueError: this is bad
```

Since the facility was set to `16`, the PRI code ends up being `16 * 8 + 7 == 135` for `DEBUG` level messages and `16 * 8 + 3 == 131` for `ERROR` messages.

Exception texts are of course still appended, when the `exception` log method is called (or the `exc_info` argument is passed), but the custom `line_break_repl` here is used for reformatting those texts.

## Dependencies

- Python `>=3.8` `<=3.12`
- No third-party dependencies
- OS agnostic


[github-last-commit]: https://github.com/daniil-berg/syslogformat/commits
[github-last-commit-img]: https://img.shields.io/github/last-commit/daniil-berg/syslogformat?label=Last%20commit&logo=git
[apache2]: https://apache.org/licenses/LICENSE-2.0
[apache2-img]: https://img.shields.io/badge/Apache-2.0-darkred.svg?logo=apache
[pypi-latest-version]: https://pypi.org/project/syslogformat/
[pypi-latest-version-img]: https://img.shields.io/pypi/v/syslogformat?color=teal&logo=pypi

[1]:  https://docs.python.org/3/library/logging.html#formatter-objects
[2]:  https://datatracker.ietf.org/doc/html/rfc3164#section-4.1
[3]:  https://daniil-berg.github.io/syslogformat
[4]:  https://github.com/daniil-berg/syslogformat
[5]:  https://github.com/daniil-berg/syslogformat/issues
[6]:  https://docs.python.org/3/library/logging.config.html#dictionary-schema-details
[7]:  https://docs.python.org/3/library/logging.config.html#logging-config-dict-userdef
[8]:  https://docs.python.org/3/library/logging.config.html#logging.config.dictConfig
[9]:  https://datatracker.ietf.org/doc/html/rfc3164#section-4.1.1
[10]: https://docs.python.org/3/howto/logging-cookbook.html#formatting-styles
[11]: https://docs.python.org/3/library/logging.html#logging.Formatter
[12]: https://docs.python.org/3/library/logging.html#logrecord-attributes
