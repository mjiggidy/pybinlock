"""
Given a path to a bin (.avb), "hold" a lock on it while you do stuff.
I don't know -- I think it's neat.
"""

import sys, pathlib
from binlock import BinLock

if __name__ == "__main__":

	if not len(sys.argv) > 1:
		print(f"Usage: {pathlib.Path(__file__).name} path_to_bin.avb", file=sys.stderr)
		sys.exit(1)
	
	path_bin = pathlib.Path(sys.argv[1])
	if not path_bin.suffix.lower() == ".avb":
		print(f"Expecting a `.avb` file here, got {path_bin} instead", file=sys.stderr)
		sys.exit(2)
	
	with BinLock().hold_bin(path_bin) as lock:
		input(f"Holding lock on {path_bin} as {lock.name}... (press any key)")
	
	if BinLock().from_bin(path_bin):
		print("Somehow unable to release bin")
		sys.exit(3)

	print("Lock released")