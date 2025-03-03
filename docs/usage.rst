Usage
=====

Once you have :doc:`installed <installation>` the ``pybinlock`` package, you can import the :mod:`binlock` library:

.. code-block:: python

    import binlock

.. note::
    The package is distributed for installation as ``pybinlock``, but the import name of the library is ``binlock``.

Create a new lock
-----------------

Use the :class:`binlock.BinLock` class to create a new lock in memory:

.. autoclass:: binlock.BinLock
    :no-index:
    :no-members:

.. code-block:: python

    from binlock import BinLock

    # By default, a lock will use your hostname, mimicking Avid's behavior
    my_lock = BinLock()

    # You can alternatively specify a custom lock name
    custom_lock = BinLock("Do Not Touch")

Read an existing lock
---------------------

Use the :meth:`binlock.BinLock.from_bin` factory method to read an existing lock for a given bin:

.. automethod:: binlock.BinLock.from_bin
    :no-index:

.. code-block:: python

    from binlock import BinLock
    
    lock = BinLock.from_bin("01_EDITS/Reel 1.avb")
    if not lock:
        print("Bin is not locked")
    else:
        print(f"Bin is locked by {lock.name}")

.. tip::
    Many of these methods accept an optional ``missing_bin_okay`` ::class:`python:bool`, which defaults to ``True``.
    
    If ``missing_bin_okay`` is set to ``False``, they will throw a :class:`FileNotFoundError` if the given 
    bin path does not exist.


Lock a bin
----------

Temporarily hold a lock
^^^^^^^^^^^^^^^^^^^^^^^

Use :meth:`binlock.BinLock.hold_bin` as a context manager to safely "hold the lock" on a bin while you programmatically 
read or write to it.  The context manager protects against writing to a bin that is already locked by someone else, and 
cleanly removes the lock once your code is complete.

If the bin is already locked, this will throw a :class:`binlock.exceptions.BinLockExistsError`.

.. automethod:: binlock.BinLock.hold_bin
    :no-index:

.. code-block:: python

    from binlock import BinLock
    from binlock.exceptions import BinLockExistsError

    bin_path = "01_EDITS/Reel 1.avb"
    
    try:
        with BinLock("Processing...").hold_bin(bin_path, missing_bin_okay=False) as lock:
            print(f"Bin is successfully locked as {lock.name}")
            do_stuff_to_bin(bin_path)
    except BinLockExistsError:
        print("Cannot proceed: Bin is locked by another machine")
    except FileNotFoundError:
        print(f"Bin does not exist at {bin_path}")
    else:
        print("Processing complete; bin is now unlocked")

.. _indefinite-locks:

Indefinitely lock a bin
^^^^^^^^^^^^^^^^^^^^^^^

Use :meth:`binlock.BinLock.lock_bin` when you wish to lock a bin and *leave* it that way.

If the bin is already locked, this will throw a :class:`binlock.exceptions.BinLockExistsError`.

.. automethod:: binlock.BinLock.lock_bin
    :no-index:

.. code-block:: python

    import pathlib
    from binlock import BinLock
    from binlock.exceptions import BinLockExistsError

    turnover_folder = "05_TURNOVERS/TO SND/250420/"
    lock = BinLock("Delivered 4/21")

    for avb_path in pathlib.Path(turnover_folder).rglob("*.avb"):
        if avb_path.name.startswith("."):
            # Skip dotfiles
            continue
        try:
            lock.lock_bin(avb_path)
        except BinLockExistsError:
            print(f"Skipping {avb_path.name}: Bin is locked by someone else")
        else:
            print(f"Locked {avb_path.name} as {lock.name}")

Unlock a bin
------------

Use :meth:`binlock.BinLock.unlock_bin` to unlock a bin by deleting the ``.lck`` file.  This 
is useful for unlocking :ref:`indefinite locks <_indefinite-locks>`, or for removing stale 
locks left over from an Avid crash or archived project.

As a security measure, the :attr:`binlock.BinLock.name` attribute of the :class:`binlock.BinLock` instance must 
match the name of the lock you are attempting to remove.

This method will raise :class:`binlock.exceptions.BinLockNotFoundError` if the bin is not locked.

It will raise :class:`binlock.exceptions.BinLockOwnershipError` if the name on the lock does not match the name of 
the :class:`binlock.BinLock` that is calling :method:`binlock.BinLock.unlock_bin`.

.. automethod:: binlock.BinLock.unlock_bin
    :no-index:

.. warning::
    
    Unlocking a bin is extremely risky, and can result in lost or corrupt data if the bin is 
    in use by another system.  Be very careful to ensure that the lock is yours to remove.

.. code-block:: python

    from binlock import BinLock
    from binlock.exceptions import BinLockNotFoundError, BinLockOwnershipError

    my_lock = BinLock("zEditor")
    bin_path = "01_EDITS/Reel 3.avb"

    try:
        my_lock.unlock_bin(bin_path)
    except BinLockNotFoundError:
        print("Bin was not locked")
    except BinLockOwnershipError:
        current_lock = BinLock.from_bin(bin_path)
        print(f"Cannot unlock: Bin is locked by {current_lock.name}, not {my_lock.name}")
    else:
        print(f"{bin_path} has been unlocked.")
