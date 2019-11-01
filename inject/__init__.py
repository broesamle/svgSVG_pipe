""" Inject SVG content into existing SVG files.

Relies on `xml.etree.ElementTree` (in short `ET`)
for SVG/XML element representation.
"""

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

class ExistingDoc(object):
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
            coords = re.findall("([^\s,]+)+", vbox)
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
        ### FIXME: Throw NotFoundError instead of returning None
        xpath = ".//svg:g[@id='%s']" % id
        return self.root.find(xpath, ExistingDoc._NS)

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
                                    ExistingDoc._NS):
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
        return self.root.find(xpath, ExistingDoc._NS)

    def save(self, file):
        self.tree.write(file, encoding="utf8")

class SVGDocInScale(ExistingDoc):
    """ Inject graphical content into an existing SVG document.

    An `InjectPoint` can be obtained via `*_injectpoint`
    methods. Multiple injectpoints can be used simultaneously.
    """

    def get_layer_injectpoint(self, id, hrange, vrange,
                              group=None, **delta_hv):
        """ Get a `ScaledInjectPoint` for injecting content.

            The element for injection will be the SVG `g`
            element representing the layer with the given `id`.

            Transformation parameters will be based on the
            document's top-level element's `viewBox` and the
            given ranges.

            `hrange`, `vrange`, `delta_h`, `delta_v`:
            cf. WorldDocTrafo.
            """
        target_el = self.get_layer(id)
        if not target_el:
            raise NotFoundError("No Layer with id=%s" % id)
        ### if group element is given, insert it as inj. target
        if group is not None:
            g = ET.fromstring(group)
            target_el.append(g)
            target_el = g
        return ScaledInjectPoint(target_el,
                                 self.get_viewbox(),
                                 hrange, vrange,
                                 **delta_hv)

    def get_rect_injectpoint(self, id, hrange, vrange, **delta_hv):
        def _rect2group(svgelement, newattribs):
            # FIXME:
            # To just rename the tag rather than cleanly create
            # a new element is certainly not polite towards
            # the ethos of engineering.
            # However, it avoids finding parents and indices,
            # which is not straightforward in ElementTree.
            svgelement.tag = svgelement.tag.replace('rect','g')
            svgelement.attrib = newattribs
            return svgelement

        target_el = self.get_svg_element('rect', id)
        if target_el is None:
            raise NotFoundError("No `rect` element with id=%s" % id)
        vbox = list(map(float, (target_el.attrib['x'],
                                target_el.attrib['y'],
                                target_el.attrib['width'],
                                target_el.attrib['height'])))
        injectrect_copy = ET.fromstring(ET.tostring(target_el))
        injectrect_copy.attrib['opacity'] = "0.452"
        target_el = _rect2group(target_el,
                                {'id': "INJ_%s" % id})
        target_el.append(injectrect_copy)
        return ScaledInjectPoint(target_el, vbox,
                                 hrange, vrange, **delta_hv)

class WorldDocTrafo(object):
    """ Transform world coords into document coordinates.

    Convention:

    `h`, `v`: horizontal and vertical coords in some
        world/source/data/user-chosen coordinate system
        Horizontal and vertical world coords can have
        different (physical) units; which corresponds to s
        eparate scale factors for each dimension.
        World coordinates have to be numbers without unit.

    `x`, `y`: document coordinates as they will
        appear in the final SVG document. The default unit of the
        document is assumed to be pixels.

    `__init__` dynamically creates the tranformation functions
        `h2x` and `v2y` as instance properties (not methods!).
        Alternative delta calculation functions can be defined.
        """

    def __init__(self, viewbox, hrange, vrange,
                 delta_h=None, delta_v=None):
        """ Initialize scale factors and transformation functions.

        `viewbox`:  SVG canonical form `(x,y,width,height)`
            but with x, y, width, and height being `float`.

        `hrange`, `vrange`:
            A 'view' on the data (world coords).

        `delta_h`, `delta_v` (optional): If defined they
            override the canonical difference operation `-` for
            delta calculation on world coordinates.
            This can be useful for cases where the built-in `-`
            is not suitable such as for non-trivial numeric
            representations with, say, python's `datetime` and
            `timedelta` which needs conversion for further
            calculations.
            """
        ### Define the View on the data: horizontal, vertical
        self.h1, self.h2 = hrange
        self.v1, self.v2 = vrange
        ### document dimensions: x, y
        self.x1, self.y1, width, height = viewbox
        ### init scale factors and transformation functions
        if delta_h is not None:
            # non-trivial delta calculation function
            self.hx_factor = width / delta_h(self.h1, self.h2)
            self.h2x = lambda h,                 \
                              h1=self.h1,        \
                              x1=self.x1,        \
                              sc=self.hx_factor, \
                              d=delta_h : d(h1,h)*sc + x1
        else:
            # use simple and fast `-`
            self.hx_factor = width / (self.h2-self.h1)
            self.h2x = lambda h,           \
                              h1=self.h1,  \
                              x1=self.x1,  \
                              sc=self.hx_factor : (h-h1)*sc + x1

        if delta_v is not None:
            # non-trivial delta calculation function
            self.vy_factor = heigth / delta_v(self.v1, self.v2)
            self.v2y = lambda v,                 \
                              v1=self.v1,        \
                              y1=self.y1,        \
                              sc=self.vy_factor, \
                              d=delta_v : d(v1,v)*sc + y1
        else:
            # use simple and fast `-`
            self.vy_factor = height / (self.v2-self.v1)
            self.v2y = lambda v,          \
                              v1=self.v1, \
                              y1=self.y1, \
                              sc=self.vy_factor : (v-v1)*sc + y1

    def h2x(h):
        """ Horizontal world coords `h` --> document x-coordinates.

        This stub will be replaced by __init__.
        """
        raise Exception("Internal error: h2x was not initialized properly. Please contact the administrator ,-)")

    def v2y(v):
        """ Vertical world coords `v` --> document y-coordinates.

        This stub will be replaced by __init__.
        """
        raise Exception("Internal error: h2x was not initialized properly. Please contact the administrator ,-)")

class ScaledInjectPoint(WorldDocTrafo):
    """ Scale and inject SVG content into a target area/element.

        `ScaledInjectPoint` is derived from `WorldDocTrafo`
        and combines a target SVG element with specific scaling
        parameters for injecting content into a rectangular
        target area (e.g. derived from the geometry of the `rect`
        element or its `viewBox`).
        """

    def __init__(self, target_element, viewBox, hrange, vrange,
                 **delta_hv):
        """ Extends `WorldDocTrafo.__init__`.

        `target_element`: An SVG element defining
            the point where new conted will get injected.
        """
        super().__init__(viewBox, hrange, vrange, **delta_hv)
        self.target = target_element

    def inject(self, content):
        """Inject SVG content provided as `str` or `ET.Element`."""
        if isinstance(content, ET.Element):
            self.target.append(inj)
        else:
            try:
                self.target.append(ET.fromstring(content))
            except (ET.ParseError, TypeError) as e:
                raise ParseError("Invalid type or syntax for content %s" % content)
