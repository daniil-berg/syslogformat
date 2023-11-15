"""Custom type definitions/aliases."""

from logging import PercentStyle
from typing import Any, Mapping, Optional, Union
from typing_extensions import Literal, NotRequired, TypedDict

AnyMap = Mapping[str, Any]
""""""
StyleKey = Literal["%", "{", "$"]
""""""
Style = PercentStyle
""""""
LogLevel = Union[int, str]
""""""
LevelFmtMap = Mapping[LogLevel, str]
""""""


class FormatterKwargs(TypedDict, total=False):
    """Constructor keyword-arguments of the [`logging.Formatter`][] class."""

    fmt: Optional[str]
    """"""
    datefmt: Optional[str]
    """"""
    style: StyleKey
    """"""
    validate: bool
    """"""
    defaults: Optional[AnyMap]
    """"""


class StyleKwargs(TypedDict):
    """Constructor keyword-arguments of any `logging.PercentStyle` class."""

    fmt: str
    """"""
    defaults: NotRequired[Optional[AnyMap]]
    """"""
