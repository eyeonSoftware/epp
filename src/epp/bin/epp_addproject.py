#!/usr/bin/env python
#coding=utf-8
#? py

'''
epp-addproject.py
####################################

Add a project control script

:copyright: 2013 by eyeon Software Inc., see AUTHORS for more details
:license: Some rights reserved, see LICENSE for more details
'''

import os
import shutil

from epp.helper.xml.dir import StructHandler
import epp.helper.osplus as osplus
import epp.helper.xml.settings as settings
from epp.model.format import Format

# -------------------------------------------------------------------------------------
def create_generation(projectname, project_dir, project_root_dir, gen):
    """docstring for create_generation"""

    # TODO: With new build.
    
    if not gen.status(True):
        return (False, "Generation not running.")


    return gen.create_project(projectname, project_dir, project_root_dir)

# -------------------------------------------------------------------------------------
def add_project(name, template, project_format, gen):
    """docstring for add_project"""

    epp_root = osplus.get_env("EPP_ROOT")

    if not os.path.isdir(epp_root):
        return (False, "Could not find EPP ROOT directory. Set the EPP_ROOT env variable first.", )

    cur_settings = settings.XMLSettings(os.path.join(epp_root, "config.xml") )
    project_root_dir = cur_settings.get("paths", "projectdir", None)

    if project_root_dir is None:
        return (False, "Don't know the project root dir. Please set it in your config.xml first.", )

    project_dir = os.path.join(project_root_dir, name)

    if os.path.isdir(project_dir):
        return (False, "Project folder '{0}' already exists.".format(name),)

    template_filepath = os.path.join(epp_root, "templates", "project_dirs", template)
    
    if not os.path.isfile(template_filepath):
        return (False, "Template '{0}' does not exists".format(template))

    args = project_format.to_dict("format_")
    args["PROJECTNAME"] = name


    sh = StructHandler(template_filepath, project_root_dir, False, True, args)

    # We save all input variables for later path reconstruction
    # We don't save all env vars though
    proj_settings = settings.XMLSettings(os.path.join(project_dir, "project_vars.xml") )
    for key, value in args.items():
        proj_settings.set("creationvars", key, str(value))
    for key, value in sh.used_environ.items():
        proj_settings.set("creationenvars", key, str(value))
    #print(template_filepath, project_dir, False, True, args)

    # Copy the template for reference
    shutil.copy(template_filepath, os.path.join(project_dir, "project_template.xml"))

    ret = create_generation(name, project_dir, project_root_dir, gen)
    if not ret[0]:
        return ret

    return (True, '{0} successfully created.'.format(name))

#print add_project("hello", "project.xml", Format(123, 240, 24, 1.0, 1.0, "Hello"))
