# syslogformat

**Python <a href="https://docs.python.org/3/library/logging.html#formatter-objects" target="_blank">`logging.Formatter`</a> class for <a href="https://datatracker.ietf.org/doc/html/rfc3164#section-4.1" target="_blank">syslog</a> style messages**

---

[📑 Documentation][1] &nbsp; | &nbsp; [🧑‍💻 Source Code][2] &nbsp; | &nbsp; [🐛 Bug Tracker][3]

---

## Installation

`pip install syslogformat`

## Usage

### Basic configuration

As is the case with any logging formatter setup, you need to use the special `()` key to indicate the custom class to use.
(See the <a href="https://docs.python.org/3/library/logging.config.html#dictionary-schema-details" target="_blank">Dictionary Schema Details</a> and <a href="https://docs.python.org/3/library/logging.config.html#logging-config-dict-userdef" target="_blank">User-defined objects</a> sections in the official `logging.config` documentation.)

For example, you could use the following config dictionary, pass it to the <a href="https://docs.python.org/3/library/logging.config.html#logging.config.dictConfig" target="_blank">`logging.config.dictConfig`</a> function, and start logging like this:

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
<15>DEBUG   | foo
<14>INFO    | bar
<12>WARNING | baz | __init__.<module>.24
<11>ERROR   | oof | __init__.<module>.28 --> Traceback (most recent call last): --> File "/path/to/module.py", line 26, in <module> --> raise ValueError("this is bad") --> ValueError: this is bad
```

### The `PRI` prefix

To adhere to the `syslog` standard outlined in RFC 3164, every log message must begin with the so called <a href="https://datatracker.ietf.org/doc/html/rfc3164#section-4.1.1" target="_blank">`PRI` part</a>.
This is a code enclosed in angle brackets that indicates the **facility** generating the message and **severity** of the event.
The facility is encoded as an integer between 0 and 23 and the severity is encoded as an integer between 0 and 7.
The `PRI` code is calculated by multiplying the facility by 8 and adding the severity.

Programs like **`systemd-journald`** hide the `PRI` part in their output, but interpret it behind the scenes to allow things like highlighting messages of a certain level a different color and filtering by severity.

By default the facility code `1` is used, which indicates user-level messages, but this can be easily configured (see below).
Since a `DEBUG` log message corresponds to a severity of `7`, the resulting `PRI` part of the first log message is `<15>` (since `1 * 8 + 7 == 15`).
An `ERROR` has the severity `3`, so that message has the `PRI` part `<11>`.

### Configuration options

In addition to the usual <a href="https://docs.python.org/3/library/logging.html#logging.Formatter" target="_blank">formatter options</a>, the `SyslogFormatter` provides the following parameters:

| Parameter             | Description                                                                                                                                                                                                                                        |   Default   |
|-----------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------:|
| `facility`            | The facility value to use for every log message                                                                                                                                                                                                    |     `1`     |
| `line_break_repl`     | To prevent a single log message taking up more than one line, every line-break (and consecutive whitespace) is replaced with this string. Passing `None` disables this behavior.                                                                   |   ` --> `   |
| `detail_threshold`    | Any log message with log level greater or equal to this value will have information appended to it about the module, function and line number, where the log record was made. If a custom message format is passed, this argument will be ignored. |  `WARNING`  |
| `prepend_level_name`  | If `True`, the log level name will be prepended to every log message (but _after_ the `syslog` PRI part). If a custom message format is passed, this argument will be ignored.                                                                     |   `True`    |

### Extended configuration example

Here is an example using a <a href="https://docs.python.org/3/library/logging.html#logrecord-attributes" target="_blank">custom message format</a> and a different facility and line break replacement:

```python hl_lines="8-11"
import logging.config

log_config = {
    "version": 1,
    "formatters": {
        "my_syslog_formatter": {
            "()": "syslogformat.SyslogFormatter",
            "format": "$message [$name]",
            "style": "$",
            "facility": 16,             # <-- specific to syslogformat
            "line_break_repl": " 🚀 ",  # <-- specific to syslogformat
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
<135>foo [root]
<134>bar [root]
<132>baz [root]
<131>oof [root] 🚀 Traceback (most recent call last): 🚀 File "/path/to/module.py", line 30, in <module> 🚀 raise ValueError("this is bad") 🚀 ValueError: this is bad
```

## Dependencies

Python Version 3.7+, OS agnostic


[1]: https://daniil-berg.github.io/syslogformat
[2]: https://github.com/daniil-berg/syslogformat
[3]: https://github.com/daniil-berg/syslogformat/issues
