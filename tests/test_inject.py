import io

from svgSVG_pipe import inject as INJ

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

class Test_ExistingDoc:
    def test_get_viewbox(self):
        fileobject = io.StringIO(svgdocument1)
        svgdoc = INJ.ExistingDoc(fileobject)
        x, y, w, h = svgdoc.get_viewbox()
        assert x==0.0
        assert y==0.0
        assert w==2834.646
        assert h==34.6
