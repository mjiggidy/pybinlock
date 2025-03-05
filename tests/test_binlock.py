import pytest
import pathlib

from binlock import BinLock
from binlock.exceptions import (
	BinLockNameError,
	BinLockFileDecodeError,
	BinLockExistsError,
	BinLockNotFoundError,
	BinLockOwnershipError,
)
from binlock.defaults import DEFAULT_FILE_EXTENSION, DEFAULT_LOCK_NAME, MAX_NAME_LENGTH, TOTAL_FILE_SIZE

# Helper function to create a dummy bin file
def create_dummy_bin(tmp_path, name="dummy.avb"):
	file_path = tmp_path / name
	file_path.write_text("dummy content")
	return file_path

# --- Constructor and Property Tests ---

def test_binlock_invalid_name_non_string():
	with pytest.raises(BinLockNameError):
		BinLock(name=123)

def test_binlock_invalid_name_empty():
	with pytest.raises(BinLockNameError):
		BinLock(name="   ")

def test_binlock_invalid_name_non_printable():
	with pytest.raises(BinLockNameError):
		BinLock(name="\x07Hello")

def test_binlock_invalid_name_too_long():
	too_long = "a" * (MAX_NAME_LENGTH + 1)
	with pytest.raises(BinLockNameError):
		BinLock(name=too_long)

def test_binlock_valid_name():
	name = "validuser"
	lock = BinLock(name=name)
	assert lock.name == name

# --- File Writing and Reading Tests ---

def test_to_from_path(tmp_path):
	name = "testuser"
	lock = BinLock(name=name)
	lock_file = tmp_path / f"dummy{DEFAULT_FILE_EXTENSION}"
	# Write lock file to disk
	lock.to_path(str(lock_file))
	assert lock_file.is_file()
	# Read the lock file back
	lock_from_file = BinLock.from_path(str(lock_file))
	assert lock_from_file == lock

# --- Bin Locking/Unlocking Tests ---

def test_lock_and_from_bin(tmp_path):
	# Create a dummy bin file (required to pass the missing_bin_ok check)
	bin_file = create_dummy_bin(tmp_path, "dummy.avb")
	bin_file_path = str(bin_file)
	expected_lock_path = bin_file.with_suffix(DEFAULT_FILE_EXTENSION)
	
	lock = BinLock(name="tester")
	# Initially, no lock should be present
	assert BinLock.from_bin(bin_file_path) is None
	# Lock the bin
	lock.lock_bin(bin_file_path, missing_bin_ok=False)
	assert expected_lock_path.is_file()
	# Retrieve the lock via from_bin
	lock_read = BinLock.from_bin(bin_file_path)
	assert lock_read is not None
	assert lock_read.name == "tester"
	# Attempting to lock an already locked bin raises an error
	with pytest.raises(BinLockExistsError):
		lock.lock_bin(bin_file_path, missing_bin_ok=False)

def test_unlock_bin(tmp_path):
	# Create a dummy bin file
	bin_file = create_dummy_bin(tmp_path, "dummy.avb")
	bin_file_path = str(bin_file)
	expected_lock_path = bin_file.with_suffix(DEFAULT_FILE_EXTENSION)
	
	lock = BinLock(name="tester")
	# Lock the bin
	lock.lock_bin(bin_file_path, missing_bin_ok=False)
	assert expected_lock_path.is_file()
	# Unlock the bin
	lock.unlock_bin(bin_file_path, missing_bin_ok=False)
	assert not expected_lock_path.is_file()

def test_unlock_bin_not_locked(tmp_path):
	bin_file = create_dummy_bin(tmp_path, "dummy.avb")
	bin_file_path = str(bin_file)
	lock = BinLock(name="tester")
	with pytest.raises(BinLockNotFoundError):
		lock.unlock_bin(bin_file_path, missing_bin_ok=False)

def test_unlock_bin_wrong_owner(tmp_path):
	# Create dummy bin file and determine lock file path
	bin_file = create_dummy_bin(tmp_path, "dummy.avb")
	bin_file_path = str(bin_file)
	expected_lock_path = bin_file.with_suffix(DEFAULT_FILE_EXTENSION)
	
	lock1 = BinLock(name="owner1")
	lock2 = BinLock(name="owner2")
	
	# Lock with the first lock instance
	lock1.lock_bin(bin_file_path, missing_bin_ok=False)
	with pytest.raises(BinLockOwnershipError):
		lock2.unlock_bin(bin_file_path, missing_bin_ok=False)
	
	# Cleanup using the correct owner
	lock1.unlock_bin(bin_file_path, missing_bin_ok=False)
	assert not expected_lock_path.is_file()

# --- Context Manager Tests ---

def test_hold_lock_context(tmp_path):
	# Directly test hold_lock with a chosen lock file path
	lock_file = tmp_path / "dummy.lck"
	lock_file_path = str(lock_file)
	lock = BinLock(name="contextuser")
	
	with lock.hold_lock(lock_file_path) as held_lock:
		assert held_lock.name == "contextuser"
		assert pathlib.Path(lock_file_path).is_file()
	# After context exit, the lock file should be removed
	assert not pathlib.Path(lock_file_path).is_file()

def test_hold_bin_context(tmp_path):
	# Test hold_bin using a dummy bin file
	bin_file = create_dummy_bin(tmp_path, "dummy.avb")
	bin_file_path = str(bin_file)
	expected_lock_path = bin_file.with_suffix(DEFAULT_FILE_EXTENSION)
	lock = BinLock(name="contextuser")
	
	with lock.hold_bin(bin_file_path, missing_bin_ok=False) as held_lock:
		assert held_lock.name == "contextuser"
		assert expected_lock_path.is_file()
	assert not expected_lock_path.is_file()
