"""
Given a path to a bin (.avb), "hold" a lock on it while you do stuff.
I don't know -- I think it's neat.
"""

import sys, pathlib
from binlock import BinLock
from binlock.exceptions import BinLockExistsError
from binlock.defaults import DEFAULT_LOCK_NAME

USAGE = f"Usage: {pathlib.Path(__file__).name} path_to_bin.avb [OptionalBinLockName]"

if __name__ == "__main__":

	if not len(sys.argv) > 1:
		print(USAGE, file=sys.stderr)
		sys.exit(1)
	
	path_bin = pathlib.Path(sys.argv[1])
	if not path_bin.suffix.lower() == ".avb":
		print(f"Expecting a `.avb` file here, got {path_bin} instead", file=sys.stderr)
		print(USAGE, file=sys.stderr)
		sys.exit(2)

	lock_name = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_LOCK_NAME
	
	try:
		with BinLock(lock_name).hold_bin(path_bin) as lock:
			input(f"Holding lock on {path_bin} as {lock.name}... (press any key)")

	except BinLockExistsError as e:
		print(f"Bin is already locked by {BinLock.from_bin(path_bin).name}")
		sys.exit(3)

	else:
		print("Lock released")