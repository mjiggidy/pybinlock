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
Here, the context manager will throw a `FileExistsError` if the lock already exists, and will not continue.  Otherwise, it will lock the bin with `zMichael` for 60 seconds, then release the lock.
