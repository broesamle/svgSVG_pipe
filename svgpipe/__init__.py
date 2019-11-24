import re
import xml.etree.ElementTree as ET

### This affects all modules also using ET :(
ET.register_namespace('',"http://www.w3.org/2000/svg")
ET.register_namespace('xlink',"http://www.w3.org/1999/xlink")

class ParseError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class NotFoundError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class SVGDoc(object):
    """ An existing SVG document.

    Allows to inject new SVG content which be provided as
    `xml.etree.ElementTree.Element` or string.
    """

    _NS = {'svg' :'http://www.w3.org/2000/svg'}

    def __init__(self, filename):
        self.tree = ET.parse(filename)
        self.root = self.tree.getroot()

    def get_viewbox(self):
        """ Get the `viewBox` of the toplevel (root) SVG element.

        Returns a sequence of the form `[x,y,width,height]`.
        """
        vbox = self.root.get('viewBox', None)
        if isinstance(vbox, str):
            coords = re.findall("([^ \t,]+)+", vbox)
            if len(coords) != 4:
                raise ParseError("viewBox coordinates not valid: %s" % vbox)
            return list(map(float, coords))
        elif vbox == None:
            return None
        else:
            raise ParseError("Unknown error while parsing viewBox coordinates: %s" % vbox)

    def get_layer(self, id):
        """ Get an SVG `g` element with the given `id`.

        Popular vector graphics applications interpret
        this pattern as a 'layer'.

        `id` must me a be a string.
        """
        return self.get_svg_element('g', id)

    def get_layers_as_dict(self, ids):
        """ Retrieve all 'layers' with given `ids`.

        'layer': cf. `get_layer`

        Returns a dict of `ElementTree.Element` instances.
        The returned dictionary maps each id to its corresponding
        SVG `g` element representing the layer.
        If no element is found, the corresponding id will not
        be in the dict.
        """
        xpath = "svg:g[@id]"
        result = {}
        for el in self.root.findall(xpath,
                                    SVGDoc._NS):
            id = el.get('id')
            if id in ids:
                if id in result:
                    raise ParseError("Duplicate element with id %s" % id)
                result[id] = el
        return result

    def get_svg_element(self, tag, id):
        """ Return the svg `tag` element with the given `id`.

        `tag` is the local svg tagname as a `str`, without
        any namespace prefixes. Examples: 'rect', 'g'.
        """
        xpath = ".//svg:%s[@id='%s']" % (tag,id)
        svgel = self.root.find(xpath, SVGDoc._NS)
        if svgel is None:
            raise NotFoundError("No '%s' element with id '%s' found."
                                % (tag,id))
        return svgel
