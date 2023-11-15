"""Custom type definitions/aliases."""

import sys
from logging import PercentStyle
from typing import TYPE_CHECKING, Any, Mapping, Optional, Union
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


if TYPE_CHECKING and sys.version_info < (3, 10):

    class FormatterKwargs(TypedDict, total=False):  # noqa: D101
        fmt: Optional[str]
        datefmt: Optional[str]
        style: StyleKey
        validate: bool

    class StyleKwargs(TypedDict):  # noqa: D101
        fmt: str

else:

    class FormatterKwargs(TypedDict, total=False):
        """Constructor keyword-arguments of the [`logging.Formatter`][]."""

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
        """Constructor keyword-arguments of any `logging.PercentStyle`."""

        fmt: str
        """"""
        defaults: NotRequired[Optional[AnyMap]]
        """"""
