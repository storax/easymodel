.. :changelog:

History
-------

0.1.0 (2014-08-27)
+++++++++++++++++++++++++++++++++++++++

* First release on PyPI.

0.2.0 (2015-01-04)
+++++++++++++++++++++++++++++++++++++++

* Specialized views that handle click events and propagate them to the editor widget.
* Easier insertion and removal of rows
* Editing supported

0.3.0 (2015-02-10)
+++++++++++++++++++++++++++++++++++++++

* Fix emit signal when calling set_data
* Fix editor resizing
* Add ItemDataRoles to retrieve the internal objects of an index
* Easy conversion from ItemData to TreeItem
* Emit clicks on widgetdelegate via QApplication and to the actual child widget

0.4.0 (2015-08-09)
+++++++++++++++++++++++++++++++++++++++

* python 3 support

0.4.1 (2015-11-05)
+++++++++++++++++++++++++++++++++++++++

* Fix click recursion in delegate event propagation

0.4.2 (2015-11-07)
+++++++++++++++++++++++++++++++++++++++

* Update tests for PySide 1.2.4

0.5.0 (2015-11-08)
+++++++++++++++++++++++++++++++++++++++

* Add cascading views
