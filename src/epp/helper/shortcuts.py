#!/usr/bin/env python
#coding=utf-8
#? py

'''
shortcuts.py
####################################



:copyright: 2013 by eyeon Software Inc., see AUTHORS for more details
:license: Some rights reserved, see LICENSE for more details
'''
import glob
import os

from epp.helper.xml.dir_query import DirQuery
import epp.helper.osplus as osplus
import epp.helper.xml.settings as settings
from epp.model.format import format_from_dict

# -------------------------------------------------------------------------------------
def project_format(projectname):
    """docstring for project_format"""
    epp_root = osplus.get_env("EPP_ROOT")

    cur_settings = settings.XMLSettings(os.path.join(epp_root, "config.xml") )
    project_root = cur_settings.get("paths", "projectdir", None)

    project_settings = settings.XMLSettings(os.path.join(project_root, projectname, "project_config.xml") )

    fields = ("name", "width", "height", "framerate", "aspectx", "aspecty",)

    format_dict = {}

    for field in fields:
        format_dict[field] = project_settings.get("format", field)

    return format_dict        

# -------------------------------------------------------------------------------------
def project_format_object(projectname):
    """docstring for project_format_object"""
    format_dict = project_format(projectname)

    return format_from_dict(format_dict)

# -------------------------------------------------------------------------------------
def project_root_path():
    """docstring for project_root"""
    epp_root = osplus.get_env("EPP_ROOT")

    cur_settings = settings.XMLSettings(os.path.join(epp_root, "config.xml") )
    project_root = cur_settings.get("paths", "projectdir", None)

    return project_root

# -------------------------------------------------------------------------------------
def project_path(projectname):
    """docstring for shot"""

    project_root = project_root_path()
    project_dir = os.path.join(project_root, projectname)

    if not os.path.isdir(project_dir):
        return ""

    return project_dir

# -------------------------------------------------------------------------------------
def project_id_path(projectname, id_):
    """docstring for shot"""

    project_root = project_root_path()
    project_dir = project_path(projectname)

    if not os.path.isdir(project_dir):
        return ""

    project_template = os.path.join(project_dir, "project_template.xml")
    project_vars = os.path.join(project_dir, "project_vars.xml")

    if not os.path.isfile(project_template) or not os.path.isfile(project_vars):
        return ""

    dq = DirQuery(project_template, project_vars)
    id_path = dq.get_path(id_, project_root)

    return id_path

# -------------------------------------------------------------------------------------
def shot_path(projectname, shotname):
    """docstring for shot"""

    shot_root = project_id_path(projectname, "shots")
    shot_dir = os.path.join(shot_root, shotname)

    if not os.path.isdir(shot_dir):
        return ""

    return shot_dir

# -------------------------------------------------------------------------------------
def shot_root_path(projectname):
    """docstring for shot"""

    shot_root = project_id_path(projectname, "shots")

    if not os.path.isdir(shot_root):
        return ""

    return shot_root

# -------------------------------------------------------------------------------------
def shot_id_path(projectname, shotname, id_):
    """docstring for shot_id_path"""
    shot_dir = shot_path(projectname, shotname)
    shot_root_dir = shot_root_path(projectname)

    if not os.path.isdir(shot_dir):
        return ""

    shot_template = os.path.join(shot_dir, "shot_template.xml")
    shot_vars = os.path.join(shot_dir, "shot_vars.xml")

    if not os.path.isfile(shot_template) or not os.path.isfile(shot_vars):
        return ""

    dq = DirQuery(shot_template, shot_vars)
    id_path = dq.get_path(id_, shot_root_dir)

    return id_path

# -------------------------------------------------------------------------------------
def main():
    """docstring for main"""
    print shot_id_path("ReleaseTest01","Animatic\\220", "compositions") 

if __name__ == '__main__':
    main()    
