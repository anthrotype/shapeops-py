===========
shapeops-py
===========


.. image:: https://img.shields.io/pypi/v/shapeops.svg
        :target: https://pypi.python.org/pypi/shapeops

A Python port of the caryll-shapeops_ Javascript library to perform boolean operations and overlap removal on Bezier curves.

The ``shapeops.ufo`` module provides the same interface as the `BooleanOperations`_ package, with the four ``union``, ``intersections``, ``difference`` and ``xor`` operations, and support for the PointPen protocol.

Usage
-----

*TODO*

.. code-block:: python

  import shapeops
  shape1 = [[
    {'x': 0, 'y': 0, 'on': True}, 
    {'x': 100, 'y': 0, 'on': False}, 
    {'x': 200, 'y': 100, 'on': False}, 
    {'x': 200, 'y': 200, 'on': True},
    {'x': 0, 'y': 0, 'on': True}
  ], ...]
  shape2 = [...]
  result = shapeops.boole(shapeops.ops.intersection, shape1, shape2)


Credits
-------

* Belleve Invis (`@be5invis`_), the author of the original Javascript library.
* Mike Kamermans (`@pomax`_), and his `Bezier.js`_ library (the ``shapeops.bezier`` package is a Python port of the latter).
* Frederik Berlaen (`@typemytype`_), the author of `BooleanOperations`_.
* Gregor Ratajc (`@greginvm`_), maintainer of the `Pyclipper`_ bindings for Angus Johnson's `Clipper`_ library, which is used by ``shapeops`` to perform boolean operations on polygons.

.. _caryll-shapeops: https://github.com/caryll/shapeops
.. _@be5invis: https://github.com/be5invis
.. _@pomax: https://github.com/pomax
.. _Bezier.js: https://github.com/Pomax/bezierjs
.. _@typemytype: https://github.com/typemytype
.. _BooleanOperations: https://github.com/typemytype/booleanOperations
.. _@greginvm: https://github.com/greginvm
.. _Pyclipper: https://github.com/greginvm/pyclipper
.. _Clipper: http://www.angusj.com/delphi/clipper.php
