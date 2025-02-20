# pybinlock

`binlock` is a python module for programatically reading and writing Avid Media Composer bin locks (`.lck` files), which are primarily used in multiuser Avid environments.

The `binlock.BinLock` class encapsulates the name used in a bin lock and provides functionality for reading and writing a bin lock `.lck` file.  It is essentially a python 
[`dataclass`](https://docs.python.org/3/library/dataclasses.html) with additional validation and convenience methods.  With `binlock.Binlock`, lock files can be programatically 
created, [read from](#reading), [written to](#writing), or [held with a context manager](#as-a-context-manager).

## Reading

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

## Writing

Directly writing a `.lck` file works similarly with the `BinLock.to_path(lck_path)` class method, passing a path to the `.lck` file you would like to create.

```python
from binlock import BinLock
lock = BinLock("zMichael")
lock.to_path("01_EDITS/Reel 1.lck")
```
This would lock your `Reel 1.avb` bin with the name `zMichael` in your Avid proejct.  You may need to refresh your project, or attempt to open the bin, to immediately 
see the result.

>[!CAUTION]
>Directly writing a `.lck` file in this way will allow you to overwrite any existing `.lck` file, which is almost certainly a bad idea.  Take care to first
>check for an existing `.lck` file, or even better, use the context manager approach instead.

## As A Context Manager

The strongly recommended way to programatically lock an Avid bin using `pybinlock` is to use `BinLock.hold(lck_path)` as a context manager.  This allows you to "hold" the 
lock on a bin while you do stuff to it, while including safety checks to ensure a lock does not already exist (i.e. the bin is locked by someone else), and automatically 
removing the lock on exit or on fatal error.

```python
import time
from binlock import BinLock
with BinLock("zMichael").hold("01_EDITS/Reel 1.lck"):
  time.sleep(60) # Look busy
```
Here, the context manager will throw a `BinLockExistsError` if the lock already exists, and will not continue.  Otherwise, it will lock the bin with `zMichael` for 60 seconds, then release the lock.

### Being A "Good Citizen"

I don't mean to toot my own little horn here, but I have also released [`pybinlog`](https://github.com/mjiggidy/pybinlog), which is a python module for writing bin log files.  It is highly 
recommended that any time you lock a bin, you also add an entry in the Avid bin log, just as Avid would do.  Here they are together:

```python
from binlock import BinLock, BinLockExistsError
from binlog import BinLog

path_bin = "01_EDITS/Reel 1.avb"
path_lock = BinLock.lock_path_from_bin_path(path_bin)
path_log  = BinLog.log_path_from_bin_path(path_bin)

computer_name = "zMichael"
user_name     = "MJ 2024.12.2"

try:
  with BinLock(computer_name).hold(path_lock):
    BinLog.touch(path_log, computer=computer_name, user=user_name)
    do_cool_stuff_to_bin(path_bin)

except BinLockExistsError as e:
  try:
    print("Bin is already locked by", BinLock.from_path(path_lock).name)
  except Exception as e:
    print("Bin is already locked")
```
