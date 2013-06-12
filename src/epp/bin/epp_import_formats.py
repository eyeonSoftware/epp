#!/usr/bin/env python
#coding=utf-8
#? py C:\ProgramData\eyeon\Fusion\Profiles\Default\VidModes.def C:\temp\formats.xml

'''
epp_import_formats.py
####################################

Import Fusion VideoModes to epp XML file.

:copyright: 2013 by eyeon Software Inc., see AUTHORS for more details
:license: Some rights reserved, see LICENSE for more details
'''

import argparse
import os
import sys

import epp.helper.xml.settings as settings
from epp.helper.slpp import slpp as lua

# -------------------------------------------------------------------------------------
def import_formats(filepath, destpath):
    """docstring for import_formats"""
    if not os.path.isfile(filepath):
        print("File not found.")
        sys.exit(1)

    with open(filepath, "r") as f:
        formats = f.read().decode("utf-8")
    
    formats_dict = lua.decode(formats)

    destdir = os.path.dirname(destpath)

    if not os.path.isdir(destdir):
        os.makedirs(destdir)

    formats_setting = settings.XMLSettings(destpath, root="formats")

    topic = "format"
    for name, keys in formats_dict.items():
        for key, value in keys.items():

            # Ignore lists like Guides
            if not isinstance(value, (tuple, list, dict, set)):
                # Only if not exists
                if formats_setting.get(topic, key, topic_attr={"name": name}) is None:
                    formats_setting.set(topic, key, str(value), {"name": name})
                else:
                    pass

# -------------------------------------------------------------------------------------
def main():
    """docstring for main"""
    pass                
    parser = argparse.ArgumentParser(description='epp Import Formats')
    parser.add_argument('VIDMODES',
            help='Path to VidModes.def source file.') 
    parser.add_argument('DESTXML',
            help='Path to formats destination xml file.') 

    args = parser.parse_args()

    import_formats(args.VIDMODES, args.DESTXML)

if __name__ == '__main__':
    main()    
