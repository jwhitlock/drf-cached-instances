.. :changelog:

History
=======

0.3.2 (2015-09-23)
------------------
* Remove deprecation warning in Django 1.8
* Expand tests to Django master and Django REST Framework 3.2
* Fix invalid mock.patch tests that break under mock 1.3.0
* Documentation updates and fixes

0.3.1 (2015-06-16)
------------------
* Move get_object_or_404 to mixin method, to allow easier extending.

0.3.0 (2015-04-09)
------------------
* Tested with Django 1.8
* Tested with Django REST Framework 2.4, 3.0, and 3.1
* CachedModel now supports .pk attribute as an alias, usually to the .id
  field. DRF 3 uses .pk to determine if a model is saved to database, and
  returns empty relation data for unsaved fields.
* cache.delete_all_versions() will delete all cached instances of a model and
  PK. This is useful when changes are made outside of normal requests, such as
  during a data migration.

0.2.0 (2014-12-11)
------------------
* Add ``update_only`` option to ``cache.update_instance``, to support eventual
  consistency for cold caches.

0.1.0 (2014-11-06)
------------------

* First release on PyPI.
