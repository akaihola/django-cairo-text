==================================
 Change log for django-cairo-text
==================================

-------------------------
Release 1.1.1: 2009-03-20
-------------------------

* a failing optimizer now sends e-mail (production mode) or raises an
  exception (debug mode)
* bugfix: fixed string format in the size mismatch exception message
* minor documentation fix

-----------------------
Release 1.1: 2009-03-16
-----------------------

* added support for external image optimizers
* added support for embedding base64 encoded images in <IMG> tags
* template tag returns a ``TextImage`` instance instead of a dict

-----------------------
Release 1.0: 2009-03-06
-----------------------

* initial release
* renamed ``y`` option to ``baseline``
* removed broken GIF "support"
* added unit tests
* bugfix: cached images not regenerated anymore
* bugfix: copy presets before applying overrides
* documentation: wrote README.rst_
* documentation: wrote CHANGES.rst_

.. _README.rst: README.rst
.. _CHANGES.rst: CHANGES.rst

----------
2009-03-04
----------

* initial checkin to repository
* use PyCairo for rendering
* PNG support
* presets in settings.py
* uploaded to GitHub
