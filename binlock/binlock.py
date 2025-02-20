"""Utilites for working with bin locks (.lck files)"""

import dataclasses

@dataclasses.dataclass()
class BinLock:
	"""Represents a bin lock file (.lck)"""

	name:str
	"""Name of the Avid the lock belongs to"""

	def __postinit__(self):
		if self.name is None:
			raise ValueError("Username for the lock must not be empty")
		
	@staticmethod
	def _read_utf16le(buffer) -> str:
		"""Decode as UTF-16le until we hit NULL"""

		b_name = b""
		while True:
			b_chars = buffer.read(2)
			if b_chars == b"\x00\x00":
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
				raise ValueError(f"{lock_path}: This does not appear to be a valid lock file ({e})")
		return cls(name=name)
	
	def to_path(self, lock_path:str):
		"""Write to .lck lockfile"""

		with open(lock_path, "wb") as lock_file:
			lock_file.write(self.name[:255].ljust(255, '\x00').encode("utf-16le"))