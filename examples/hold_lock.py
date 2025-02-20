"""
Given a path to a bin (.avb), "hold" a lock on it while you do stuff.
I don't know -- I think it's neat.
"""

import sys, pathlib, enum
from binlock import BinLock, DEFAULT_FILE_EXTENSION

class OverEngineeredExitCodes(enum.IntEnum):

	EXIT_OK   = 0
	BAD_USAGE = 1
	NOT_AVB   = 2
	NO_AVB    = 3

if __name__ == "__main__":

	if not len(sys.argv) > 1:
		print(f"Usage: {pathlib.Path(__file__).name} path_to_bin.avb", file=sys.stderr)
		sys.exit(OverEngineeredExitCodes.BAD_USAGE)
	
	path_bin = pathlib.Path(sys.argv[1])
	if not path_bin.suffix.lower() == ".avb":
		print(f"Expecting a `.avb` file here, got {path_bin} instead", file=sys.stderr)
		sys.exit(OverEngineeredExitCodes.NOT_AVB)
	
	elif not path_bin.is_file():
		print(f"Bin does not exist: {path_bin}", file=sys.stderr)
		sys.exit(OverEngineeredExitCodes.NO_AVB)

	# Determine lock path from a given bin path
	path_lock = BinLock.lock_path_from_bin_path(path_bin)

	# Lock bin while we do stuff, then release it
	with BinLock("anon").hold(path_lock):
		input("Deleting important things...")
	
	print("Done")