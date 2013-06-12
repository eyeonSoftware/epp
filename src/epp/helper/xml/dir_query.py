#!/usr/bin/env python
#coding=utf-8
#? py

'''
dir_query.py
####################################

Querying directory structure xml files. Needs a 

:copyright: 2013 by eyeon Software Inc., see AUTHORS for more details
:license: Some rights reserved, see LICENSE for more details
'''
from __future__ import absolute_import

import os
import re
import sys

sys.path[0] = ".."

import lxml.etree as etree
#import elementtree.ElementTree as etree
#from elementtree import SimpleXMLTreeBuilder # part of your codebase
#etree.XMLTreeBuilder = SimpleXMLTreeBuilder.TreeBuilder

import epp.helper.xml.settings as settings

def lower_keys(x):
    if isinstance(x, list):
        return [lower_keys(v) for v in x]
    if isinstance(x, dict):
        return dict((k.lower(), lower_keys(v)) for k, v in x.iteritems())
    return x


# #############################################################################################
class DirQuery(object):
    """docstring for DirQuery"""
    # -------------------------------------------------------------------------------------
    # Attributes
    PAT_VAR = re.compile("[$](.+)[;]")
    PAT_ENVVAR = re.compile("[%](.+)[%]")
    # -------------------------------------------------------------------------------------
    def filepath():
        doc = "The filepath property to the path"
        def fget(self):
            return self._filepath
        def fset(self, value):
            self._filepath = value
        return locals()
    filepath = property(**filepath())

    # -------------------------------------------------------------------------------------
    def varfile():
        doc = "The varfile property."
        def fget(self):
            return self._varfile
        def fset(self, value):

            if value is None:
                return

            if os.path.isfile(value):
                self.varset = settings.XMLSettings( value )
            else:
                self.varset = None


            self._varfile = value
        return locals()
    varfile = property(**varfile())

    # -------------------------------------------------------------------------------------
    # Private
    # -------------------------------------------------------------------------------------
    def __init__(self, filepath, varfile=None, additional_vars = {}, additional_envvars = {}):
        super(DirQuery, self).__init__()
        self.varset = None
        self.filepath = filepath
        self.varfile = varfile
        self.additional_vars = lower_keys(additional_vars)
        self.additional_envvars = lower_keys(additional_envvars)

        if os.path.isfile(self.filepath):
            self._xml = etree.parse(self.filepath)
        else:
            self._xml = None

    # -------------------------------------------------------------------------------------
    def _parse_vars(self, name):
        """docstring for _parse_vars"""

        mat = self.PAT_VAR.match(name)
        if mat is not None:
            varname = mat.group(1)

            repl = self.additional_vars.get(varname.lower(), None)
        
            if repl is None and self.varset is not None:
                repl = self.varset.get("creationvars", varname)

            if repl is not None:
                name = self.PAT_VAR.subn(re.escape(repl), name)[0]

        mat = self.PAT_ENVVAR.match(name)
        if mat is not None:
            varname = mat.group(1)

            repl = self.additional_envvars.get(varname.lower(), None)

            if repl is None and self.varset is not None:
                repl = self.varset.get("creationenvvars", varname)

            if repl is not None:
                name = self.PAT_ENVVAR.subn(re.escape(repl), name)[0]

        return name
    

    # -------------------------------------------------------------------------------------
    def _iter_parent(self, child, parent_map, build_path):
        """docstring for _iter_parent"""

        if child in parent_map:
            return build_path.append( self._iter_parent(parent_map[child], parent_map, build_path) )

    # -------------------------------------------------------------------------------------
    # Public
    # -------------------------------------------------------------------------------------
    def get_path_raw(self, itemid):
        """docstring for get_path"""
        
        root_tag = self._xml.find(".//folder[@id='{0}']".format(itemid))
        if root_tag is None:
            return []

        parent_map = dict((c, p) for p in self._xml.getiterator() for c in p)

        path = [self._parse_vars(root_tag.attrib['name'])]
        cur_child = root_tag
        while cur_child in parent_map:
            cur_child = parent_map[cur_child]
            if cur_child.tag.lower() == "folder":
                path.append(self._parse_vars(cur_child.attrib['name']))

        path.reverse()
        return path

    # -------------------------------------------------------------------------------------
    def get_path(self, itemid, root=""):
        """docstring for get_path"""
        path = self.get_path_raw(itemid)

        if not len(path):
            return ""

        return os.path.join(root, *path)


if __name__ == '__main__':
    
    dq = DirQuery(r"D:\eyeon\repos\epp\src\epp\_templates\project_dirs\Project.xml", None, {'Projectname': 'hello'})

    print dq.get_path("output_folder")
