"""Utilites for working with bin locks (.lck files)"""

import dataclasses, pathlib, typing, contextlib, socket
from . import BinLockNameError, BinLockFileDecodeError, BinLockExistsError, BinLockNotFoundError, BinLockOwnershipError

DEFAULT_FILE_EXTENSION:str = ".lck"
"""The default file extension for a lock file"""

DEFAULT_LOCK_NAME:str = socket.gethostname()
"""Default name to use on the lock, if none is provided"""

MAX_NAME_LENGTH:int = 24
"""Maximum allowed lock name"""
# TODO: Observed max 21 in real-life locks... need to investigate

TOTAL_FILE_SIZE:int = 255
"""Total size of a .lck file"""

@dataclasses.dataclass(frozen=True)
class BinLock:
	"""Represents a bin lock file (.lck)"""

	name:str = DEFAULT_LOCK_NAME
	"""Name of the Avid the lock belongs to"""

	def __post_init__(self):
		"""Validate lock name"""

		if not isinstance(self.name, str):
			raise BinLockNameError(f"Lock name must be a string (got {type(self.name)})")
		elif not self.name.strip():
			raise BinLockNameError("Username for the lock must not be empty")
		elif not self.name.isprintable():
			raise BinLockNameError("Username for the lock must not contain non-printable characters")
		elif len(self.name) > MAX_NAME_LENGTH:
			raise BinLockNameError(f"Username for the lock must not exceed {MAX_NAME_LENGTH} characters (attempted {len(self.name)} characters)")

	@staticmethod
	def _read_utf16le(buffer:typing.BinaryIO) -> str:
		"""Decode as UTF-16le until we hit NULL"""

		b_name = b""
		while True:
			b_chars = buffer.read(2)
			if not b_chars or b_chars == b"\x00\x00":
				break
			b_name += b_chars
		return b_name.decode("utf-16le")
	
	def lock_bin(self, bin_path:str, missing_bin_ok:bool=True):
		"""Lock a given bin (.avb) with this lock"""

		if not missing_bin_ok and not pathlib.Path(bin_path).is_file():
			raise FileNotFoundError(f"Bin does not exist at {bin_path}")
		
		lock_path = self.get_lock_path_from_bin_path(bin_path)

		# Prevent locking an already-locked bin
		if pathlib.Path(lock_path).is_file():
			try:
				lock = self.from_path(lock_path)
				raise BinLockExistsError(f"Bin is already locked by {lock.name}")
			except Exception as e:	# Flew too close to the sun
				raise BinLockExistsError("Bin is already locked")
		
		self.to_path(lock_path)
	
	def unlock_bin(self, bin_path:str, missing_bin_ok:bool=True):
		"""
		Unlock a given bin (.avb)
		
		For safety, the name on the bin lock MUST match the name on this `BinLock` instance
		"""

		if not missing_bin_ok and not pathlib.Path(bin_path).is_file():
			raise FileNotFoundError(f"Bin does not exist at {bin_path}")

		bin_lock = self.from_bin(bin_path)

		if not bin_lock:
			raise BinLockNotFoundError("This bin is not currently locked")
		
		if bin_lock != self:
			raise BinLockOwnershipError("Bin locks do not match")
		
		pathlib.Path(self.get_lock_path_from_bin_path(bin_path)).unlink(missing_ok=True)
	
	@classmethod
	def from_bin(cls, bin_path:str, missing_bin_okay:bool=True) -> "BinLock":
		"""
		Get the existing lock for a given bin (.avb) path

		Returns `None` if the bin is not locked
		"""

		if not missing_bin_okay and not pathlib.Path(bin_path).is_file():
			raise FileNotFoundError(f"Bin does not exist at {bin_path}")
		
		lock_path = cls.get_lock_path_from_bin_path(bin_path)
		
		if not pathlib.Path(lock_path).is_file():
			return None
		
		return cls.from_path(lock_path)

	@classmethod
	def from_path(cls, lock_path:str) -> "BinLock":
		"Read from .lck lockfile"

		with open(lock_path, "rb") as lock_file:
			try:
				name = cls._read_utf16le(lock_file)
			except UnicodeDecodeError as e:
				raise BinLockFileDecodeError(f"{lock_path}: This does not appear to be a valid lock file ({e})")
		return cls(name=name)
	
	def to_path(self, lock_path:str):
		"""Write to .lck lockfile"""

		with open(lock_path, "wb") as lock_file:
			lock_file.write(self.name[:MAX_NAME_LENGTH].ljust(TOTAL_FILE_SIZE, '\x00').encode("utf-16le"))
	
	def hold_lock(self, lock_path:str) -> "_BinLockContextManager":
		"""Context manager to hold a lock at a given path"""

		return _BinLockContextManager(self, lock_path)
	
	def hold_bin(self, bin_path:str, missing_bin_ok:bool=True) -> "_BinLockContextManager":
		"""Context manager to hold a lock for a given bin (.avb) path"""

		if not missing_bin_ok and not pathlib.Path(bin_path).is_file():
			raise FileNotFoundError(f"Bin does not exist at {bin_path}")

		lock_path = self.get_lock_path_from_bin_path(bin_path)
		return _BinLockContextManager(self, lock_path)
	
	@staticmethod
	def get_lock_path_from_bin_path(bin_path:str) -> str:
		"""Determine the lock path from a given bin path"""

		return str(pathlib.Path(bin_path).with_suffix(DEFAULT_FILE_EXTENSION))

class _BinLockContextManager(contextlib.AbstractContextManager):
	"""Context manager for a binlock file"""

	def __init__(self, lock:BinLock, lock_path:str):
		"""Save the info"""

		self._lock_info = lock
		self._lock_path = lock_path

	def __enter__(self) -> BinLock:
		"""Write the lock on enter"""

		if pathlib.Path(self._lock_path).is_file():
			raise BinLockExistsError(f"Lock already exists at {self._lock_path}")
		
		try:
			self._lock_info.to_path(self._lock_path)
		except Exception as e:
			pathlib.Path(self._lock_path).unlink(missing_ok=True)
			raise e

		return self._lock_info

	def __exit__(self, exc_type, exc_value, traceback) -> bool:
		"""Remove the lock on exit and call 'er a day"""

		pathlib.Path(self._lock_path).unlink(missing_ok=True)		
		return False