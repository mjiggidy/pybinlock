Best practices
##############

When writing a program that operates in a shared Avid project alongside active users, 
it is important for your program to follow the same procedures as a "legitimate" 
(no offense) Avid system.  :mod:`binlock` exists to help developers design programs that 
are "good citizens" in this environment.  This document details additional best practices 
that should be followed to ensure your program plays nicely with other users and machines 
on the network.

Order of operations
===================

Opening a bin unlocked
----------------------

#. The bin is locked from modification by other users with the creation of a ``.lck`` file
#. The ``.avb`` is read from storage

Closing a bin
-------------

#. The ``.avb`` file is opened for writing
#. Changes are written back to the ``.avb`` file
#. If modifications were made by the user:
	#. An entry is added to the bin's ``.log`` file
	#. A copy of the bin with these changes is saved to the Attic
#. The ``.avb`` file is closed
#. The lock is removed

Other tools
===========

pybinhistory
------------

You may also be interested in `pybinhistory <https://pybinhistory.readthedocs.io/>`_ for reading and writing Avid bin log (``.log``) files.