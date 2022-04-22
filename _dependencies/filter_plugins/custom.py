#!/usr/bin/env python

from ansible.utils.display import Display
from ansible.template import AnsibleUndefined
from io import BytesIO

display = Display()


# Create an aggregation on aggkeys (which may be a nested key) within the dictarr array of dicts.  Differs from the builtin jinja2 filter 'groupby' in that it returns a dict for each aggregation, rather than putting it at array elem 0.
def dict_agg(dictarr, aggkeys):
    import json
    results = {}

    if dictarr:
        for dictItem in dictarr:
            newDictItem = dictItem
            for aggkey in aggkeys.split('.'):
                if aggkey in newDictItem:
                    newDictItem = newDictItem[aggkey]
                else:
                    newDictItem = None
                    break
            if newDictItem:
                if newDictItem not in results:
                    results[newDictItem] = []

                results[newDictItem].append(dictItem)

    return json.dumps(results, indent=4)


# Return extra_vars string (i.e. what the command line expects for 'extra' vars) from a dict of extra variables
def extravars_from_dict(extravars_dict):
    import json
    if type(extravars_dict) is dict:
        return " ".join(["-e " + k + "='" + json.dumps(v, separators=(',', ':')) + "'" for k, v in extravars_dict.items()])
    else:
        if type(extravars_dict) != AnsibleUndefined:
            display.warning(u"extravars_from_dict - WARNING: could not parse extravars as dict")
        return ""


# Return the ASCII character for a given ordinal character code
def tochr(i):
    return chr(i)


# Query an XML string for specific elements
def xpath(xmlstr, xpath, namespaces=None):
    from ansible import errors
    try:
        from lxml import etree
    except ImportError:
        raise errors.AnsibleFilterError("Error: The `lxml` module is required")

    if not xpath:
        raise errors.AnsibleFilterError("Error: xpath not defined")

    xml = etree.parse(BytesIO(xmlstr.encode('utf-8')), etree.XMLParser(remove_blank_text=False))
    # display.warning(u"xml type: %s" % type(xml))

    ## If this is an array of strings (if the user has parsed out the final leaf node), then return the string; otherwise return the xml.tostring() value (ansible cannot use the native etree Element type anyway)
    xpath_res = xml.xpath(xpath, namespaces=namespaces, smart_strings=False)
    return [xpath_elem if type(xpath_elem) is str else etree.tostring(xpath_elem).decode() for xpath_elem in xpath_res]


# From https://stackoverflow.com/a/10077069/12491741
# Converts XML to dict using the 'official' (reversible) spec in http://www.xml.com/pub/a/2006/05/31/converting-between-xml-and-json.html
# Note: doesn't handle namespaces.
def xml_to_dict(xmlstr):
    from collections import defaultdict
    from xml.etree import ElementTree as ET
    import xmltodict

    # return xmltodict.parse(xmlstr)

    def etree_to_dict(t):
        d = {t.tag: {} if t.attrib else None}
        children = list(t)
        if children:
            dd = defaultdict(list)
            for dc in map(etree_to_dict, children):
                for k, v in dc.items():
                    dd[k].append(v)
            d = {t.tag: {k: v for k, v in dd.items()}}  # Everything is a python list, because we can't tell whether an XML element sometimes might defined more than once...
            # d = {t.tag: {k: v[0] if len(v) == 1 else v for k, v in dd.items()}}
        if t.attrib:
            d[t.tag].update(('@' + k, v) for k, v in t.attrib.items())
        if t.text:
            text = t.text.strip()
            if children or t.attrib:
                if text:
                    d[t.tag]['#text'] = text
            else:
                d[t.tag] = text
        return d

    return etree_to_dict(ET.fromstring(xmlstr))


# From https://stackoverflow.com/a/10077069/12491741
# Converts dict back to XML
def dict_to_xml(d):
    from xml.etree import ElementTree as ET
    try:
        basestring
    except NameError:  # python3
        basestring = str

    # https://stackoverflow.com/a/65808327/12491741
    def _pretty_print(current, parent=None, index=-1, depth=0, space="    "):
        for i, node in enumerate(current):
            _pretty_print(node, current, i, depth + 1)
        if parent is not None:
            if index == 0:
                parent.text = '\n' + (space * depth)
            else:
                parent[index - 1].tail = '\n' + (space * depth)
            if index == len(parent) - 1:
                current.tail = '\n' + (space * (depth - 1))

    def _to_etree(d, root):
        if not d:
            pass
        elif isinstance(d, basestring):
            root.text = d
        elif isinstance(d, dict):
            for k, v in d.items():
                assert isinstance(k, basestring)
                if k.startswith('#'):
                    assert k == '#text' and isinstance(v, basestring)
                    root.text = v
                elif k.startswith('@'):
                    assert isinstance(v, basestring)
                    root.set(k[1:], v)
                elif isinstance(v, list):
                    for e in v:
                        _to_etree(e, ET.SubElement(root, k))
                else:
                    _to_etree(v, ET.SubElement(root, k))
        else:
            raise TypeError('invalid type: ' + str(type(d)))

    assert isinstance(d, dict) and len(d) == 1
    tag, body = next(iter(d.items()))
    node = ET.Element(tag)
    _to_etree(body, node)

    _pretty_print(node)
    return ET.tostring(node).decode()


class FilterModule(object):
    def filters(self):
        return {
            'dict_agg': dict_agg,
            'extravars_from_dict': extravars_from_dict,
            'xpath': xpath,
            'tochr': tochr,
            'xml_to_dict': xml_to_dict,
            'dict_to_xml': dict_to_xml
        }
