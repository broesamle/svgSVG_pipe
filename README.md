

`svg|pipe` Transactions for existing SVG documents
==================================================

**Note:** *The project is in an early stage of development. 0.x.x versions do not garantee a stable API.*

`inject` data and SVG content into an existing document, keeping its structure intact.

`extract` data and SVG content from an existing document (planned).

`transfer` data, attributes, etc. between existing SVG elements (planned).


Motivation
----------

Graphics applications are often picky (extremely picky) about the formatting of graphics documents. In order to have SVG files interpreted by your/everybodies favourite vector graphics application, the file structure not only needs to follow the SVG specs, but should follow a precise structure of layers, ids, and other unwritten conventions.

The project wants to facilitate transactions on existing documents for graphics-based workflows:

 + automated SVG generation (e.g. for data visualisation)
 + smooth integration with interactive vector graphics/CAD applications
 + automated data-import into complex pre-formatted graphics documents for visualisation


Philosophy
----------

`svg|pipe` not only uses SVG documents for import/export of graphical content into/from some existing stock of data. SVG documents are XML documents and can serve as data structures themselves.


Requirements and Installation
-----------------------------

Currently under development using:

* Python 3.7
* Pytest 5.2.2.


Install and test
----------------

```
pip install svgpipe
```

(on Windows with older pythons you may need `python -m pip install svgpipe`)


### run tests

When in the package directory, just type:
```
pytest
```

When the package was installed via `pip`:

```
pytest --pyargs svgpipe
```


### visual inspection of test results

To get a file output of the SVG content involved in the testing:
+ Set environment variable `SVGPIPE_TEST_SVG_OUT` to point to the desired output directory.
+ Make sure the directory/folder exists.

After the test run, for each svg injection test there will be three SVG files:
+ `XXXX_test.svg` (before the injection)
+ `XXXX_result.svg` (what was actually the case after the injection)
+ `XXXX_expect.svg` (what should be the case after the injection)
