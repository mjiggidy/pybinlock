import unittest, pathlib
from binlock import BinLock, defaults, exceptions

EXAMPLE_NAME = "zTesteroonie"
EXAMPLE_PATH = str(pathlib.Path(__file__).with_name("example.lck"))
EXAMPLE_BIN  = str(pathlib.Path(__file__).with_name("example.avb"))

class BinLockTests(unittest.TestCase):

	def test_readLock(self):

		# Bin exists
		BinLock.from_bin(EXAMPLE_BIN)
		lock = BinLock.from_bin(EXAMPLE_BIN, missing_bin_ok=False)
		self.assertEqual(lock.name, EXAMPLE_NAME)

		# Check bin not exist
		self.assertIsNone(BinLock.from_bin("NOTABIN.avb"))
		with self.assertRaises(FileNotFoundError):
			BinLock.from_bin("NOTABIN.avb", missing_bin_ok=False)

		# Not a lock
		with self.assertRaises(exceptions.BinLockFileDecodeError):
			BinLock.from_path(EXAMPLE_BIN)
	
	def test_unlockBin(self):

		with self.assertRaises(exceptions.BinLockOwnershipError):
			BinLock("NotTheName").unlock_bin(EXAMPLE_BIN)

		

if __name__ == "__main__":

	unittest.main()