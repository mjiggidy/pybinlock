import unittest, pathlib, tempfile
from binlock import BinLock, defaults, exceptions

EXAMPLE_NAME  = "zTesteroonie"
EXAMPLE_PATH  = str(pathlib.Path(__file__).with_name("example.lck"))
EXAMPLE_BIN   = str(pathlib.Path(__file__).with_name("example.avb"))
EXAMPLE_NOBIN = str(pathlib.Path(__file__).with_name("notabin.avb"))

class BinLockTests(unittest.TestCase):

	def test_validate(self):

		# ---
		# Validate lock name
		# ---

		with self.assertRaises(exceptions.BinLockNameError):
			BinLock("")

		with self.assertRaises(exceptions.BinLockNameError):
			BinLock(" ")

		with self.assertRaises(exceptions.BinLockNameError):
			BinLock(2)

		with self.assertRaises(exceptions.BinLockNameError):
			BinLock(int)

		with self.assertRaises(exceptions.BinLockNameError):
			BinLock("Heeheehee\n")

		with self.assertRaises(exceptions.BinLockNameError):
			BinLock("A" * (defaults.MAX_NAME_LENGTH+1))
		
		BinLock("A" * defaults.MAX_NAME_LENGTH)
		BinLock("💦") # TODO: I... GUESS this is valid?
		BinLock(defaults.DEFAULT_LOCK_NAME)
		
		# ---
		# Write locks
		# ---

		with self.assertRaises(FileNotFoundError):
			BinLock(EXAMPLE_NAME).lock_bin(EXAMPLE_NOBIN, missing_bin_ok=False)
		BinLock(EXAMPLE_NAME).lock_bin(EXAMPLE_NOBIN, missing_bin_ok=True)
		
		# Existing bin
		# Write
		BinLock(EXAMPLE_NAME).lock_bin(EXAMPLE_BIN, missing_bin_ok=False)
		# But don't overwrite
		with self.assertRaises(exceptions.BinLockExistsError):
			BinLock(EXAMPLE_NAME).lock_bin(EXAMPLE_BIN)

		self.assertEqual(pathlib.Path(EXAMPLE_PATH).stat().st_size, defaults.TOTAL_FILE_SIZE * 2)

		# ---
		# Read locks
		# ---

		# Lock exists (from test_writelock) but bin doesn't
		with self.assertRaises(FileNotFoundError):
			BinLock.from_bin(EXAMPLE_NOBIN, missing_bin_ok=False)
		
		lock1 = BinLock.from_bin(EXAMPLE_NOBIN)

		BinLock.from_bin(EXAMPLE_BIN)
		lock2 = BinLock.from_bin(EXAMPLE_BIN, missing_bin_ok=False)

		self.assertTrue(lock1.name == lock2.name == EXAMPLE_NAME)

		# ---
		# Remove locks
		# ---

		# Remove nobin
		with self.assertRaises(exceptions.BinNotFoundError):
			BinLock().unlock_bin(EXAMPLE_NOBIN, missing_bin_ok=False)
		with self.assertRaises(exceptions.BinLockOwnershipError):
			BinLock("peepee").unlock_bin(EXAMPLE_NOBIN)
		
		self.assertTrue(pathlib.Path(EXAMPLE_NOBIN).with_suffix(".lck").is_file())
		lock1.unlock_bin(EXAMPLE_NOBIN)
		self.assertFalse(pathlib.Path(EXAMPLE_NOBIN).with_suffix(".lck").is_file())
		with self.assertRaises(exceptions.BinLockNotFoundError):
			lock1.unlock_bin(EXAMPLE_NOBIN)

		# Remove bin
		with self.assertRaises(exceptions.BinLockOwnershipError):
			BinLock("peepee").unlock_bin(EXAMPLE_BIN)
		self.assertTrue(pathlib.Path(EXAMPLE_BIN).with_suffix(".lck").is_file())
		lock2.unlock_bin(EXAMPLE_BIN, missing_bin_ok=False)
		self.assertFalse(pathlib.Path(EXAMPLE_BIN).with_suffix(".lck").is_file())
		with self.assertRaises(exceptions.BinLockNotFoundError):
			lock2.unlock_bin(EXAMPLE_BIN, missing_bin_ok=False)
		

		# ---
		# Context manager
		# ---

		# Bin already locked
		BinLock("HereFirst").lock_bin(EXAMPLE_BIN)
		with self.assertRaises(exceptions.BinLockExistsError), BinLock().hold_bin(EXAMPLE_BIN) as lock:
			print(lock)
		BinLock("HereFirst").unlock_bin(EXAMPLE_BIN)
		self.assertIsNone(BinLock("HereFirst").from_bin(EXAMPLE_BIN))

		# All is well
		with BinLock("M. Holden").hold_bin(EXAMPLE_BIN) as lock:
			# Lock exists and matches the name
			self.assertEqual(BinLock.from_bin(EXAMPLE_BIN), lock)
		self.assertIsNone(BinLock.from_bin(EXAMPLE_BIN))

		with self.assertRaises(exceptions.BinLockChangedError), BinLock(EXAMPLE_NAME).hold_bin(EXAMPLE_BIN) as lock:
			# Remove lock unexpectedly like a bad person
			self.assertEqual(lock, BinLock.from_bin(EXAMPLE_BIN))
			lock.unlock_bin(EXAMPLE_BIN)
		self.assertIsNone(BinLock.from_bin(EXAMPLE_BIN))

		with self.assertRaises(exceptions.BinLockChangedError), BinLock(EXAMPLE_NAME).hold_bin(EXAMPLE_BIN) as lock:
			# REPLACE lock unexpectly
			# You deserve whatever happens here honestly smdh
			lock.unlock_bin(EXAMPLE_BIN)
			BinLock("Satan").lock_bin(EXAMPLE_BIN)
		BinLock("Satan").unlock_bin(EXAMPLE_BIN)

if __name__ == "__main__":


	unittest.main()