"""
A lil' library for reading and writing bin lock (.lck) files
By Michael Jordan <michael@glowingpixel.com>
https://github.com/mjiggidy/pybinlock
"""

MAX_NAME_LENGTH:int = 24
"""Maximum allowed lock name"""
# TODO: Observed max 21 in real-life locks... need to investigate

DEFAULT_FILE_EXTENSION = ".lck"
"""
The default file extension for a lock file

Not used directly by `BinLock`, but perhaps useful to reference
in your own scripts so that we're all on the same page
"""

from .exceptions import BinLockFileDecodeError, BinLockLengthError, BinLockExistsError
from .binlock import BinLock