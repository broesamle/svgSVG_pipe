import io

import pytest

import svgpipe
import svgpipe.transfer as TRA
import svgpipe.tests.utils as TU

class Test_SVGDocInj(TU.SVGDoc_Tester):
    TEM1 = """<?xml version='1.0' encoding='utf-8'?>
<svg version="1.2" baseProfile="tiny" xmlns="http://www.w3.org/2000/svg"
 x="0px" y="0px" width="90.71px" height="68.03px" viewBox="%s">
<g id="Layer_B"></g>
<g id="Layer_A">%s</g>
</svg>
"""

    def _prepare_proto(attr_proto, attr_target, attr_target_after):
        vbox = '0 0 200 200'
        proto = ('<rect id="P" x="30" y="30" width="50" height="50" '
                 '%s />') % attr_proto
        target = ('<rect id="T" x="100" y="100" width="90" height="90" '
                 '%s />') % attr_target
        target_after = ('<rect id="T" x="100" y="100" width="90" height="90" '
                 '%s />') % attr_target_after
        content_test = TU.SVGDoc_Tester.TEM1 % (
                                vbox, proto+target)
        content_expect = TU.SVGDoc_Tester.TEM1 % (
                                vbox, proto+target_after)
        return content_test, content_expect

    def test_transfer_fill(self, write_if_svgout):
        content_test, content_expect = Test_SVGDocInj._prepare_proto(
                 'fill="#2EC" stroke="#aad" stroke-width="15"',
                 'fill="#904" stroke="#5d4" stroke-width="8"',
                 'fill="#2EC" stroke="#5d4" stroke-width="8"')
        svgdoc = Test_SVGDocInj._prepare_svgdoc(
                        content_test,
                        content_expect,
                        write_if_svgout)
        proto = svgdoc.get_svg_element('rect', 'P')
        target = svgdoc.get_svg_element('rect', 'T')
        TRA.apply_attribs([target], proto, ['fill'])
        Test_SVGDocInj._save_result(svgdoc,
                                    content_expect,
                                    write_if_svgout)
