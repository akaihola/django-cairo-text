==================================
 Change log for django-cairo-text
==================================

---------------------------
Release 1.1: in development
---------------------------

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
