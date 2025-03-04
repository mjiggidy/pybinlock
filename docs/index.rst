.. pybinlock documentation master file, created by
   sphinx-quickstart on Fri Feb 28 21:54:50 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

#########
pybinlock
#########

``pybinlock`` is a python package for the :mod:`binlock` library.

:mod:`binlock` is a python library for programmatically locking and unlocking bins in Avid Media Composer projects.

.. caution::

   :mod:`binlock` is an unofficial library created for educational purposes.  While the ``.lck`` lock file format 
   is a very simple one, it is officially undocumented. Use this library at your own risk -- the developer assumes 
   no responsibility for any damage to your project, loss of data, or underwhelming box office performance.


About bin locks
===============

"Bin locking" is a mechanism primarily used in multi-user Avid environments to indicate that a particular machine on the network has temporary ownership 
over an Avid bin (``.avb`` or ``.avs`` files) to potentially write changes.  While one machine holds the lock, others are still able to 
open the bin, albeit in read-only mode, until the lock is released.  In this way, two operators cannot inadvertently make changes to the 
same bin at the same time.

About :mod:`binlock`
====================

This here :mod:`binlock` library works by reading and writing (``.lck``) files, which are the underyling mechanisms used by Avid to mark bins as "locked."

Interesting uses
----------------

:mod:`binlock` allows functionality beyond Avid's typical lock file implementation, such as:

* Permanently locking bins
* Temporarily locking bins while programmatically reading/writing to them
* Custom lock names for displaying short messages, such as *why* the bin is locked
* Removing "stale" locks

See :doc:`usage` for examples!

See also
========

- `pybinhistory <https://pybinhistory.readthedocs.io>`_: A python library for reading and writing Avid bin log (``.log``) files

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   usage
   bestpractices
   api