#!/usr/bin/env python
#coding=utf-8

'''
filesystem.py
####################################



:copyright: 2013 by eyeon Software Inc., see AUTHORS for more details
:license: Some rights reserved, see LICENSE for more details
'''

import glob
import os
from epp.helper.shortcuts import shot_id_path, shot_root_path, project_root_path
import lxml.etree as etree


# -------------------------------------------------------------------------------------
def projects(rootdir):
    """docstring for projects"""
    project_list = []

    for root, dirs, files in os.walk(rootdir, topdown=True):
        cur_path = ""

        for name in files:
            if name.lower() == "project_config.xml":
                cur_path = root

                # Quit if the root is already in the list
                is_child = False
                for cur_project in project_list:
                    if root.startswith(cur_project):
                        is_child = True

                if not is_child:                        
                    name = root[len(rootdir):].strip(os.path.sep)
                    project_list.append((name, root, ))
                break

    return project_list

# -------------------------------------------------------------------------------------
def shots(rootdir, project):
    """docstring for shots"""
    project_shots = os.path.join(rootdir, project, "project_shots.xml")
    
    shot_root_dir = shot_root_path(project)

    shot_dict = {}
    if os.path.isfile(project_shots):
        with open(project_shots, 'rt') as f:
            tree = etree.parse(f)
            
            for item in tree.findall(".//shot"):

                shot_dir = os.path.join(shot_root_dir, item.text.strip('"'))
                if os.path.isdir(shot_dir):
                    shot_dict[item.attrib["name"]] = shot_dir
        
    return shot_dict


# -------------------------------------------------------------------------------------
def comps(project, shot):
    """docstring for comps"""
    comp_dir = shot_id_path(project, shot, "compositions")

    if os.path.isdir(comp_dir):
        return glob.glob(os.path.join(comp_dir, "*.comp"))
    
    return []

# -------------------------------------------------------------------------------------
def project_shot_from_path(filepath):
    """docstring for project_shot_from_file"""

    projectroot = project_root_path()
    all_projects = projects(projectroot)
    
    res = (None, None)
    for projectname, projectdir in all_projects:
        cur_shots = shots(projectroot, projectname)
        shotdir = shot_root_path(projectname)
        if filepath.lower().startswith(shotdir.lower()):

            filepath_end = filepath[len(shotdir):].strip(os.path.sep)
            curshot = None
            for shot in cur_shots:
                if filepath_end.lower().startswith(shot.lower()):
                    curshot = shot

            if curshot is not None:
                res = (projectname, curshot)

    return res

