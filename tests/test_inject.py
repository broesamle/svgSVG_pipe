import codecs
import datetime
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
    html_opener = """<!DOCTYPE html>
<html><head>
<title>svg&gt;&gt;SVG inject: Test Panorama</title>
<style>iframe { border:none; }</style>
</head>
<body style="font-family: monospace; border: 0px;">
<h2>Test Panorama</h2>
<p><b>Insepect test results visually:</b><br>
[test setup]&nbsp;&nbsp;&nbsp;[expected result]&nbsp;&nbsp;&nbsp;[result]</p>
"""

    try:
        _SVG_OUT = os.environ['SVGPIPE_TEST_SVG_OUT']
        _panorama_svgfile = codecs.open(os.path.join(_SVG_OUT, "panorama.html"),
                            mode='w', encoding="utf8")
        _panorama_svgfile.write(html_opener)
        def _write_if_svgout(filename, content, newtest=None):
            if newtest is not None:
                _panorama_svgfile.write("\n<h3>%s</h3>\n" % newtest)
            item = '<iframe src="{:s}"></iframe>\n'.format(filename)
            _panorama_svgfile.write(item)
            f = codecs.open(os.path.join(_SVG_OUT, filename),
                            mode='w', encoding="utf8")
            f.write(content)
    except KeyError:
        _panorama_svgfile = None
        def _write_if_svgout(filename, content, newtest=None):
            pass

    yield _write_if_svgout
    if _panorama_svgfile:
        _panorama_svgfile.write('</body></html>')
        _panorama_svgfile.close()

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

class Test_ExistingDoc:
    svgdocument1 = """<?xml version='1.0' encoding='utf8'?>
<svg xmlns="http://www.w3.org/2000/svg"
     baseProfile="tiny"
     id="Layer_A"
     version="1.2"
     viewBox="0 0 2834.646 34.6"
     xml:space="preserve">
<g id="Layer_A1">%s</g>
<g id="Layer_A2">%s</g>
</svg>
"""

    def test_get_viewbox(self):
        fileobject = io.StringIO(Test_ExistingDoc.svgdocument1
                                 % ("",""))
        svgdoc = INJ.ExistingDoc(fileobject)
        x, y, w, h = svgdoc.get_viewbox()
        assert x==0.0
        assert y==0.0
        assert w==2834.646
        assert h==34.6

    def test_get_layer(self):
        fileobject = io.StringIO(Test_ExistingDoc.svgdocument1
                                 % ("",""))
        svgdoc = INJ.ExistingDoc(fileobject)
        layer = svgdoc.get_layer("Layer_A1")
        assert type(layer) is not None
        with pytest.raises(INJ.NotFoundError):
            svgdoc.get_layer("X")

    def test_get_poly_injectpoint(self):
        fileobject = io.StringIO(Test_ExistingDoc.svgdocument1
                                 % ('<polygon id="Poly1"/>',
                                    '<polyline id="Poly2"/>'))
        svgdoc = INJ.ExistingDoc(fileobject)
        poly1 = svgdoc.get_poly_injectpoint('polygon',"Poly1")
        assert poly1 is not None
        poly2 = svgdoc.get_poly_injectpoint('polyline',"Poly2")
        assert poly2 is not None
        with pytest.raises(INJ.NotFoundError):
            svgdoc.get_poly_injectpoint("t","X")
        with pytest.raises(INJ.NotFoundError):
            svgdoc.get_poly_injectpoint("polygon","Poly2")
        with pytest.raises(INJ.NotFoundError):
            svgdoc.get_poly_injectpoint("polyline","Poly1")

class Test_SVGDocInScale:
    TEM1 = """<?xml version='1.0' encoding='utf-8'?>
<svg version="1.2" baseProfile="tiny" xmlns="http://www.w3.org/2000/svg"
 x="0px" y="0px" width="90.71px" height="68.03px" viewBox="%s">
<g id="Layer_B"></g>
<g id="Layer_A">%s</g>
</svg>
"""

    def _prepare(content_test, content_expect, write_if):
        testname = caller_fname()
        write_if(testname+_TEST_SUFFIX+_SVG_EXT,
                 content_test,
                 newtest=testname)
        write_if(testname+_EXPECT_SUFFIX+_SVG_EXT, content_expect)
        infile = io.StringIO(content_test)
        svgdoc = INJ.SVGDocInScale(infile)
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

    def test_inject_into_layer(self, write_if_svgout):
        vbox = '0 10 90.71 68.03'
        content_test = Test_SVGDocInScale.TEM1 % (vbox,
            '<rect x="59.527" y="17.008"'
            ' width="25.512" height="39.685" fill="#8080C0" />')
        content_expect = Test_SVGDocInScale.TEM1 % (vbox,
            '<rect x="59.527" y="17.008"'
            ' width="25.512" height="39.685" fill="#8080C0" />'
            '<rect x="0" y="10" width="90.71" height="68.03"'
            ' fill="#00CC44" opacity="0.4" />'
            '<line x1="0" y1="10" x2="90.71" y2="78.03"'
            ' stroke="black" />')
        svgdoc = Test_SVGDocInScale._prepare(content_test,
                                             content_expect,
                                             write_if_svgout)
        world_horiz = (-10,20)
        world_left, world_right = world_horiz
        world_width = world_right - world_left
        world_vert = (0,40)
        world_top, world_bottom  = world_vert
        world_height = world_bottom - world_top
        injp = svgdoc.get_layer_injectpoint("Layer_A",
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

    def test_inject_into_rect(self, write_if_svgout):
        vbox = '0 10 90.71 68.03'
        content_test = Test_SVGDocInScale.TEM1 % (vbox,
            '<rect id="Rect_9" x="59.527" y="17.008"'
            ' width="25.512" height="39.685" fill="#8080C0" />')
        newrect = ('<rect x="59.527" y="17.008" width="25.512"'
                   ' height="39.685" fill="#C0C080" opacity="0.4" />')
        newline = ('<line x1="59.527" y1="17.008" x2="85.039"'
                   ' y2="56.693" stroke="black" />')
        after_injection = (
            '<g id="INJ_Rect_9">'
            # The inject rect gets semi-transparent after injection
            '<rect id="Rect_9" x="59.527" y="17.008" width="25.512"'
            ' height="39.685" fill="#8080C0" opacity="0.452"/>' +
            newrect+newline + '</g>')
        content_expect = Test_SVGDocInScale.TEM1 % (vbox,
                                                    after_injection)
        svgdoc = Test_SVGDocInScale._prepare(content_test,
                                             content_expect,
                                             write_if_svgout)
        world_left, world_width = (59.527, 25.512)
        world_right = world_left + world_width
        world_top, world_height = (17.008, 39.685)
        world_bottom = world_top + world_height
        injp = svgdoc.get_rect_injectpoint("Rect_9",
                                           (world_left, world_right),
                                           (world_top, world_bottom))
        x1doc = injp.h2x(world_left)
        y1doc = injp.v2y(world_top)
        x2doc = injp.h2x(world_right)
        y2doc = injp.v2y(world_bottom)
        injp.inject(newrect)
        injp.inject(newline)
        Test_SVGDocInScale._save_result(svgdoc,
                                        content_expect,
                                        write_if_svgout)


    _POLY_POINTS = ('931,2169.304 817.627,2169.285'
                    ' 770.96,2169.285 667.874,2307.31 539.317,2191.927'
                    ' 229.269,2186.255 165,2169.304 57.23,2292.125 '
                    ' 57.23,2452.75 930.978,2452.75')

    def _two_poly(tag, points, points_after, addons):
        _POLY_TEM = '<%s id="Poly1" points="%s" %s/>'
        return (_POLY_TEM % (tag, points, addons),
                _POLY_TEM % (tag, points_after, addons))

    def test_inject_points_polygon(self, write_if_svgout):
        vbox = '0 2100 1200 300'
        addons = 'fill="#2E2" stroke="#122" stroke-width="10"'
        poly, poly_after = Test_SVGDocInScale._two_poly("polygon",
                           Test_SVGDocInScale._POLY_POINTS,
                           '900.54,2000 ' +
                           Test_SVGDocInScale._POLY_POINTS +
                           ' 870,2600.338', addons)
        content_test = Test_SVGDocInScale.TEM1 % (vbox, poly)
        content_expect = Test_SVGDocInScale.TEM1 % (vbox, poly_after)
        svgdoc = Test_SVGDocInScale._prepare(content_test,
                                             content_expect,
                                             write_if_svgout)
        injp = svgdoc.get_poly_injectpoint("polygon", "Poly1")
        injp.inject_points([(900.54, 2000)], INJ.INJ_POS_BEFORE)
        injp.inject_points([(870, 2600.338)], INJ.INJ_POS_AFTER)
        Test_SVGDocInScale._save_result(svgdoc,
                                        content_expect,
                                        write_if_svgout)

    def test_inject_points_polyline(self, write_if_svgout):
        vbox = '0 2100 1200 300'
        addons = 'fill="#2E2" stroke="#122" stroke-width="10"'
        poly, poly_after = Test_SVGDocInScale._two_poly("polyline",
                           Test_SVGDocInScale._POLY_POINTS,
                           '900.54,2000 ' +
                           Test_SVGDocInScale._POLY_POINTS +
                           ' 870,2600.338',
                           addons)
        content_test = Test_SVGDocInScale.TEM1 % (vbox, poly)
        content_expect = Test_SVGDocInScale.TEM1 % (vbox, poly_after)
        svgdoc = Test_SVGDocInScale._prepare(content_test,
                                             content_expect,
                                             write_if_svgout)
        injp = svgdoc.get_poly_injectpoint("polyline", "Poly1")
        injp.inject_points([(900.54, 2000)],
                           pos=INJ.INJ_POS_BEFORE)
        injp.inject_points([(870, 2600.338)],
                           pos=INJ.INJ_POS_AFTER)
        Test_SVGDocInScale._save_result(svgdoc,
                                        content_expect,
                                        write_if_svgout)

    def test_inject_points_polyline_trafo(self, write_if_svgout):
        vbox = '0 0 200 200'
        addons = 'fill="#2EC" stroke="#C0D" stroke-width="3" opacity="0.7"'
        rect = '<rect id="Rect1" x="10" y="30" width="150" height="75" />'
        poly, poly_after = Test_SVGDocInScale._two_poly("polyline",
                           '0,0 100,0 100,10',
                           '0,0 100,0 100,10 10,30 160,105 160,30 10,105',
                           addons)
        content_test = Test_SVGDocInScale.TEM1 % (vbox, rect+poly)
        content_expect = Test_SVGDocInScale.TEM1 % (vbox, rect+poly_after)
        svgdoc = Test_SVGDocInScale._prepare(content_test,
                                             content_expect,
                                             write_if_svgout)
        world_horiz = 1000, 2000
        world_vert = 10, 30
        world_left, world_right = world_horiz
        world_top, world_bottom  = world_vert
        trafo = svgdoc.trafo_from_rect("Rect1", world_horiz, world_vert)
        injp = svgdoc.get_poly_injectpoint("polyline", "Poly1")
        injp.inject_points([(world_left,world_top),
                            (world_right,world_bottom),
                            (world_right,world_top),
                            (world_left,world_bottom)],
                            trafo=trafo)
        Test_SVGDocInScale._save_result(svgdoc,
                                        content_expect,
                                        write_if_svgout)

    def test_insert_points_polyline_trafo(self, write_if_svgout):
        vbox = '0 0 200 200'
        addons = 'fill="#2EC" stroke="#C0D" stroke-width="3" opacity="0.7"'
        rect = '<rect id="Rect1" x="10" y="30" width="150" height="75" />'
        poly, poly_after = Test_SVGDocInScale._two_poly("polyline",
                           '0,0 100,0 100,10 10,30 10,105',
                           '0,0 100,0 100,10 10,30 160,105 160,30 10,105',
                           addons)
        content_test = Test_SVGDocInScale.TEM1 % (vbox, rect+poly)
        content_expect = Test_SVGDocInScale.TEM1 % (vbox, rect+poly_after)
        svgdoc = Test_SVGDocInScale._prepare(content_test,
                                             content_expect,
                                             write_if_svgout)
        world_horiz = 1000, 2000
        world_vert = 10, 30
        world_left, world_right = world_horiz
        world_top, world_bottom  = world_vert
        trafo = svgdoc.trafo_from_rect("Rect1", world_horiz, world_vert)
        injp = svgdoc.get_poly_injectpoint("polyline", "Poly1")
        injp.inject_points_at([(world_right,world_bottom),
                               (world_right,world_top)],
                              index=4, trafo=trafo)
        Test_SVGDocInScale._save_result(svgdoc,
                                        content_expect,
                                        write_if_svgout)

    def test_replace_point_polyline_trafo(self, write_if_svgout):
        vbox = '0 0 200 200'
        addons = 'fill="#2CE" stroke="#C0D" stroke-width="3" opacity="0.7"'
        rect = '<rect id="Rect1" x="10" y="30" width="150" height="75" />'
        poly, poly_after = Test_SVGDocInScale._two_poly("polyline",
                                    '10,30 160,30 160,105 10,105',
                                    '10,30 85,105 160,30 10,105',
                                    addons)
        content_test = Test_SVGDocInScale.TEM1 % (vbox, rect+poly)
        content_expect = Test_SVGDocInScale.TEM1 % (vbox, rect+poly_after)
        svgdoc = Test_SVGDocInScale._prepare(content_test,
                                             content_expect,
                                             write_if_svgout)
        world_horiz = 1000, 2000
        world_vert = 10, 30
        world_left, world_right = world_horiz
        world_midx = (world_right + world_left) / 2.0
        world_top, world_bottom  = world_vert
        trafo = svgdoc.trafo_from_rect("Rect1", world_horiz, world_vert)
        injp = svgdoc.get_poly_injectpoint("polyline", "Poly1")
        injp.replace_point_at((world_midx,world_bottom),
                              index=1, trafo=trafo)
        injp.replace_point_at((world_right,world_top),
                              index=-2, trafo=trafo)
        Test_SVGDocInScale._save_result(svgdoc,
                                        content_expect,
                                        write_if_svgout)

    def test_replace_all_points(self, write_if_svgout):
        vbox = '0 0 200 200'
        addons = 'fill="#3dd" stroke="#C0D" stroke-width="3" opacity="0.7"'
        rect = '<rect id="Rect1" x="10" y="30" width="150" height="75" />'
        poly, poly_after = Test_SVGDocInScale._two_poly("polyline",
                                    '50,30 60,80 80,5 100,105',
                                    '10,30 160,105 160,30 10,105',
                                    addons)
        content_test = Test_SVGDocInScale.TEM1 % (vbox, rect+poly)
        content_expect = Test_SVGDocInScale.TEM1 % (vbox, rect+poly_after)
        svgdoc = Test_SVGDocInScale._prepare(content_test,
                                             content_expect,
                                             write_if_svgout)
        world_horiz = 1000, 2000
        world_vert = 10, 30
        world_left, world_right = world_horiz
        world_top, world_bottom  = world_vert
        trafo = svgdoc.trafo_from_rect("Rect1", world_horiz, world_vert)
        injp = svgdoc.get_poly_injectpoint("polyline", "Poly1")
        injp.replace_all_points([(world_left,world_top),
                                 (world_right,world_bottom),
                                 (world_right,world_top),
                                 (world_left,world_bottom)],
                                trafo=trafo)
        Test_SVGDocInScale._save_result(svgdoc,
                                        content_expect,
                                        write_if_svgout)

    def test_replace_all_points_deltafn(self, write_if_svgout):
        vbox = '0 0 200 200'
        addons = 'fill="#3dd" stroke="#A28" stroke-width="3" opacity="0.7"'
        rect = '<rect id="Rect1" x="10" y="30" width="150" height="75" />'
        poly, poly_after = Test_SVGDocInScale._two_poly("polyline",
                                    '50,30 60,80 80,5 100,105',
                                    '10,30 160,105 160,30 10,105',
                                    addons)
        content_test = Test_SVGDocInScale.TEM1 % (vbox, rect+poly)
        content_expect = Test_SVGDocInScale.TEM1 % (vbox, rect+poly_after)
        svgdoc = Test_SVGDocInScale._prepare(content_test,
                                             content_expect,
                                             write_if_svgout)
        world_horiz = 1000,2000
        world_vert = 10, 30
        world_left, world_right = world_horiz
        world_top, world_bottom  = world_vert
        trafo = svgdoc.trafo_from_rect("Rect1", world_horiz, world_vert)
        injp = svgdoc.get_poly_injectpoint("polyline", "Poly1")
        # xxvarnamexx2: using datetime and a custom delta_h
        world_horiz2 = (datetime.datetime(2015,9,22),
                       datetime.datetime(2016,2,9))
        world_left2, world_right2 = world_horiz2
        trafo2 = svgdoc.trafo_from_rect("Rect1", world_horiz2, world_vert,
                            delta_h=lambda t1, t2:(t2-t1).total_seconds())
        with pytest.raises(TypeError):
            injp.replace_all_points([(world_left2,world_top),
                                     (world_right,world_bottom),
                                     (world_right,world_top),
                                     (world_left,world_bottom)])
        with pytest.raises(TypeError):
            injp.replace_all_points([(world_left,world_top),
                                     (world_right2,world_bottom),
                                     (world_right,world_top),
                                     (world_left,world_bottom)])
        injp.replace_all_points([(world_left2,world_top),
                                 (world_right2,world_bottom),
                                 (world_right2,world_top),
                                 (world_left2,world_bottom)],
                                trafo=trafo2)
        Test_SVGDocInScale._save_result(svgdoc,
                                        content_expect,
                                        write_if_svgout)

    def test_replace_all_points_flip_y(self, write_if_svgout):
        vbox = '0 0 200 200'
        addons = 'fill="#3dd" stroke="#C0D" stroke-width="3" opacity="0.7"'
        rect = '<rect id="Rect1" x="10" y="30" width="150" height="75" />'
        poly, poly_after = Test_SVGDocInScale._two_poly("polyline",
                                    '50,30 60,80 80,5 100,105',
                                    '10,30 10,105 160,105',
                                    addons)
        content_test = Test_SVGDocInScale.TEM1 % (vbox, rect+poly)
        content_expect = Test_SVGDocInScale.TEM1 % (vbox, rect+poly_after)
        svgdoc = Test_SVGDocInScale._prepare(content_test,
                                             content_expect,
                                             write_if_svgout)
        world_horiz = 1000, 2000
        world_vert = 10, 30
        world_left, world_right = world_horiz
        world_top, world_bottom  = world_vert
        trafo = svgdoc.trafo_from_rect("Rect1",
                                       world_horiz, world_vert,
                                       flip_y=True)
        injp = svgdoc.get_poly_injectpoint("polyline", "Poly1")
        injp.replace_all_points([(world_left,world_bottom),
                                 (world_left,world_top),
                                 (world_right,world_top)],
                                trafo=trafo)
        Test_SVGDocInScale._save_result(svgdoc,
                                        content_expect,
                                        write_if_svgout)
