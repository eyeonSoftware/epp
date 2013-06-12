#!/usr/bin/env python
#coding=utf-8

'''
basexml.py
####################################

Base XML Helper function

:copyright: 2013 by eyeon Software Inc., see AUTHORS for more details
:license: Some rights reserved, see LICENSE for more details
'''

import lxml.etree as etree
import pprint
import sys


def xmlfile_to_dict(file):
    tree = etree.parse( file )
    root = tree.getroot()

    return etree_to_dict(root)


def etree_to_dict(el):

    d={}

    if not isinstance(el.tag, basestring):
        d["__Comment__"] = {}
        return d

    d[el.tag] = {}

    if el.attrib:
        d[el.tag]['attrib'] = el.attrib
    if el.text:
        d[el.tag]['content'] = el.text.strip()
    else:
        d[el.tag]['children'] = {}
    
    children = el.getchildren()
    
    if children:
        d[el.tag]['children'] = map(etree_to_dict, children)
    return d


if __name__ == '__main__':

    # Parse file from argument
    if len(sys.argv) > 1:
        _file = sys.argv[1]
        xml_dict = xmlfile_to_dict(_file)
        pprint.pprint(xml_dict)


