"""
Bespoke :class:`Exception` classes for pybinlock
"""

class BinLockNameError(ValueError):
	"""The given lock name is not valid for use"""

class BinLockFileDecodeError(ValueError):
	"""File could not be decoded; likely not a valid lock file"""

class BinLockExistsError(FileExistsError):
	"""A lock file already exists for this bin, perhaps from another machine"""

class BinLockNotFoundError(FileNotFoundError):
	"""An expected bin lock is not found"""

class BinLockOwnershipError(PermissionError):
	"""The existing bin lock belongs to another entity (lock names do not match)"""