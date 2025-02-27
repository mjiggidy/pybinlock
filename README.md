# pybinlock

`binlock` is a python package for programmatically reading and writing Avid Media Composer bin locks (`.lck` files).

Lock files are primarily used in multi-user Avid environments to indicate that a particular machine on the network (and of course, the user behind it!) has temporary ownership over an Avid bin (`.avb` file) to 
potentially write changes to the bin.  While one machine holds the lock, others are still able to open the bin, albeit in read-only mode, until the lock is released.  In this way, two operators cannot 
inadvertently make changes to a bin that would step over each other.

The ability to lock, unlock, and otherwise parse a lock file for a bin would be similarly useful for pipeline and automation purposes, and that's where `binlock` comes in.

>[!WARNING]
>While the `.lck` lock file format is a very simple one, it is officially undocumented.  Use this library at your own risk -- I assume no responsibility for any damage to your
>project, loss of data, or underwhelming box office performance.

## Quick Start

### Indefinitely Locking A Bin:

```python
from binlock import BinLock

default_lock = BinLock()                    # The lock name defaults to the machine's hostname, mimicking Avid's behavior
custom_lock  = BinLock("Do Not Touch")      # A custom display name can be given to the lock for special purposes

custom_lock.lock_bin("01_EDITS/Reel 1.avb") # Here, `Reel 1.avb` will appear locked in Avid as "Do Not Touch"
```

### Reading an existing bin lock:

```python
from binlock import BinLock

# You can either directly provide the path to a lock file,
# or provide a path to an Avid bin, and `BinLock` will figure out the appropriate path to the lock file for you
# Ultimately, both of these statements read from the same `01_EDITS/Reel 1.lck`

lock_from_lck = BinLock.from_path("01_EDITS/Reel 1.lck") # Read the .lck file directly at a given path
lock_from_avb = BinLock.from_bin("01_EDITS/Reel 1.avb")  # Read the .lck file corresponding to a given avid bin path

print(f"{lock_from_lck=}  {lock_from_avb=}")
```

Example Output (assuming the Avid bin `Reel 1.avb` is currently locked by `zMichael`):
```
lock_from_lck=BinLock(name='zMichael')  lock_from_avb=BinLock(name='zMichael')
```

### Locking a bin while you do stuff ("holding" the lock), then releasing it:

```python
from binlock import BinLock

path_bin = "01_EDITS/Reel 1.avb"

# Use a context manager to lock a bin as "Processing Bin..." while you do stuff to the bin
with BinLock("Processing Bin...").hold_bin(path_bin) as lock:
  print(f"Bin has been locked as {lock.name}")
  do_risky_things_to_bin(path_bin)

print("Lock has been released")
```

That's the gist of it!  For more of the nitty-gritty, read on.

---

The `binlock.BinLock` class encapsulates the information used in a bin lock and provides functionality for reading and writing a bin lock `.lck` file.  It is essentially a python 
[`dataclass`](https://docs.python.org/3/library/dataclasses.html) with additional validation and convenience methods.  With `binlock.Binlock`, lock files can be programmatically 
created, [read from](#reading), [written to](#locking-a-bin), or ["held" with a context manager](#holding-a-lock-on-a-bin) to indicate ownership and render bins read-only to other users in 
the shared project.

Working with bin locks can be done either by referring directly to the `.lck` files themselves, or to the Avid bins `.avb` they affect.  Ultimately this depends on how you like to 
work and what exacly you're doing, but often the best way is to refer to the Avid bins, which we'll cover first.

## Bin-Referred Operations

Many times, it's best to think of bin locking in terms of the bins you're affecting.  The `binlock.BinLock` class provides methods to read, lock, unlock, or temporarily "hold the lock" for an Avid bin.

### Reading

Reading the lock info for an Avid bin is possible with the `BinLock.from_bin(avb_path)` class method, passing an existing `.avb` file path as a string.

```python
from binlock import BinLock
lock = BinLock.from_bin("01_EDITS/Reel 1.avb")  # Returns a `BinLock` object
if lock:
  print(lock.name)
```
Here, `BinLock.from_bin(avb_path)` returns a`BinLock` object representing the `.lck` lockfile info for a locked bin, or `None` if the bin is not locked.  We then print the name of the lock, for example:
```
zMichael
```

### Locking A Bin

To lock an Avid bin (by writing a `.lck` lock file), we'll create a new `BinLock` object and use it to lock a bin.

```python
from binlock import BinLock
from binlock.exceptions import BinLockExistsError
new_lock = BinLock("zMichael")
try:
  new_lock.lock_bin("01_EDITS/Reel 2.avb")
except BinLockExistsError as e:
  print(e)
else:
  print("Bin is now locked!")
```

Once executed, `Reel 2.avb` will appear locked by `zMichael` to all users on the project.  Custom names can be used for other purposes, such as `Locked Picture` or `Delivered` to indicate 
no further changes are to be made to the bins.  If the bin is already locked, a `BinLockExistsError` will be raised instead.

If a name string is not provided, the machine's host name will be used by default, just as Avid would do.  Therefore, a good one-liner to lock a bin for the current machine might be:

```python
from binlock import BinLock
BinLock(avb_path).lock_bin("01_EDITS/Reel 3.avb")
```

### Unlocking A Bin

A bin can be unlocked, but only by a `BinLock` of the same name.

```python
from binlock import BinLock
from binlock.exceptions import BinLockOwnershipError
try:
  BinLock("zMichael").unlock_bin("01_EDITS/Reel 2.avb")
except BinLockOwnershipError as e:
  print(e)
else:
  print("Bin has been unlocked.")
```

Because a bin should **only** be unlocked by the process that locked it in the first place, if the lock names do not match, a `BinLockOwnershipError` will be raised as a safety precaution, and the bin will not be unlocked.

>[!CAUTION]
>Unlocking bins can be extremely risky and result in data loss if done carelessly.  A bin should only be unlocked if you were the one who locked it, and you are certain that any changes you have made have been properly committed.
>Instead of manually locking and unlocking bins, you should instead [hold a lock](#holding-a-lock-on-a-bin) whenever possible, as described below.

### Holding A Lock On A Bin

It is often much safer to utilize a context manager to lock a bin only while you perform actions on it, then release the lock immediately after.  This is possible with the `BinLock.hold_bin(avb_path)` context manager:

```python
from binlock import BinLock

path_bin = "01_EDITS/Reel 3.avb"

with BinLock("zAdmin").hold_bin(path_bin) as lock:
  print(f"Bin locked as {lock.name}.  Now doing stuff to the bin...")
  do_stuff_to_bin(path_bin)
print("Lock released.")
```

Here, a bin will be safely locked, then unlocked on completion.

## Lock-Referred Operations

Operations similar to [bin-referred operations](#bin-referred-operations) can be done by referencing the `.lck` lock files directly.  This may be useful for 
more specialized workflows, but should be used with caution as the are less safe.

### Reading A Lock File

Reading from an existing `.lck` file is possible using the `BinLock.from_path(lck_path)` class method, passing an existing `.lck` file path as a string.

```python
from binlock import BinLock
lock = BinLock.from_path("01_EDITS/Reel 1.lck")
print(lock.name)
```
This would output the name on the lock, for example:
```
zMichael
```

### Writing A Lock File

Directly writing a `.lck` lock file works similarly to the `BinLock.to_path(lck_path)` class method, passing a path to the `.lck` file you would like to create.

```python
from binlock import BinLock
lock = BinLock("zMichael")
lock.to_path("01_EDITS/Reel 1.lck")
```
This would lock your `Reel 1.avb` bin with the name `zMichael` in your Avid project.  You may need to refresh your project, or attempt to open the bin, to immediately 
see the result.

>[!CAUTION]
>Directly writing a `.lck` file in this way will allow you to overwrite any existing `.lck` file, which is almost certainly a bad idea.  Take care to first
>check for an existing `.lck` file, or even better, use the context manager approach by [holding a lock file](#holding-a-lock-file) instead.

### Holding A Lock File

The strongly recommended way to programmatically lock an Avid bin using `binlock` is to use `BinLock.hold_lock(lck_path)` as a context manager.  This allows you to "hold" the 
lock on a bin while you do stuff to it.  It includes safety checks to ensure a lock does not already exist (i.e. the bin is locked by someone else), and automatically 
removes the lock on exit or on fatal error.

This approach should be used whenever possible (in favor of [directly writing](#writing-a-lock-file) a `.lck`, which can be more risky).

```python
import time
from binlock import BinLock
with BinLock("zMichael").hold_lock("01_EDITS/Reel 1.lck"):
  time.sleep(60) # Look busy
```
Here, the context manager will throw a `BinLockExistsError` if the lock already exists, and will not continue.  Otherwise, it will lock the bin with `zMichael` for 60 seconds, then release the lock.

## Being A "Good Citizen"

I don't mean to toot my own little horn here, but I have also released [`pybinhistory`](https://github.com/mjiggidy/pybinhistory), which is a python package for writing bin log files.  It is highly 
recommended that any time you modify the contents of a bin, you also add an entry in the Avid bin log, just as Avid would do.  Here they are together:

```python
from binlock import BinLock
from binlock.exceptions import BinLockExistsError
from binhistory import BinLog, BinLogEntry

path_bin  = "01_EDITS/Reel 1.avb"

try:

  with BinLock(computer_name).hold_bin(path_bin):
    # Do custom things
    do_cool_stuff_to_bin(path_bin)
    # Then add an entry to the bin log
    BinLog.touch_bin(path_bin)
except BinLockExistsError:
  print(e)
```
