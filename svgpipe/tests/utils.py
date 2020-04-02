from collections import defaultdict
import io
import re
import string
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

class Testbild:
    _MINDOC1 = """<?xml version='1.0' encoding='utf-8'?>
<svg version="1.2"
     baseProfile="tiny"
     xmlns="http://www.w3.org/2000/svg"
     x="$x" y="$y" width="$width" height="$height"
     viewBox="$viewBox">
<g id="$L1_name">$L1_content</g>
<g id="$L2_name">$L2_content</g>
</svg>
"""
    ### Note: Last layers in the document are rendered last, hence,
    ###       appear as top layers in the rendered view.
    ###       Please double-check with your vector editor's convention.
    def minimal(**kwargs):
        """ Return a 'minimal' SVG document as a string.

        `kwargs`: Optional keyword arguments substitute corresponding
            placeholders in the document template string. Unset
            keywords will will result in default values being used.
        """
        defaults = {
            'viewBox': "0 0 100 150",
            'x': "0px",
            'y': "0px",
            'width': "100px",
            'height': "150px",
            'L1_name': "L1",
            'L2_name': "L2",
        }
        d = dict(defaults)
        d.update(kwargs)    # override defaults with present keyword args
        dd = defaultdict(str, d)   # return "" for all other fields
        return string.Template(Testbild._MINDOC1).substitute(dd)

class SVGDocMaker:
    def prepare_svgdoc(content_test, content_expect, write_if):
        testname = caller_fname()
        write_if(testname+_TEST_SUFFIX+_SVG_EXT,
                 content_test,
                 newtest=testname)
        write_if(testname+_EXPECT_SUFFIX+_SVG_EXT, content_expect)
        infile = io.StringIO(content_test)
        svgdoc = svgpipe.inject.SVGDocInj(infile)
        return svgdoc

    def save_result(svgdoc, content_expect, write_if):
        testname = caller_fname()
        outfile = io.BytesIO()
        svgdoc.save(outfile)
        content_result = outfile.getvalue().decode("utf8")
        outfile.close()
        assert_xml_equiv(content_result, content_expect)
        write_if(testname+_RESULT_SUFFIX+_SVG_EXT,
                 content_result)
