import sys, pathlib, dataclasses
from datetime import datetime, timezone
from binlock import BinLock

USAGE_STRING = f"Usage: {pathlib.Path(__file__).name} avid_project_folder_path"

@dataclasses.dataclass(frozen=True)
class LockDetails:
	lock_info:BinLock
	lock_path:pathlib.Path
	bin_path:pathlib.Path|None
	timestamp_modified:datetime

def get_lock_details(lock_path:pathlib.Path) -> LockDetails:

	lock_info = BinLock.from_path(lock_path)
	bin_path = lock_path.with_suffix(".avb") if lock_path.with_suffix(".avb").is_file() else None
	timestamp = datetime.fromtimestamp(lock_path.stat().st_mtime, tz=timezone.utc)

	return LockDetails(
		lock_info = lock_info,
		lock_path = lock_path,
		bin_path  = bin_path,
		timestamp_modified = timestamp
	)

	

if __name__ == "__main__":

	if not len(sys.argv) > 1:
		print(USAGE_STRING, file=sys.stderr)
		sys.exit(1)

	path_project = sys.argv[1]
	
	if not pathlib.Path(path_project).is_dir():
		print(f"Not a valid Avid project folder: {path_project}", file=sys.stderr)
		print(USAGE_STRING, file=sys.stderr)
		sys.exit(2)

	locks:list[LockDetails] = []

	for lock_path in pathlib.Path(path_project).rglob("*.lck"):
		
		if lock_path.name.startswith("."):
			# Skip resource forks
			continue

		try:
			locks.append(get_lock_details(lock_path))
		except Exception as e:
			print(f"Skipping {lock_path}: {e}", file=sys.stderr)
			continue

	print("")
	
	if not locks:
		print("No locks found!  That's nice.")
		sys.exit(0)
	
	print(f"Found {len(locks)} lock(s):")
	print("")

	for lock_details in sorted(locks, key = lambda l: l.timestamp_modified):

		print(f"{lock_details.timestamp_modified.strftime('%Y-%m-%d %H:%M')} \t{lock_details.lock_info.name.ljust(24)} \t{lock_details.bin_path}")