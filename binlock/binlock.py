"""Utilites for working with bin locks (.lck files)"""

import dataclasses, pathlib, typing, contextlib
from . import MAX_NAME_LENGTH, BinLockLengthError, BinLockFileDecodeError

@dataclasses.dataclass(frozen=True)
class BinLock:
	"""Represents a bin lock file (.lck)"""

	name:str
	"""Name of the Avid the lock belongs to"""

	def __post_init__(self):
		"""Validate lock name"""

		if not self.name.strip():
			raise BinLockLengthError("Username for the lock must not be empty")
		elif len(self.name) > MAX_NAME_LENGTH:
			raise BinLockLengthError(f"Username for the lock must not exceed {MAX_NAME_LENGTH} characters (attempted {len(self.name)} characters)")
		
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
			lock_file.write(self.name[:MAX_NAME_LENGTH].ljust(255, '\x00').encode("utf-16le"))
	
	def hold(self, lock_path:str) -> "_BinLockContextManager":
		"""Hold the lock"""

		return _BinLockContextManager(self, lock_path)


class _BinLockContextManager(contextlib.AbstractContextManager):
	"""Context manager for a binlock file"""

	def __init__(self, lock:BinLock, lock_path:str):
		"""Save the info"""

		self._lock_info = lock
		self._lock_path = lock_path

	def __enter__(self) -> "_BinLockContextManager":
		"""Write the lock on enter"""

		if pathlib.Path(self._lock_path).is_file():
			raise FileExistsError(f"Lock already exists at {self._lock_path}")
		
		try:
			self._lock_info.to_path(self._lock_path)
		except Exception as e:
			pathlib.Path(self._lock_path).unlink(missing_ok=True)
			raise e

		return self

	def __exit__(self, exc_type, exc_value, traceback) -> bool:
		"""Remove the lock on exit and call 'er a day"""

		pathlib.Path(self._lock_path).unlink(missing_ok=True)		
		return False