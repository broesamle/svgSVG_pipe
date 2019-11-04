import codecs
import io
import os
import re
import traceback
import xml.dom.minidom as minidom

import pytest

from svgSVG_pipe import inject as INJ

_TEST_SUFFIX = "_test"
_EXPECT_SUFFIX = "_expect"
_RESULT_SUFFIX = "_result"
_SVG_EXT = ".svg"

@pytest.fixture(scope="module")
def write_if_svgout():
    try:
        _SVG_OUT = os.environ['SVGPIPE_TEST_SVG_OUT']
        print("Test SVG output:", _SVG_OUT)
        def _write_if_svgout(filename, content):
            f = codecs.open(os.path.join(_SVG_OUT, filename),
                            mode='w', encoding="utf8")
            f.write(content)
    except KeyError:
        def _write_if_svgout(filename, content):
            pass

    return _write_if_svgout

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
def get_this_fname():
    return traceback.extract_stack(None, 2)[0][2]

def get_caller_fname():
    return traceback.extract_stack(None, 3)[0][2]

class Test_ExistingDoc:
    svgdocument1 = """<?xml version='1.0' encoding='utf8'?>
<svg xmlns="http://www.w3.org/2000/svg"
     baseProfile="tiny"
     id="Layer_A"
     version="1.2"
     viewBox="0 0 2834.646 34.6"
     xml:space="preserve">
<g id="Layer_A1"></g>
<g id="Layer_A2"></g>
</svg>
"""

    def test_get_viewbox(self):
        fileobject = io.StringIO(Test_ExistingDoc.svgdocument1)
        svgdoc = INJ.ExistingDoc(fileobject)
        x, y, w, h = svgdoc.get_viewbox()
        assert x==0.0
        assert y==0.0
        assert w==2834.646
        assert h==34.6

class Test_SVGDocInScale:
    TEM1 = """<?xml version='1.0' encoding='utf-8'?>
<svg version="1.2" baseProfile="tiny" xmlns="http://www.w3.org/2000/svg"
 x="0px" y="0px" width="90.71px" height="68.03px" viewBox="0 10 90.71 68.03">
<g id="Layer_B"></g>
<g id="Layer_A">%s</g>
</svg>
"""

    def _prepare(content_test, content_expect, write_if):
        testname = get_caller_fname()
        write_if(testname+_TEST_SUFFIX+_SVG_EXT, content_test)
        write_if(testname+_EXPECT_SUFFIX+_SVG_EXT, content_expect)
        infile = io.StringIO(content_test)
        svgdoc = INJ.SVGDocInScale(infile)
        return svgdoc

    def _save_result(svgdoc, content_expect, write_if):
        testname = get_caller_fname()
        outfile = io.BytesIO()
        svgdoc.save(outfile)
        content_result = outfile.getvalue().decode("utf8")
        outfile.close()
        assert_xml_equiv(content_result, content_expect)
        write_if(testname+_RESULT_SUFFIX+_SVG_EXT,
                 content_result)

    def test_inject_into_layer(self, write_if_svgout):
        content_test = Test_SVGDocInScale.TEM1 % (
            '<rect x="59.527" y="17.008"'
            ' width="25.512" height="39.685" fill="#8080C0" />')
        content_expect = Test_SVGDocInScale.TEM1 % (
            '<rect x="59.527" y="17.008"'
            ' width="25.512" height="39.685" fill="#8080C0" />'
            '<rect x="0" y="10" width="90.71" height="68.03"'
            ' fill="#00CC44" opacity="0.4" />'
            '<line x1="0" y1="10" x2="90.71" y2="78.03"'
            ' stroke="black" />')
        svgdoc =Test_SVGDocInScale._prepare(content_test,
                                            content_expect,
                                            write_if_svgout)
        world_horiz = (-10,20)
        world_left, world_right = world_horiz
        world_width = world_right - world_left
        world_vert = (0,40)
        world_top, world_bottom  = world_vert
        world_height = world_bottom - world_top
        injp =  svgdoc.get_layer_injectpoint("Layer_A",
                                             world_horiz,
                                             world_vert)
        x1doc = injp.h2x(world_left)
        y1doc = injp.v2y(world_top)
        x2doc = injp.h2x(world_right)
        y2doc = injp.v2y(world_bottom)
        widthdoc = injp.hx_factor * world_width
        heightdoc = injp.vy_factor * world_height
        rect = ('<rect x="{:g}" y="{:g}" width="{:g}" height="{:g}"'
                ' fill="#00CC44" opacity="0.4" />').format(
                                             x1doc, y1doc,
                                             widthdoc, heightdoc)
        injp.inject(rect)
        line = ('<line x1="{:g}" y1="{:g}" x2="{:g}" y2="{:g}"'
                ' stroke="black" />').format(x1doc, y1doc,
                                             x2doc, y2doc)
        injp.inject(line)
        Test_SVGDocInScale._save_result(svgdoc,
                                        content_expect,
                                        write_if_svgout)
