import io
import re
import traceback
import xml.dom.minidom as minidom

import pytest

import svgpipe

_TEST_SUFFIX = "_test"
_EXPECT_SUFFIX = "_expect"
_RESULT_SUFFIX = "_result"
_SVG_EXT = ".svg"

def normalise_xml(xmlstr):
    xmlstr = xmlstr.replace("\n", " ")
    xmlstr = xmlstr.replace("\t", " ")
    xmlstr = xmlstr.replace("> <", "><")
    xmlstr, _dummy = re.subn(" +", " ", xmlstr)
    return minidom.parseString(xmlstr).toprettyxml()

def assert_xml_equiv(result, expected):
        got = normalise_xml(result)
        exp = normalise_xml(expected)
        assert got == exp, ("XML mismatch. \nGOT:\n{:s}\n\n"
                            "EXPECTED:\n{:s}").format(got, exp)

# cf. https://stackoverflow.com/questions/251464/
def this_fname():
    return traceback.extract_stack(None, 2)[0][2]

def caller_fname():
    return traceback.extract_stack(None, 3)[0][2]

class SVGDoc_Tester:
    TEM1 = """<?xml version='1.0' encoding='utf-8'?>
<svg version="1.2" baseProfile="tiny" xmlns="http://www.w3.org/2000/svg"
 x="0px" y="0px" width="90.71px" height="68.03px" viewBox="%s">
<g id="Layer_B"></g>
<g id="Layer_A">%s</g>
</svg>
"""
    def _prepareSVGDoc(content_test, content_expect, write_if):
        testname = caller_fname()
        write_if(testname+_TEST_SUFFIX+_SVG_EXT,
                 content_test,
                 newtest=testname)
        write_if(testname+_EXPECT_SUFFIX+_SVG_EXT, content_expect)
        infile = io.StringIO(content_test)
        svgdoc = svgpipe.inject.SVGDocInj(infile)
        return svgdoc

    def _save_result(svgdoc, content_expect, write_if):
        testname = caller_fname()
        outfile = io.BytesIO()
        svgdoc.save(outfile)
        content_result = outfile.getvalue().decode("utf8")
        outfile.close()
        assert_xml_equiv(content_result, content_expect)
        write_if(testname+_RESULT_SUFFIX+_SVG_EXT,
                 content_result)
