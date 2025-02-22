"""
Create and hold a lock, independent of a bin
"""

import sys, pathlib
from binlock import BinLock

if __name__ == "__main__":

	if not len(sys.argv) > 1:
		print(f"Usage: {pathlib.Path(__file__).name} path_to_lock.lck", file=sys.stderr)
		sys.exit(1)
	
	path_lock = pathlib.Path(sys.argv[1])
	if not path_lock.suffix.lower() == ".lck":
		print(f"Expecting a `.lck` file here, got {path_lock} instead", file=sys.stderr)
		sys.exit(2)
	
	with BinLock("zMichael").hold_lock(path_lock) as lock:
		input(f"Holding lock at {path_lock} as {lock.name}... (press any key)")

	print("Lock released")