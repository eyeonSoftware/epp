#!/usr/bin/env python
#coding=utf-8
#? py

'''
controller.py
####################################

Controller class for eyeon Fusion
Requires PeyeonScript / Running Fusion instance.

:copyright: 2013 by eyeon Software Inc., see AUTHORS for more details
:license: Some rights reserved, see LICENSE for more details
'''
import bisect
from collections import Counter #Py 2.7+
import glob
import os
import re
import unicodedata


import PeyeonScript as eyeon
from epp.helper.xml.dir_query import DirQuery
import epp.helper.osplus as osplus

# -------------------------------------------------------------------------------------
def fu_controller():
    """docstring for gen_controller"""
    
    return Controller()

# #############################################################################################
class Controller(object):
    """Controller for eyeon Generation"""
    # -------------------------------------------------------------------------------------
    # Attributes
    app = None     # Connection to Host app
    pat_version = re.compile(r"""[^a-zA-Z0-9][vV](\d+)""")
    pat_version_sub = re.compile(r"""([^a-zA-Z0-9])([vV])(\d+)""")
    SAVE_FORMATS = None

    # -------------------------------------------------------------------------------------
    # Private
    # -------------------------------------------------------------------------------------
    def __init__(self):
        super(Controller, self).__init__()

        self.connect()
        
    # -------------------------------------------------------------------------------------
    # Public
    # -------------------------------------------------------------------------------------
    def get_comp(self):
        """docstring for get_comp"""
        if not self.status(True):
            return (False, "No connection.")

        comp = self.app.CurrentComp

        # Check for validity
        if comp is None:
            return (False, "No composition.")
        
        return (True, comp)

    # -------------------------------------------------------------------------------------
    def get_meta(self, name=None, comp=None):
        """docstring for get_meta"""
        # Use what was given if possible
        if comp is None:
            comp = self.app.CurrentComp

        # Check for validity
        if comp is None:
            return (False, "No composition.")

        metadata = comp.GetData(name)

        return (True, metadata)

    # -------------------------------------------------------------------------------------
    def set_format(self, new_format, comp=None):
        """docstring for set_format"""
        
        if not self.status(True):
            return (False, "No connection.")

        # Use what was given if possible
        if comp is None:
            comp = self.app.CurrentComp

        comp.SetPrefs({
            "Comp.FrameFormat.Width": new_format.width,
            "Comp.FrameFormat.Height": new_format.height,
            "Comp.FrameFormat.AspectX": new_format.aspectx,
            "Comp.FrameFormat.AspectY": new_format.aspecty,
            "Comp.FrameFormat.Rate": new_format.framerate,
            "Comp.FrameFormat.Name": new_format.name,
            })
        
        return (True, "")            


    # -------------------------------------------------------------------------------------
    def set_meta(self, data, name=None, comp=None, add=False):
        """docstring for get_meta"""
        # Use what was given if possible
        if comp is None:
            comp = self.app.CurrentComp

        # Check for validity
        if comp is None:
            return (False, "No composition.")

        if add:
            ret, old_data = self.get_meta(name, comp)
            if ret and old_data is not None:
                data = dict(old_data.items() + data.items())

        if name is None:
            comp.SetData(data)
        else:
            comp.SetData(name, data)

        return (True, "")


    # -------------------------------------------------------------------------------------
    def get_save_formats(self):
        """docstring for get_formats"""

        if not self.status(True):
            return (False, "No connection.")

        # Cached?
        if self.SAVE_FORMATS is not None:
            return self.SAVE_FORMATS

        regs = self.app.GetRegList("CT_ImageFormat")
        #regs.Attrs = {}

        self.SAVE_FORMATS = {}

        for reg in regs.values():
            attrs = self.app.GetRegAttrs(reg.ID)
            
            if not attrs.get('REGB_MediaFormat_CanSaveImages', False):
                continue

            ext = attrs['REGST_MediaFormat_Extension'][1.0]
            name = attrs['REGS_MediaFormat_FormatName']

            self.SAVE_FORMATS[name] = ext
            
        return self.SAVE_FORMATS            

    # -------------------------------------------------------------------------------------
    def add_tool(self, regid, name=None, posx=-32768, posy=-32768, comp=None, lock=True):
        """docstring for add_tool"""

        if not self.status(True):
            return (False, "No connection.")

        # Use what was given if possible
        if comp is None:
            comp = self.app.CurrentComp

        if lock:
            comp.Lock()

        tool = comp.AddTool(regid, posx, posy)

        if lock:
            comp.Unlock()

        if name is not None:
            if regid in ("Loader", "Saver",):
                tool.SetAttrs({"TOOLB_NameSet": True})

            tool.SetAttrs({"TOOLS_Name": "epp" + name})
            


        return (True, tool)


    # -------------------------------------------------------------------------------------
    def create_saver(self, saverpath, name=None, comp=None):
        """docstring for create_saver"""

        if not self.status(True):
            return (False, "No connection.")

        # Use what was given if possible
        if comp is None:
            comp = self.app.CurrentComp

        # Check for validity
        if comp is None:
            return (False, "No composition.")

        saverpath = str(saverpath)

        if name is None:
            name = os.path.splitext(os.path.basename(saverpath))[0]

        ret = self.add_tool("Saver", name=name, comp=comp)

        if not ret[0]:
            return ret

        saver = ret[1]

        saverdir = os.path.dirname(saverpath)
        if not os.path.isdir(saverdir):
            os.makedirs(saverdir)

        #print saver.Clip[comp["TIME_UNDEFINED"]]
        saver.Clip[comp["TIME_UNDEFINED"]] = saverpath
        #saver.OutputFormat = "OpenEXRFormat"
        #saver.OpenEXRFormat.Depth = 1
        #saver.OpenEXRFormat.Compression = 3

        return (True, "")

    # -------------------------------------------------------------------------------------
    def set_pathmap(self, key, value):
        """docstring for set_pathmap"""
        #print key + value
        if not self.status(True):
            return (False, "No connection")

        res = self.app.SetPrefs("Global.Paths.Map."+str(key), str(value))
        msg = "Failed" if res == False else "Success"
        return (res, msg)

    # -------------------------------------------------------------------------------------
    def get_pathmap(self, key, default=None):
        """docstring for set_pathmap"""
        if not self.status(True):
            return False

        ret = self.app.GetPrefs("Global.Paths.Map."+key)
        if ret is None:
            return default
        return ret

    # -------------------------------------------------------------------------------------
    def save_comp(self, path, metadata=None):
        """docstring for save_comp"""
        
        if not self.status(True):
            return (False, "No connection.")

        comp = self.app.CurrentComp

        if comp is None:
            return (False, "No composition.")

        if metadata is not None:
            self.set_meta(metadata, "epp", add=True)
        
        # Don't like unicode
        path = osplus.unitostr(path)
        return (comp.Save(path), "Failed to save the comp.")

    # -------------------------------------------------------------------------------------
    def get_version(self, filename):
        """docstring for get_version"""
        
        return self.pat_version.findall(filename)

    # -------------------------------------------------------------------------------------
    def save_new_version(self):
        """docstring for update_savers"""

        if not self.status(True):
            return (False, "No connection.")

        comp = self.app.CurrentComp
        if comp is None:
            return (False, "No composition.")


        comp_filepath = comp.GetAttrs("COMPS_FileName")
        if comp_filepath == "":
            return (False, "Save compososition first as a version.")

        comp_dir = os.path.dirname(comp_filepath)
        comp_filename = os.path.basename(comp_filepath)

        comp_ver = self.get_version(comp_filename)

        if len(comp_ver) > 1:
            return (False, "Multiple versions found in: " + comp_filename)
        elif len(comp_ver) < 1:
            return (False, "No versions found in: " + comp_filename)
    
        new_version = int(comp_ver[0]) + 1


        while(True):
            # Comp
            new_comp_filename = self.pat_version_sub.sub("\g<1>\g<2>%03d" % new_version, comp_filename)
            new_comp_filepath = os.path.join(comp_dir, new_comp_filename)
            if os.path.isfile(new_comp_filepath):
                options = {1: {1:"Only Enabled", 2:"Text", "Name": "Error", "Default": "Composition with that version already exists:\n{0}\nTry next available version or cancel?".format(new_comp_filename), "ReadOnly": True }}
                ret = comp.AskUser("New Versions", options)

                if ret is None:
                    return (False, "Canceled by user.")

                new_version += 1
            else:
                break

        res, msg = self.update_savers(new_version)
        if not res:
            return (False, msg)


        comp.Save(new_comp_filepath)

        return (True, "Compostion saved to %s" % new_comp_filename)

    # -------------------------------------------------------------------------------------
    def update_savers(self, new_version):
        """docstring for update_saver"""

        if not self.status(True):
            return (False, "No connection.")

        comp = self.app.CurrentComp
        if comp is None:
            return (False, "No composition.")


        saver_options = {}
        i = 1

        all_savers = comp.GetToolList(False, "Saver").values()

        if len(all_savers) < 1:
            return (True, "No Savers found")

        all_savers_dict = dict(zip ([saver.Name for saver in all_savers], all_savers))

        savers_to_check = []

        for saver_name in sorted(all_savers_dict.keys()):

            saver = all_savers_dict[saver_name]

            cur_filepath = saver.Clip[comp.TIME_UNDEFINED]
            versions = self.pat_version.findall(cur_filepath)

            version_count = Counter(versions)

            if len(version_count) < 1:
                saver_options[i] = {1:saver_name, 2:"Text", "Name": "[  ] %s: %s" % (saver_name, os.path.basename(cur_filepath)), "Lines":1, "ReadOnly": True, "Default":"No Version Found. Skipped."}
                i += 1
                continue

            if len(version_count) == 1 and (int(version_count.keys()[0]) == new_version):
                saver_options[i] = {1:saver_name, 2:"Text", "Name": "[  ] %s: %s" % (saver_name, os.path.basename(cur_filepath)), "Lines":1, "ReadOnly": True, "Default":"V%03d -- Version UpToDate. Skipped." % new_version}
                i += 1
                continue




            cur_default = 1 if len(version_count) > 0 else 0

            old_version = ",".join(version_count.keys())
            
            # Version up for each saver ...
            #new_version = int(sorted(version_count.keys())[-1]) + 1

            savers_to_check.append(saver_name)
            saver_options[i] = {1:saver_name, 2:"Checkbox", "Name": "%s: %s" % (saver_name, os.path.basename(cur_filepath)), "Default":cur_default}
            i += 1
            saver_options[i] = {1:"txt_" + saver_name, 2:"Text", "Name": "", "Default": "V%s --> V%03d" % (old_version, new_version), "ReadOnly":True, "Lines": 1}
            i += 1

        i += 1
        saver_options[i] = {1:"Only Enabled", 2:"Checkbox", "Name": "Process only enabled Savers", "Default":0}
        ret = comp.AskUser("New Versions", saver_options)

        if ret is None:
            return (False, "Canceled by user.")

        only_enabled = ret["Only Enabled"]

        i = 0
        for saver_name in savers_to_check:

            saver = all_savers_dict[saver_name]
            disabled = saver.GetAttrs("TOOLB_PassThrough")

            if ret[saver_name] == 0:
                continue

            if only_enabled == 1 and disabled == True:
                continue

            cur_filepath = saver.Clip[comp.TIME_UNDEFINED]
            new_filepath = self.pat_version_sub.sub("\g<1>\g<2>%03d" % new_version, cur_filepath)

            new_dir = new_filepath
            if os.path.splitext(new_dir)[1] != "" and not os.path.isdir(new_dir):
                new_dir = os.path.dirname(new_dir)

            if not os.path.isdir(new_dir):
                os.makedirs(new_dir)

            saver.Clip = new_filepath
            i += 1

        return (True, "%d of %d Savers updated to V%03d" % (i, len(savers_to_check), new_version))

    # -------------------------------------------------------------------------------------
    def connect(self):
        """docstring for connect"""

        self.app = eyeon.scriptapp("Fusion")

        return self.status()
    
    # -------------------------------------------------------------------------------------
    def status(self, connect=False):
        """docstring for status"""
        status = self._status()

        if not status and connect:
            return self.connect()
        
        return status

    # -------------------------------------------------------------------------------------
    def _status(self):
        """Check if connection to application is valid"""
        if self.app is None:
            return False

        try:
            self.app.GetHelp()
        except TypeError:
            return False

        return True

# -------------------------------------------------------------------------------------
def main():
    """docstring for main"""
    c = Controller()    
    #shot = "freedom25"
    #print c.insert_shot("shotproject3", shot, r"C:\projects\shotproject3\shots\{0}\standin.png".format(shot), r"C:\projects\shotproject3\Shots")
    print c.create_saver(r"C:\temp\test_hello.jpg", name="HELLO")

    #shot = "400"

    #c.insert_shot("shotproject3", shot, r"C:\projects\shotproject3\shots\{0}\standin.png".format(shot), r"C:\projects\shotproject3\Shots")

if __name__ == '__main__':
    main()
