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

from epp.helper.xml.dir_query import DirQuery
from epp.helper.xml.dir import StructHandler
import epp.helper.osplus as osplus
import epp.helper.xml.settings as settings
from epp.model.format import Format
from PySide.QtGui import QPixmap, QPainter, QColor, QFont, QApplication
from PySide.QtCore import Qt

# -------------------------------------------------------------------------------------
def tag_image(source, dest, tag, font, fontsize, x, y, width, height, aspectx, aspecty, red, green, blue, bold=False, italic=False):
    """docstring for tag_image"""

    app = QApplication.instance()
    
    pixmap = QPixmap(source)

    color = QColor(red,green,blue)
    font = QFont(font)
    font.setPixelSize(int(fontsize*pixmap.height()))
    font.setItalic(italic)
    font.setBold(bold)

    painter = QPainter(pixmap)
    painter.setPen(color)
    painter.setFont(font);
    painter.drawText(x*pixmap.width(),y*pixmap.height(), tag)
    painter.end()

    # Resize and save
    return pixmap.toImage().scaled(width*aspectx, height*aspecty, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation).scaled(width, height, Qt.IgnoreAspectRatio, Qt.SmoothTransformation).save(dest)

# -------------------------------------------------------------------------------------
def create_generation(projectname, shotname, project_dir, shot_dir, shot_root, gen, cur_settings, insertpos, clip=None):
    """docstring for create_generation"""
    
    if not gen.status(True):
        return (False, "Generation not running.")

    epp_root = osplus.get_env("EPP_ROOT")

    source_filename = cur_settings.get("standin", "source", "standin.png", create=True)


    source_filepath = os.path.join(epp_root, "templates", "images", source_filename)

    if not os.path.isfile(source_filepath):
        return (False, "Standin not found.")

    do_tag = cur_settings.get("standin", "tag", "True", create=True).lower() in ['true', 'yes', '1']

    # STANDIN
    dest = os.path.join(shot_dir, "standin.png")

    if do_tag:
        project_config = settings.XMLSettings(os.path.join(project_dir, "project_config.xml") )
        width = int(project_config.get("format", "width", "1920"))
        height = int(project_config.get("format", "height", "1080"))
        aspectx = float(project_config.get("format", "aspectx", "1.0"))
        aspecty = float(project_config.get("format", "aspecty", "1.0"))

        x = float(cur_settings.get("standin", "x", "0.08", create=True))
        y = 1.0-float(cur_settings.get("standin", "y", "0.51", create=True)) # Fusion Space
        font = cur_settings.get("standin", "font", "Lucida Sans Unicode", create=True)
        fontsize = float(cur_settings.get("standin", "fontsize", "0.15", create=True))
        fontbold = cur_settings.get("standin", "fontbold", "False", create=True).lower() in ['true', 'yes', '1']
        fontitalic = cur_settings.get("standin", "fontitalic", "False", create=True).lower() in ['true', 'yes', '1']
        r = int(cur_settings.get("standin", "fontred", "255", create=True))
        g = int(cur_settings.get("standin", "fontgreen", "255", create=True))
        b = int(cur_settings.get("standin", "fontblue", "255", create=True))

        ret = tag_image(source_filepath, dest, shotname, font, fontsize, x, y, width, height, aspectx, aspecty, r, g, b, fontbold, fontitalic)

    else:
        ret = False

    if not ret:
        # Fall back to default
        shutil.copy(source_filepath, dest)

    # Generation
    return gen.insert_shot(projectname, shotname, dest, shot_root, insertpos, clip)
    

# -------------------------------------------------------------------------------------
def add_shot(projectname, shotname, template, gen, insertpos, clip=None):
    """docstring for add_project"""

    epp_root = osplus.get_env("EPP_ROOT")

    if not os.path.isdir(epp_root):
        return (False, "Could not find EPP ROOT directory. Set the EPP_ROOT env variable first.", )

    cur_settings = settings.XMLSettings(os.path.join(epp_root, "config.xml") )
    project_root_dir = cur_settings.get("paths", "projectdir", None)

    if project_root_dir is None:
        return (False, "Don't know the project root dir. Please set it in your config.xml first.", )

    project_dir = os.path.join(project_root_dir, projectname)

    project_template = os.path.join(project_dir, "project_template.xml")
    project_vars = os.path.join(project_dir, "project_vars.xml")
    project_shots = os.path.join(project_dir, "project_shots.xml")

    if not os.path.isfile(project_template):
        return (False, "Project Template not found.")

    # Optional
    if not os.path.isfile(project_vars):
        project_vars = None
    
    dq = DirQuery(project_template, project_vars)

    try:
        shot_root = dq.get_path("shots", project_root_dir)
    except:
        return (False, "Shot directory not found")

    if not shot_root.lower().startswith(project_dir.lower()):
        return (False, "Shot and project directories do not match.")

    shot_dir = os.path.join(shot_root, shotname)

    if os.path.isdir(shot_dir):
        return (False, "Shot folder '{0}' already exists.".format(shotname),)

    template_filepath = os.path.join(epp_root, "templates", "shot_dirs", template)
    
    if not os.path.isfile(template_filepath):
        return (False, "Template '{0}' does not exists".format(template))

    ####
    #TODO: Better off in its own module

    import lxml.etree as etree
    from lxml.etree import ElementTree
    from lxml.etree import Element, SubElement, Comment, tostring, XMLParser
    root = Element('shots')
    if os.path.isfile(project_shots):
        with open(project_shots, 'rt') as f:
            parser = XMLParser(remove_blank_text=True)
            tree = etree.parse(f, parser)
            
            if tree.find(".//shot[@name='{0}']".format(shotname)) is not None:
                return (False, "Shot '{0}' already exists in shotlist.".format(shotname),)

            root = tree.getroot()

    shot_item = SubElement(root, 'shot', name=shotname)
    shot_item.text = '"{0}"'.format(shotname)

    with open(project_shots, 'w') as f:
        f.write(tostring(root, pretty_print=True, encoding="utf-8", xml_declaration=True))

    ####

    args = {}
    args["SHOTNAME"] = shotname

    sh = StructHandler(template_filepath, shot_root, False, True, args)

    # We save all input variables for later path reconstruction
    # We don't save all env vars though
    proj_settings = settings.XMLSettings(os.path.join(shot_dir, "shot_vars.xml") )
    for key, value in args.items():
        proj_settings.set("creationvars", key, str(value))
    for key, value in sh.used_environ.items():
        proj_settings.set("creationenvars", key, str(value))
    #print(template_filepath, project_dir, False, True, args)

    # Copy the template for reference
    shutil.copy(template_filepath, os.path.join(shot_dir, "shot_template.xml"))

    ret = create_generation(projectname, shotname, project_dir, shot_dir, shot_root, gen, cur_settings, insertpos, clip)

    if ret[0]:
        return (True, '{0} successfully created.'.format(shotname))
    else:
        return (False, '{0} created, but Generation link failed.\n{1}'.format(shotname, ret[1]))

#print add_project("hello", "project.xml", Format(123, 240, 24, 1.0, 1.0, "Hello"))
