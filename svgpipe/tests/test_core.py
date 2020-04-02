import io

import pytest

import svgpipe
from svgpipe.tests.utils import SVGDocMaker, Testbild

class Test_SVGDoc:

    def test_get_viewbox(self):
        fileobject = io.StringIO(Testbild.minimal(
                            viewBox="0 0 2834.646 34.6"))
        svgdoc = svgpipe.SVGDoc(fileobject)
        x, y, w, h = svgdoc.get_viewbox()
        assert x==0.0
        assert y==0.0
        assert w==2834.646
        assert h==34.6

    def test_get_layer(self):
        fileobject = io.StringIO(Testbild.minimal(
                            L1_name="L1", L2_name="L2"))
        svgdoc = svgpipe.SVGDoc(fileobject)
        layer = svgdoc.get_layer("L1")
        assert type(layer) is not None
        layer = svgdoc.get_layer("L2")
        assert type(layer) is not None
        with pytest.raises(svgpipe.NotFoundError):
            svgdoc.get_layer("X")
