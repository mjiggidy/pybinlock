import pytest
import pathlib
from binlock import BinLock
from binlock.defaults import MAX_NAME_LENGTH
from binlock.exceptions import (
	BinLockNameError,
	BinLockFileDecodeError,
	BinLockExistsError,
	BinLockOwnershipError,
)


# Helper to create a dummy bin file (with a .avb extension)
def create_dummy_bin(tmp_path):
	dummy_bin = tmp_path / "dummy.avb"
	dummy_bin.write_text("dummy content")
	return dummy_bin

def test_binlock_creation_valid():
	# Creating a BinLock with a valid name should succeed.
	lock = BinLock(name="valid_user")
	assert lock.name == "valid_user"

def test_binlock_invalid_empty_name():
	# An empty (or whitespace-only) name should raise an error.
	with pytest.raises(BinLockNameError):
		BinLock(name="   ")

def test_binlock_invalid_non_string():
	# A non-string name should raise an error.
	with pytest.raises(BinLockNameError):
		BinLock(name=123)

def test_binlock_invalid_too_long_name():
	# A name longer than MAX_NAME_LENGTH should raise an error.
	long_name = "a" * (MAX_NAME_LENGTH + 1)
	with pytest.raises(BinLockNameError):
		BinLock(name=long_name)

def test_to_from_path_roundtrip(tmp_path):
	# Write a lock to file then read it back; the objects should be equal.
	lock = BinLock(name="tester")
	lock_file = tmp_path / "test.lck"
	lock.to_path(str(lock_file))
	loaded_lock = BinLock.from_path(str(lock_file))
	assert loaded_lock == lock

def test_lock_bin_creates_lock_file(tmp_path):
	# Locking a bin should create the corresponding lock file.
	dummy_bin = create_dummy_bin(tmp_path)
	lock = BinLock(name="user1")
	lock_file_path = pathlib.Path(lock.get_lock_path_from_bin_path(str(dummy_bin)))
	# Ensure the lock file doesn't exist before locking.
	if lock_file_path.exists():
		lock_file_path.unlink()
	lock.lock_bin(str(dummy_bin))
	assert lock_file_path.exists()

def test_lock_bin_already_locked(tmp_path):
	# Trying to lock an already locked bin should raise a BinLockExistsError.
	dummy_bin = create_dummy_bin(tmp_path)
	lock1 = BinLock(name="user1")
	lock2 = BinLock(name="user2")
	# First lock the bin.
	lock1.lock_bin(str(dummy_bin))
	with pytest.raises(BinLockExistsError):
		lock2.lock_bin(str(dummy_bin))
	# Cleanup: remove the lock file.
	lock_file = pathlib.Path(lock1.get_lock_path_from_bin_path(str(dummy_bin)))
	if lock_file.exists():
		lock_file.unlink()

def test_unlock_bin_removes_lock_file(tmp_path):
	# Unlocking a bin should remove its lock file.
	dummy_bin = create_dummy_bin(tmp_path)
	lock = BinLock(name="user1")
	lock.lock_bin(str(dummy_bin))
	lock_file = pathlib.Path(lock.get_lock_path_from_bin_path(str(dummy_bin)))
	assert lock_file.exists()
	lock.unlock_bin(str(dummy_bin))
	assert not lock_file.exists()

def test_unlock_bin_wrong_owner(tmp_path):
	# Unlocking with a BinLock instance that doesn't match the one that locked it
	# should raise a BinLockOwnershipError.
	dummy_bin = create_dummy_bin(tmp_path)
	lock1 = BinLock(name="user1")
	lock2 = BinLock(name="user2")
	lock1.lock_bin(str(dummy_bin))
	with pytest.raises(BinLockOwnershipError):
		lock2.unlock_bin(str(dummy_bin))
	# Cleanup:
	lock_file = pathlib.Path(lock1.get_lock_path_from_bin_path(str(dummy_bin)))
	if lock_file.exists():
		lock_file.unlink()

def test_get_lock_from_bin_returns_none(tmp_path):
	# When no lock file exists, get_lock_from_bin should return None.
	dummy_bin = create_dummy_bin(tmp_path)
	assert BinLock.from_bin(str(dummy_bin)) is None

def test_hold_lock_context_manager(tmp_path):
	# The hold_lock context manager should create the lock file on entry and remove it on exit,
	# while returning the BinLock instance.
	lock = BinLock(name="user1")
	lock_file_path = tmp_path / "test.lck"
	if lock_file_path.exists():
		lock_file_path.unlink()
	with lock.hold_lock(str(lock_file_path)) as held_lock:
		assert held_lock == lock
		assert lock_file_path.exists()
	assert not lock_file_path.exists()

def test_hold_bin_context_manager(tmp_path):
	# The hold_bin context manager should similarly manage the lock for a given bin.
	dummy_bin = create_dummy_bin(tmp_path)
	lock = BinLock(name="user1")
	lock_file_path = pathlib.Path(lock.get_lock_path_from_bin_path(str(dummy_bin)))
	if lock_file_path.exists():
		lock_file_path.unlink()
	with lock.hold_bin(str(dummy_bin)) as held_lock:
		assert held_lock == lock
		assert lock_file_path.exists()
	assert not lock_file_path.exists()

def test_corrupt_lock_file(tmp_path):
	# A lock file that cannot be decoded as UTF-16le should raise BinLockFileDecodeError.
	lock_file = tmp_path / "corrupt.lck"
	# Write an odd number of bytes to provoke a decode error.
	lock_file.write_bytes(b'\xff')
	with pytest.raises(BinLockFileDecodeError):
		BinLock.from_path(str(lock_file))
