"""
Defines sane defaults for internal operations
"""

def _default_name_from_hostname() -> str:
	"""Use the hostname if possible; """
	import socket
	try:
		return socket.gethostname()
	except:
		return "pybinlock"

DEFAULT_FILE_EXTENSION:str = ".lck"
"""The default file extension for a lock file"""

TOTAL_FILE_SIZE:int = 255
"""Total size of a .lck file"""

MAX_NAME_LENGTH:int = 22
"""Maximum allowed lock name"""
# NOTE: Lock name lengths beyond 22 characters don't necessarily freak Avid out, but are truncated with an ellipse

DEFAULT_LOCK_NAME:str = _default_name_from_hostname()[:MAX_NAME_LENGTH]
"""Default name to use on the lock, if none is provided"""