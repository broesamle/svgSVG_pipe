""" Transfer content from one part to another within existing SVG documents."""

def apply_attribs(target_elements, prototype_element,
                  attribs=None):
    """ Transfer attributes from one element to a list of target elements.

    `target_elements`: List of target elements.
    `prototype_element`: SVG element of which the properties
        will be transfered to the targets.
    `attribs` (optional): List of attribute names to be transferred.
        If ommitted, a preselected list of attributes will be used.
    """

    if attribs is None:
        _attribs = ['fill', 'stroke', 'stroke-width']
    else:
        _attribs = attribs
    for t in target_elements:
        for a in _attribs:
            t.attrib[a] = prototype_element.attrib[a]
