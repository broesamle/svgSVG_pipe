import datetime
import io

import pytest

import svgpipe
from svgpipe.tests.utils import SVGDocMaker, Testbild
from svgpipe.inject import INJ_POS_AFTER, INJ_POS_BEFORE

class Test_SVGDocInj:
    def test_get_poly_injectpoint(self):
        fileobject = io.StringIO(Testbild.minimal(
                            L1_content=('<polygon id="Poly1"/>',
                                        '<polyline id="Poly2"/>')))
        svgdoc = svgpipe.inject.SVGDocInj(fileobject)
        poly1 = svgdoc.get_poly_injectpoint('polygon',"Poly1")
        assert poly1 is not None
        poly2 = svgdoc.get_poly_injectpoint('polyline',"Poly2")
        assert poly2 is not None
        with pytest.raises(svgpipe.NotFoundError):
            svgdoc.get_poly_injectpoint("t","X")
        with pytest.raises(svgpipe.NotFoundError):
            svgdoc.get_poly_injectpoint("polygon","Poly2")
        with pytest.raises(svgpipe.NotFoundError):
            svgdoc.get_poly_injectpoint("polyline","Poly1")

    def test_inject_into_layer(self, write_if_svgout):
        vbox = '0 10 90.71 68.03'
        content_test = Testbild.minimal(viewBox=vbox,
                L1_content=(
                    '<rect x="59.527" y="17.008" width="25.512"'
                    ' height="39.685" fill="#8080C0" />'))
        content_expect = Testbild.minimal(viewBox=vbox,
                L1_content=(
                    '<rect x="59.527" y="17.008"'
                    ' width="25.512" height="39.685" fill="#8080C0" />'
                    '<rect x="0" y="10" width="90.71" height="68.03"'
                    ' fill="#00CC44" opacity="0.4" />'
                    '<line x1="0" y1="10" x2="90.71" y2="78.03"'
                    ' stroke="black" />'))
        svgdoc = SVGDocMaker.prepare_svgdoc(content_test, content_expect,
                                            write_if_svgout)
        world_horiz = (-10,20)
        world_left, world_right = world_horiz
        world_width = world_right - world_left
        world_vert = (0,40)
        world_top, world_bottom  = world_vert
        world_height = world_bottom - world_top
        injp = svgdoc.get_layer_injectpoint("L1", world_horiz, world_vert)
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
        SVGDocMaker.save_result(svgdoc, content_expect, write_if_svgout)

    def test_inject_into_rect(self, write_if_svgout):
        vbox = '0 10 90.71 68.03'
        content_test = Testbild.minimal(viewBox=vbox,
                L1_content=(
                    '<rect id="Rect_9" x="59.527" y="17.008"'
                    ' width="25.512" height="39.685" fill="#8080C0" />'))
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
        content_expect = Testbild.minimal(viewBox=vbox,
                                          L1_content=after_injection)
        svgdoc = SVGDocMaker.prepare_svgdoc(content_test, content_expect,
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
        SVGDocMaker.save_result(svgdoc, content_expect, write_if_svgout)

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
        poly, poly_after = Test_SVGDocInj._two_poly("polygon",
                           Test_SVGDocInj._POLY_POINTS,
                           '900.54,2000 ' +
                           Test_SVGDocInj._POLY_POINTS +
                           ' 870,2600.338', addons)
        content_test = Testbild.minimal(viewBox=vbox, L1_content=poly)
        content_expect = Testbild.minimal(viewBox=vbox,
                                          L1_content=poly_after)
        svgdoc = SVGDocMaker.prepare_svgdoc(content_test, content_expect,
                                            write_if_svgout)
        injp = svgdoc.get_poly_injectpoint("polygon", "Poly1")
        injp.inject_points([(900.54, 2000)], INJ_POS_BEFORE)
        injp.inject_points([(870, 2600.338)], INJ_POS_AFTER)
        SVGDocMaker.save_result(svgdoc, content_expect, write_if_svgout)

    def test_inject_points_polyline(self, write_if_svgout):
        vbox = '0 2100 1200 300'
        addons = 'fill="#2E2" stroke="#122" stroke-width="10"'
        poly, poly_after = Test_SVGDocInj._two_poly("polyline",
                           Test_SVGDocInj._POLY_POINTS,
                           '900.54,2000 ' +
                           Test_SVGDocInj._POLY_POINTS +
                           ' 870,2600.338',
                           addons)
        content_test = Testbild.minimal(viewBox=vbox, L1_content=poly)
        content_expect = Testbild.minimal(viewBox=vbox, L1_content=poly_after)
        svgdoc = SVGDocMaker.prepare_svgdoc(content_test, content_expect,
                                            write_if_svgout)
        injp = svgdoc.get_poly_injectpoint("polyline", "Poly1")
        injp.inject_points([(900.54, 2000)],
                           pos=INJ_POS_BEFORE)
        injp.inject_points([(870, 2600.338)],
                           pos=INJ_POS_AFTER)
        SVGDocMaker.save_result(svgdoc, content_expect, write_if_svgout)

    def test_inject_points_polyline_trafo(self, write_if_svgout):
        vbox = '0 0 200 200'
        addons = 'fill="#2EC" stroke="#C0D" stroke-width="3" opacity="0.7"'
        rect = '<rect id="Rect1" x="10" y="30" width="150" height="75" />'
        poly, poly_after = Test_SVGDocInj._two_poly("polyline",
                           '0,0 100,0 100,10',
                           '0,0 100,0 100,10 10,30 160,105 160,30 10,105',
                           addons)
        content_test = Testbild.minimal(viewBox=vbox, L1_content=rect+poly)
        content_expect = Testbild.minimal(viewBox=vbox,
                                          L1_content=rect+poly_after)
        svgdoc = SVGDocMaker.prepare_svgdoc(content_test, content_expect,
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
        SVGDocMaker.save_result(svgdoc, content_expect, write_if_svgout)

    def test_insert_points_polyline_trafo(self, write_if_svgout):
        vbox = '0 0 200 200'
        addons = 'fill="#2EC" stroke="#C0D" stroke-width="3" opacity="0.7"'
        rect = '<rect id="Rect1" x="10" y="30" width="150" height="75" />'
        poly, poly_after = Test_SVGDocInj._two_poly("polyline",
                           '0,0 100,0 100,10 10,30 10,105',
                           '0,0 100,0 100,10 10,30 160,105 160,30 10,105',
                           addons)
        content_test = Testbild.minimal(viewBox=vbox, L1_content=rect+poly)
        content_expect = Testbild.minimal(viewBox=vbox,
                                          L1_content=rect+poly_after)
        svgdoc = SVGDocMaker.prepare_svgdoc(content_test, content_expect,
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
        SVGDocMaker.save_result(svgdoc, content_expect, write_if_svgout)

    def test_replace_point_polyline_trafo(self, write_if_svgout):
        vbox = '0 0 200 200'
        addons = 'fill="#2CE" stroke="#C0D" stroke-width="3" opacity="0.7"'
        rect = '<rect id="Rect1" x="10" y="30" width="150" height="75" />'
        poly, poly_after = Test_SVGDocInj._two_poly("polyline",
                                    '10,30 160,30 160,105 10,105',
                                    '10,30 85,105 160,30 10,105',
                                    addons)
        content_test = Testbild.minimal(viewBox=vbox, L1_content=rect+poly)
        content_expect = Testbild.minimal(viewBox=vbox,
                                          L1_content=rect+poly_after)
        svgdoc = SVGDocMaker.prepare_svgdoc(content_test, content_expect,
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
        SVGDocMaker.save_result(svgdoc, content_expect, write_if_svgout)

    def test_replace_all_points(self, write_if_svgout):
        vbox = '0 0 200 200'
        addons = 'fill="#3dd" stroke="#C0D" stroke-width="3" opacity="0.7"'
        rect = '<rect id="Rect1" x="10" y="30" width="150" height="75" />'
        poly, poly_after = Test_SVGDocInj._two_poly("polyline",
                                    '50,30 60,80 80,5 100,105',
                                    '10,30 160,105 160,30 10,105',
                                    addons)
        content_test = Testbild.minimal(viewBox=vbox, L1_content=rect+poly)
        content_expect = Testbild.minimal(viewBox=vbox,
                                          L1_content=rect+poly_after)
        svgdoc = SVGDocMaker.prepare_svgdoc(content_test, content_expect,
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
        SVGDocMaker.save_result(svgdoc, content_expect, write_if_svgout)

    def test_replace_all_points_deltafn(self, write_if_svgout):
        vbox = '0 0 200 200'
        addons = 'fill="#3dd" stroke="#A28" stroke-width="3" opacity="0.7"'
        rect = '<rect id="Rect1" x="10" y="30" width="150" height="75" />'
        poly, poly_after = Test_SVGDocInj._two_poly("polyline",
                                    '50,30 60,80 80,5 100,105',
                                    '10,30 160,105 160,30 10,105',
                                    addons)
        content_test = Testbild.minimal(viewBox=vbox, L1_content=rect+poly)
        content_expect = Testbild.minimal(viewBox=vbox,
                                          L1_content=rect+poly_after)
        svgdoc = SVGDocMaker.prepare_svgdoc(content_test, content_expect,
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
        SVGDocMaker.save_result(svgdoc, content_expect, write_if_svgout)

    def test_replace_all_points_flip_y(self, write_if_svgout):
        vbox = '0 0 200 200'
        addons = 'fill="#3dd" stroke="#C0D" stroke-width="3" opacity="0.7"'
        rect = '<rect id="Rect1" x="10" y="30" width="150" height="75" />'
        poly, poly_after = Test_SVGDocInj._two_poly("polyline",
                                    '50,30 60,80 80,5 100,105',
                                    '10,30 10,105 160,105',
                                    addons)
        content_test = Testbild.minimal(viewBox=vbox,
                                        L1_content=rect+poly)
        content_expect = Testbild.minimal(viewBox=vbox,
                                          L1_content=rect+poly_after)
        svgdoc = SVGDocMaker.prepare_svgdoc(content_test, content_expect,
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
        SVGDocMaker.save_result(svgdoc, content_expect, write_if_svgout)
