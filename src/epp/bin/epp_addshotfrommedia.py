#!/usr/bin/env python
#coding=utf-8
#? py

'''
epp_generatemeta.py
####################################

Generate Metadata from filename

:copyright: 2013 by eyeon Software Inc., see AUTHORS for more details
:license: Some rights reserved, see LICENSE for more details
'''

import os
import re
import shutil

from epp.helper.xml.dir import StructHandler
import epp.helper.osplus as osplus
import epp.helper.xml.settings as settings
import epp.helper.log as log
from epp.model.format import Format
from epp.helper.xml.dir_query import DirQuery
import epp.bin.epp_addshot as epp_addshot

# -------------------------------------------------------------------------------------
def add_shot_from_media(projectname, shotname, template, gen, insertpos, clip):
    """docstring for add_shot_from_media"""
    return epp_addshot.add_shot(projectname, shotname, template, gen, insertpos, clip)

# -------------------------------------------------------------------------------------
def generate_meta(gen, pattern):
    """Generate metadata from name and insert into the clip"""

    if not gen.status(True):
        return (False, "Generation not running.")


    if not os.path.isdir(epp_root):
        return (False, "Could not find EPP ROOT directory. Set the EPP_ROOT env variable first.", )

    PAT_FILEBASENAME = re.compile(pattern)
    selected_versions = gen.selected_versions()

    if len(selected_versions) < 1:
        return (False, "No versions selected.")

    for version in selected_versions:
        meta = version.Metadata(gen.frame())
        path = meta['Data']['File']['Path']

        mat = PAT_FILEBASENAME.findall(path)
        if len(mat):
            shotname = mat[0]
            gen.add_meta(version, shotname)
            log.info("Setting metadata of {0} to {1}".format(version.Name, shotname))
        else:
            log.warning("Skipping " + os.path.basename(path))

    return (True, "")
        
if __name__ == '__main__':
    from epp.gen.controller import gen_controller

    epp_root = osplus.get_env("EPP_ROOT")
    cur_settings = settings.XMLSettings(os.path.join(epp_root, "config.xml") )
    patterns = cur_settings.findall("shotpattern", "pattern")
    gen = gen_controller()

    ret, msg = generate_meta(gen, patterns.values()[1])
    if not ret:
        log.error(msg)

