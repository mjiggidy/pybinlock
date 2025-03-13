"""
Utilites for working with bin locks (.lck files)
"""

import pathlib, typing, contextlib
from .exceptions import BinLockNameError, BinLockFileDecodeError, BinLockExistsError, BinLockNotFoundError, BinLockOwnershipError
from .defaults import DEFAULT_FILE_EXTENSION, DEFAULT_LOCK_NAME, MAX_NAME_LENGTH, TOTAL_FILE_SIZE

class BinLock:
	"""Represents a bin lock file (.lck)"""

	def __init__(self, name:str=DEFAULT_LOCK_NAME):

		if not isinstance(name, str):
			raise BinLockNameError(f"Lock name must be a string (got {type(name)})")
		elif not name.strip():
			raise BinLockNameError("Username for the lock must not be empty")
		elif not name.isprintable():
			raise BinLockNameError("Username for the lock must not contain non-printable characters")
		elif len(name) > MAX_NAME_LENGTH:
			raise BinLockNameError(f"Username for the lock must not exceed {MAX_NAME_LENGTH} characters (attempted {len(name)} characters)")
		
		self._name = name

	@property
	def name(self) -> str:
		"""Name of the Avid the lock belongs to"""
		return self._name

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
		
		lock_path = self.get_lock_path_from_bin_path(bin_path, missing_bin_ok=missing_bin_ok)

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

		path_lock = self.get_lock_path_from_bin_path(bin_path, missing_bin_ok=missing_bin_ok)

		self.remove_path(path_lock)

	def remove_path(self, lock_path:str, ownership_check:bool=True):
		"""
		Remove a lock from at a given `.lck` path
		"""

		try:
			bin_lock = self.from_path(lock_path)
		except FileNotFoundError as e:
			raise BinLockNotFoundError("This bin is not currently locked") from e
		
		if ownership_check and bin_lock != self: # TIP: Never skip ownership check, brah
			raise BinLockOwnershipError(f"This bin is currently locked by {bin_lock.name}")
		
		try:
			pathlib.Path(lock_path).unlink()
		except FileNotFoundError:
			pass
	@classmethod
	def from_bin(cls, bin_path:str, missing_bin_ok:bool=True) -> typing.Optional["BinLock"]:
		"""
		Get the existing lock for a given bin (.avb) path

		Returns `None` if the bin is not locked
		"""
		
		lock_path = cls.get_lock_path_from_bin_path(bin_path, missing_bin_ok=missing_bin_ok)
		
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

		lock_path = self.get_lock_path_from_bin_path(bin_path, missing_bin_ok=missing_bin_ok)
		return _BinLockContextManager(self, lock_path)
	
	@staticmethod
	def get_lock_path_from_bin_path(bin_path:str, missing_bin_ok:bool=True) -> str:
		"""Determine the lock path from a given bin path"""

		if not missing_bin_ok and not pathlib.Path(bin_path).is_file():
			raise FileNotFoundError(f"Bin does not exist at {bin_path}")

		return str(pathlib.Path(bin_path).with_suffix(DEFAULT_FILE_EXTENSION))
	
	def __repr__(self) -> str:
		return f"<{self.__class__.__name__} name={self.name}>"
	
	def __str__(self) -> str:
		return self.name
	
	def __eq__(self, other) -> bool:
		return isinstance(other, self.__class__) and self.name == other.name
	
	def __hash__(self):
		return hash(self.name)

class _BinLockContextManager(contextlib.AbstractContextManager):
	"""Context manager for a binlock file"""

	def __init__(self, lock:BinLock, lock_path:str):
		"""Save the info"""

		self._lock_info = lock
		self._lock_path = lock_path
		self._lock_active = False

	def __enter__(self) -> BinLock:
		"""Write the lock on enter"""

		if pathlib.Path(self._lock_path).is_file():
			raise BinLockExistsError(f"Lock already exists at {self._lock_path}")
		
		try:
			self._lock_info.to_path(self._lock_path)
			self._lock_active = True
		except Exception as e:
			if pathlib.Path(self._lock_path).is_file():
				self._lock_info.remove_path(self._lock_path)
			raise RuntimeError from e

		return self._lock_info

	def __exit__(self, exc_type, exc_value, traceback) -> bool:
		"""Remove the lock on exit and call 'er a day"""

		# Something failed during __enter__
		if not self._lock_active:
			return False

		try:
			self._lock_info.remove_path(self._lock_path)
		except BinLockNotFoundError as e:
				raise BinLockNotFoundError("Bin lock was removed before context manager exit!") from e
		except BinLockOwnershipError as e:
				raise BinLockOwnershipError("Bin lock owner changed since its creation!") from e

		return False