#!/usr/bin/env python
#coding=utf-8
#? py meta_from_standins

'''
epp.py
####################################

global epp launcher

:copyright: 2013 by Me, see AUTHORS for more details
:license: Some rights reserved, see LICENSE for more details
'''
import argparse

from epp.ui import add_project 
from epp.ui import add_shot 
from epp.ui import create_saver 
from epp.ui import save_as 
from epp.ui import set_shot 
from epp.ui import update_shot 
from epp.ui import add_shot_from_media 
from epp.fu.controller import fu_controller
from epp.gen.controller import gen_controller
import epp.helper.log as log


# -------------------------------------------------------------------------------------
def main():
    """docstring for main"""

    fu_con = fu_controller()   
    gen_con = gen_controller()
    
    apps = {}
    apps["add_project"] = add_project.main
    apps["add_shot"] = add_shot.main
    apps["add_shot_from_media"] = add_shot_from_media.main
    apps["create_saver"] = create_saver.main
    apps["save_as"] = save_as.main
    apps["set_shot"] = set_shot.main
    apps["update_shot"] = update_shot.main
    apps["save_new_version"] = fu_con.save_new_version
    apps["meta_from_standins"] = gen_con.meta_from_standins

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('module', metavar='module', type=str, nargs='+',
                       help='Which module to launch.')

    args = parser.parse_args()
    
    for module in args.module:
        if not module in apps:
            log.error("Module not found: " + module)
        else:
            log.info("Launching " + module)
            apps[module]()
    
if __name__ == '__main__':
    try:
        main()
    except Exception, e:
        log.exception(e)
    finally:
        log.debug("Exit")
