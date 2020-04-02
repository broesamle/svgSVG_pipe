import io

import pytest

import svgpipe
import svgpipe.transfer as TRA
from svgpipe.tests.utils import SVGDocMaker, Testbild

class Test_Transfer:
    def _prepare_proto(attr_proto, attr_target, attr_target_after):
        vbox = '0 0 200 200'
        proto = ('<rect id="P" x="30" y="30" width="50" height="50" '
                 '%s />') % attr_proto
        target = ('<rect id="T" x="100" y="100" width="90" height="90" '
                 '%s />') % attr_target
        target_after = ('<rect id="T" x="100" y="100" width="90" height="90" '
                 '%s />') % attr_target_after
        content_test = Testbild.minimal(viewBox=vbox, L1_content=proto+target)
        content_expect = Testbild.minimal(viewBox=vbox,
                                          L1_content=proto+target_after)
        return content_test, content_expect

    def test_transfer_fill(self, write_if_svgout):
        content_test, content_expect = Test_Transfer._prepare_proto(
                 'fill="#2EC" stroke="#aad" stroke-width="15"',
                 'fill="#904" stroke="#5d4" stroke-width="8"',
                 'fill="#2EC" stroke="#5d4" stroke-width="8"')
        svgdoc = SVGDocMaker.prepare_svgdoc(content_test, content_expect,
                                            write_if_svgout)
        proto = svgdoc.get_svg_element('rect', 'P')
        target = svgdoc.get_svg_element('rect', 'T')
        TRA.apply_attribs([target], proto, ['fill'])
        SVGDocMaker.save_result(svgdoc, content_expect, write_if_svgout)
