class BinLockLengthError(ValueError):
	"""User name is not a valid length (between 1 and MAX_NAME_LENGTH chars)"""

class BinLockFileDecodeError(ValueError):
	"""File could not be decoded; likely not a valid lock file"""

class BinLockExistsError(FileExistsError):
	"""A lock file already exists for this bin, perhaps from another user"""