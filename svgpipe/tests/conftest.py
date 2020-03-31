import codecs
import os
import pytest

@pytest.fixture(scope="session")
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
