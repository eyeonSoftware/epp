#!/usr/bin/env python
#coding=utf-8
#? py C:\epp

'''
epp-manage.py
####################################

Commandline Manager for epp

:copyright: 2013 by eyeon Software Inc., see AUTHORS for more details
:license: Some rights reserved, see LICENSE for more details
'''

import argparse
import ctypes
from distutils.dir_util import copy_tree
import os
import sys

import epp.__INFO__ as INFO
from epp.helper.xml.dir import StructHandler
import epp.helper.osplus as osplus
import epp.helper.xml.settings as settings
from epp.helper.slpp import slpp as lua

# #############################################################################################
class Wizard(object):
    """Console Style Wizard"""
    # -------------------------------------------------------------------------------------
    # Attributes

    # -------------------------------------------------------------------------------------
    # Private
    # -------------------------------------------------------------------------------------
    def __init__(self):
        super(Wizard, self).__init__()
        
        self.cur_step = 0
        

    # -------------------------------------------------------------------------------------
    # Public
    # -------------------------------------------------------------------------------------
    def step(self, text, input_text, default="", has_to_exist=False, has_to_be_file=False, 
            has_to_be_dir=False, makedirs=False, confirm_makedirs=False, warn_if_is_dir=False, exit_on=None):
        """docstring for wizard_step"""

        self.cur_step += 1
        print ("\n-- Step {0} --".format(self.cur_step))

        if text:
            print(text)

        while(True):
            errors = 0
            ret = raw_input(input_text) or default

            if exit_on is not None and ret == exit_on:
                return None

            if has_to_exist:
                if not os.path.exists(ret):
                    errors += 1
                    print("Error: Path does not exist.")

            if has_to_be_file:
                if not os.path.isfile(ret):
                    errors += 1
                    print("Error: Path is not an existing file.")

            if has_to_be_dir:
                if not os.path.isdir(ret):
                    errors += 1
                    print("Error: Path is not an existing directory.")

            if warn_if_is_dir:
                if os.path.isdir(ret):
                    print("Warning: Directory already exists.")

            if makedirs:
                if not os.path.isdir(ret):
                    do_makedirs = True
                    if confirm_makedirs:
                        ret2 = raw_input("Directory does not exist. Create it [yes]/no? ") or "yes"
                        if ret2.lower() not in ('yes', 'y', 'true'):
                            do_makedirs = False

                    if do_makedirs:
                        os.makedirs(ret)
            
            if errors == 0:
                break

        return ret

    # -------------------------------------------------------------------------------------
    def complete(self):
        """docstring for complete"""
        print ("\n-- Complete --\n")

# -------------------------------------------------------------------------------------
def wizard(client_only):
    """docstring for wizard"""

    print ("""\nepp Install Wizard v{0}""".format(INFO.__VERSION__))
    print ("""#############################""")

    wizard = Wizard()

    ret = {}

    if not client_only:
        ret['project_dir'] = wizard.step(r"""Set the Path to the Project Root Directory where all your Projects and Shots
    will be stored in future. This is the working directory for all your assets, files etc.

    Project Root Directory [C:\projects]:""", "", r"C:\projects", makedirs=True, confirm_makedirs=True, warn_if_is_dir=True)

    ret['fu_script_dir'] = wizard.step(r"""Set the Path to the Fusion Script Directory. All the necessary Fusion scripts
will be installed here.

Fusion Script Directory [C:\Users\Public\Documents\eyeon\Fusion\Scripts\Comp]:""", r"", r"C:\Users\Public\Documents\eyeon\Fusion\Scripts\Comp",
    makedirs=True, confirm_makedirs=True)

    if not client_only:
        ret['gen_script_dir'] = wizard.step(r"""Set the Path to the Generation Script Directory. All the necessary Generation scripts
    will be installed here.

    Generation Script Directory [C:\Program Files\eyeon\Generation [AM]\scripts\generation\toolbar]:""", r"", r"C:\Program Files\eyeon\Generation [AM]\scripts\generation\toolbar",
        makedirs=True, confirm_makedirs=True)   

    if not client_only:
        ret['formats_import_filepath'] = wizard.step(r"""Import Formats from Fusion?
        
    Path to Fusion Formats [C:\ProgramData\eyeon\Fusion\Profiles\Default\VideoModes.def]/no:""", r"", r"C:\ProgramData\eyeon\Fusion\Profiles\Default\VidModes.def",
        has_to_be_file=True, exit_on="no")
    
    wizard.complete()

    return ret 

# -------------------------------------------------------------------------------------
def confirm_install(args):

    print ("\nConfirm Installation:\n")

    for key, value in args.items():
        print ("{0} - {1}".format(key, value))

    ret = raw_input("Install epp with these settings [yes]/no? ") or "yes"
    if ret.lower() in ('yes', 'y', 'true'):
        return True

    return False

# -------------------------------------------------------------------------------------
def install_epp(args):
    """docstring for install_epp"""

    struct_file = osplus.app_path("_templates", "install.xml")

    print struct_file

    if not os.path.isfile(struct_file):
        return False
    
    install_path = args['install_path']

    overwrite = False
    if not os.path.isdir(install_path):
        os.makedirs(install_path)
    else:
        overwrite = raw_input("Install Directory already exists. Do you want to keep old files [yes]/no? ") or "yes" not in ("yes", "y", "true")

    print "Creating directory strucutre ..."
    sh = StructHandler(struct_file, install_path, overwrite, True, args)

    print "Creating config file ..."
    sett = settings.XMLSettings( os.path.join(install_path, "config.xml") )

    return overwrite 

# -------------------------------------------------------------------------------------
def import_formats(filepath, destpath):
    """docstring for import_formats"""
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
def install(args):
    """docstring for install"""

    if not confirm_install(args):
        return False
    
    if "project_dir" in args and args["project_dir"] is not None:
        overwrite = install_epp(args)
        if not os.path.isdir(args["project_dir"]):
            os.path.makedirs(args["project_dir"])

    print "Setting environment variable ..."
    osplus.set_env("EPP_ROOT", args["install_path"])
    #osplus.set_env("EPP_PROJECT_ROOT", args["project_dir"])

    # TODO Install fu, gen scripts
    if "formats_import_filepath" in args and args["formats_import_filepath"] is not None:
        print "Importing format ..."
        format_filepath = os.path.join(args["install_path"], "templates", "formats.xml")
        if os.path.isfile(format_filepath) and overwrite:
            print ("Deleting old Formats ...")
            os.remove(format_filepath)
        if not os.path.isfile(format_filepath): 
            print ("Import Formats from Fusion ...")
        else:            
            print ("Appending Formats from Fusion ...")
        import_formats(args["formats_import_filepath"], format_filepath)
        print "Done."        
    
    print "Installing scripts ..."
    if "gen_script_dir" in args and args["gen_script_dir"] is not None and os.path.isdir(args["gen_script_dir"]):
        gen_src_dir = osplus.app_path("_scripts", "gen")
        copy_tree(gen_src_dir, args["gen_script_dir"])
        print "Copying Generation scripts ..."
    else:
        print "Could not copy Generation scripts."

    if args["fu_script_dir"] is not None and os.path.isdir(args["fu_script_dir"]):
        gen_src_dir = osplus.app_path("_scripts", "fu")
        copy_tree(gen_src_dir, args["fu_script_dir"])
        print "Copying Fusion scripts ..."
    else:
        print "Could not copy Fusion scripts."
    print "Done."        

    # Copy exe to bin.
    if hasattr(sys, 'frozen'):
        eppbindir = os.path.join(args["install_path"], "bin")
        if not os.path.isdir(eppbindir):
            os.makedirs(eppbindir)

        copy_tree(osplus.app_path(), eppbindir)

    return True        

# -------------------------------------------------------------------------------------
def main():
    """Main entry point"""
    try:
     is_admin = os.getuid() == 0
    except:
     is_admin = ctypes.windll.shell32.IsUserAnAdmin()

    if not is_admin:
        print "You need to be administrator to install epp."
        return
    

    parser = argparse.ArgumentParser(description='epp Console Manager')
    parser.add_argument('--no-wizard', dest='wizard', action='store_false', 
                       help='Install silently without options.')
    parser.add_argument('--client', dest='client', action='store_true', 
                       help='Install client')
    parser.add_argument('INSTALL_PATH',
            help='Path to install location of epp for data, settings and templates.')

    args = parser.parse_args()

    install_args = {}
    install_args['install_path'] = args.INSTALL_PATH
    if args.wizard:
        install_args = dict(install_args.items() + wizard(args.client).items())

    install(install_args)

if __name__ == '__main__':
    main()


