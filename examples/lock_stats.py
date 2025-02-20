"""
Read all the locks in a given folder, and determine the longest and shortest names.
Very important.
"""

import sys, pathlib
from binlock import BinLock

if __name__ == "__main__":

	if not len(sys.argv) > 1:
		print(f"Usage: {pathlib.Path(__file__).name} dir_with_locks", file=sys.stderr)
		sys.exit(1)
	
	lock_long   = None
	lock_short  = None

	for lock_path in pathlib.Path(sys.argv[1]).rglob("*.lck"):

		try:
			current_lock = BinLock.from_path(lock_path)
		except FileNotFoundError:
			print(f"Skipping missing file: {lock_path}")
			continue
		except Exception as e:
			print(f"Skipping {lock_path} because: {e}")
			continue

		if not lock_long or len(lock_long.name) < len(current_lock.name):
			lock_long = current_lock
		
		if not lock_short or len(lock_short.name) > len(current_lock.name):
			lock_short = current_lock
	
	if lock_long is None:
		print("Found no locks in here.")
		sys.exit()
	
	print(f" Longest lock name: {str(len(lock_long.name)).rjust(2)} chars  ({lock_long.name})")
	print(f"Shortest lock name: {str(len(lock_short.name)).rjust(2)} chars  ({lock_short.name})")