

`svg | SVG` svgSVG_pipe
=======================

Graphics applications are often picky (extremely picky) about the formatting of graphics documents. In order to have SVG files interpreted by your/everybodies favourite vector graphics application, the file structure not only needs to follow the SVG specs, but should follow a precise structure of layers, ids, and other unwritten conventions.

The project wants to facilitate such import/export processes in graphics-intense workflows that involve

 + automated SVG generation (e.g. for data visualisation)
 + inject/extract SVG content into/from existing XML/SVG/HTML documents
 + smooth integration with interactive vector graphics/CAD applications
 + automated data-import and visualisation into complex pre-formatted graphics documents


`svg >> SVG` svgSVG_pipe.inject
-------------------------------

Inject svg content into existing SVG documents, keeping their structure intact.


Requirements and Installation
-----------------------------


Currently under development using:

* Python 3.7
* Pytest 5.2.2.


Tests
-----


### run tests

```
pytest
```


### visual inspection of test results

To get a file output of the SVG content involved in the testing:
+ Set environment variable `SVGPIPE_TEST_SVG_OUT` to point to the desired output directory.
+ Make sure the directory/folder exists.

After the test run, for each svg injection test there will be three SVG files:
+ `XXXX_test.svg` (before the injection)
+ `XXXX_result.svg` (what was actually the case after the injection)
+ `XXXX_expect.svg` (what should be the case after the injection)
