import sys, pathlib, dataclasses
from datetime import datetime, timezone
from binlock import BinLock, exceptions

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

	if not len(sys.argv) > 1 or not pathlib.Path(sys.argv[1]).is_dir():
		print(USAGE_STRING, file=sys.stderr)
		sys.exit(1)
	
	stray_locks:list[pathlib.Path]   = []
	invalid_locks:list[pathlib.Path] = []

	for path_lock in pathlib.Path(sys.argv[1]).rglob("*.lck"):

		if path_lock.name.startswith("."):
			continue

		try:
			lock_info = BinLock.from_path(path_lock)
		except exceptions.BinLockFileDecodeError:
			invalid_locks.append(path_lock)
			continue
		except exceptions.BinLockNameError:
			invalid_locks.append(path_lock)
			continue

		
		if pathlib.Path(path_lock.with_suffix(".avb")).is_file():
			path_bin = pathlib.Path(path_lock.with_suffix(".avb"))
		elif pathlib.Path(path_lock.with_suffix(".avc")).is_file():
			path_bin = pathlib.Path(path_lock.with_suffix(".avc"))
		else:
			stray_locks.append(path_lock)
			continue

		timestamp = datetime.fromtimestamp(path_lock.stat().st_mtime, tz=timezone.utc)

		print(f"{path_bin.name:>72}  :  Locked by {lock_info.name} on {timestamp}")
	

	if stray_locks:
		print("")
		print("Stray Locks:")
		for path_lock in stray_locks:
			print(path_lock)
	if invalid_locks:
		print("")
		print("Invalid Locks:")
		for path_lock in invalid_locks:
			print(path_lock)
	