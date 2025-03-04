"""
Defines sane defaults for internal operations.

These may be changed in your program if necessary, but please refer to the documentation for notes and constraints.
"""

def _default_name_from_hostname() -> str:
	"""Use the hostname if possible; """
	import socket
	try:
		return socket.gethostname()
	except:
		return "pybinlock"

DEFAULT_FILE_EXTENSION:str = ".lck"
"""The default file extension for a lock file.  This should remain ``.lck`` for typical Avid environments."""

TOTAL_FILE_SIZE:int = 255
"""Total size of a .lck file, in bytes.  This should remain ``255`` for typical Avid environments."""

MAX_NAME_LENGTH:int = 22
"""
Maximum character length of an allowed lock name.

There does not *appear* to be a hard limit (beyond :data:`TOTAL_FILE_SIZE`//2 since we're dealing with UTF-16), 
but in practice, Avid Media Composer truncates long names to a maximum of ``22`` characters with an ellipsis.
Thus, to be safe, ``22`` seems to be a sane maximum length, but you may wish to change this for experimental 
purposes.
"""

DEFAULT_LOCK_NAME:str = _default_name_from_hostname()[:MAX_NAME_LENGTH]
"""
Default name to use on the lock, if none is provided to the constructor.

In normal use, Avid uses the machine's hostname for the lock name, so I'm using :func:`_default_name_from_hostname()`
to evaulate the hostname when the module is first loaded (rather than each time a lock is created, to avoid the overhead).
"""