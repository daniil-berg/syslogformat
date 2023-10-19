__copyright__ = "© 2023 Daniil Fajnberg"
__license__ = """Apache-2.0

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License."""

__version__ = "0.0.1"

__doc__ = """
Python `logging.Formatter` class for `syslog` style messages.

In addition to the meta information provided above, this module also provides
convenience imports of the main class from the top-level package.
"""

from .formatter import SyslogFormatter
from .severity import log_level_severity

__all__ = [
    "SyslogFormatter",
    "log_level_severity",
]
