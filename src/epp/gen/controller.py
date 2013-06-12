#!/usr/bin/env python
#coding=utf-8
#? py

'''
controller.py
####################################

Controller class for eyeon Generation
Requires PeyeonScript / Running Generation instance.

:copyright: 2013 by eyeon Software Inc., see AUTHORS for more details
:license: Some rights reserved, see LICENSE for more details
'''
import bisect
import glob
import os
import re
import unicodedata


import epp.helper.log as log
import PeyeonScript as eyeon
from epp.helper.xml.dir_query import DirQuery
import epp.helper.osplus as osplus
import epp.helper.filesystem as filesystem

# -------------------------------------------------------------------------------------
def gen_controller():
    """Controller Factory"""
    
    return Controller()

# #############################################################################################
class Controller(object):
    """Controller for eyeon Generation"""
    # -------------------------------------------------------------------------------------
    # Attributes
    app = None     # Connection to Host app
    PAT_VER = re.compile(r"(.+)_[vV](\d+)(.+)")

    # -------------------------------------------------------------------------------------
    # Private
    # -------------------------------------------------------------------------------------
    def __init__(self):
        super(Controller, self).__init__()

        self.connect()
        
    # -------------------------------------------------------------------------------------
    # Public
    # -------------------------------------------------------------------------------------
    def insert_shot(self, projectname, shotname, image, shot_root, insertpos, clipm=None):
        """Insert a shot into project"""

        projectname = str(projectname)
        shotname = str(shotname)
        image = str(image)
        shot_root = str(shot_root)

        if not self.status(True):
            return (False, "Could not establish connection with Generation. Make sure it is running.")

        if not os.path.isfile(image):
            return (False, "Standin does not exists at '{0}'".format(image))

        lock = self.app.UpdateLock()
        proj = self.app.ProjectGet()

        sub = proj.SubGet(projectname.replace(os.path.sep, "_"))
        if sub is None:
            return (False, "No sub with project name '{0}' found.".format(projectname))

        track = sub.TrackGet()
        
        if track.ClipCount() < 1:
            index = 0
        elif insertpos == 2:
            shots_by_index = []
            for i in range(int(track.ClipCount())):
                cur_clip =  track.ClipGet(i)

                # First ClipV that has the metadata will be used
                for j in range(int(cur_clip.VersionCount())):
                    cur_ver = cur_clip.VersionGet(j)
                    cur_meta = cur_ver.Metadata(cur_ver.InPoint)
                    if "ShotName" in cur_meta["Data"]["UserClip"]:
                        shots_by_index.append(cur_meta["Data"]["UserClip"]["ShotName"])
                        break


            if shotname in shots_by_index:
                return (False, "Shot '{0}' already exists in Project.".format(shotname))

            if len(shots_by_index) < 1:
                index = 0
            else:
                index = bisect.bisect_left(shots_by_index, shotname)

        elif insertpos == 0:
            index = 0
        else:
            index = int(track.ClipCount())

        ld = proj.DropFiles(image) # Unicode will be None
        
        if ld is None or len(ld) < 1:
            return (False, "Standin '{0}' could not be added to Generation.".format(image))

        ld = ld[1.0]

        if insertpos == 4:
            new_version = clipm.VersionInsert(ld, 0)
        elif insertpos == 3:
            new_version = clipm.VersionInsert(ld, clipm.VersionCount())
        else:
            new_clip = track.ClipInsert(ld, index)            
            new_version = new_clip.VersionGet()
        
        self.add_meta(new_version, shotname)

        #meta = new_version.Metadata(new_version.InPoint)
        #meta['Data']['UserClip']['ShotName'] = shotname
        #new_version.Metadata(new_version.InPoint, meta)

        self.app.UpdateUnlock(lock)

        return (True, "Shot added to Generation")

    # -------------------------------------------------------------------------------------
    def add_meta(self, version, shotname):
        """docstring for add_meta"""
        cur_meta = version.Metadata(version.InPoint)
        meta = version.Metadata(version.InPoint)
        meta['Data']['UserClip']['ShotName'] = shotname
        version.Metadata(version.InPoint, meta)

    # -------------------------------------------------------------------------------------
    def create_project(self, projectname, project_dir, project_root):
        """docstring for create_project"""

        projectname_clean = projectname.replace(os.path.sep, "_")

        project_template = os.path.join(project_dir, "project_template.xml")
        project_vars = os.path.join(project_dir, "project_vars.xml")

        if not os.path.isfile(project_template):
            return (False, "Project tempalte not found.")

        # Optional
        if not os.path.isfile(project_vars):
            project_vars = None

        dq = DirQuery(project_template, project_vars)
        gen_dir = dq.get_path("generation", project_root)

        if gen_dir == "":
            return (False, "'generation' tag not found in project_template.xml")

        gen_filepath = osplus.unitostr(os.path.join(gen_dir, projectname_clean + ".genprj"))

        #lock = self.app.UpdateLock()

        # Requires build 2013.0213 
        # Create Project with Sub and Track
        proj = self.app.ProjectCreate(projectname, True)

        self.app.ProjectActivate(proj)
        sub = proj.SubGet()

        # By convention epp expects the mainsub to be named like the project
        sub.Name = projectname
        self.app.LoadSub(sub)

        # Requires Gen Build 2013.0702 or later
        proj.SaveAs(gen_filepath)

        #self.app.UpdateUnlock(lock)

        return (True, "")

    # -------------------------------------------------------------------------------------
    def get_shot_clip(self, shotname):
        """docstring for get_shot_clip"""

        shotname = str(shotname)

        #lock = self.app.UpdateLock()
        proj = self.app.ProjectGet()
        sub = proj.SubGet()
        track = sub.TrackGet()
        
        ret = None
        for i in range(int(track.ClipCount())):
            cur_clip =  track.ClipGet(i)

            # First ClipV that has the metadata will be used
            for j in range(int(cur_clip.VersionCount())):
                cur_ver = cur_clip.VersionGet(j)
                cur_meta = cur_ver.Metadata(cur_ver.InPoint)
                if cur_meta is not None and "ShotName" in cur_meta["Data"]["UserClip"] and cur_meta["Data"]["UserClip"]["ShotName"] == shotname:
                    ret = cur_clip
                    break

            if ret is not None:
                break

        #self.app.UpdateUnlock(lock)
        return ret

    # -------------------------------------------------------------------------------------
    def meta_from_standins(self):
        """Recreate Metadata from Standins"""

        lock = self.app.UpdateLock()
        proj = self.app.ProjectGet()
        sub = proj.SubGet()
        track = sub.TrackGet()
        

        projectname = None
        shotname = None
        for i in range(int(track.ClipCount())):
            cur_clip =  track.ClipGet(i)

            # First ClipV that has the metadata will be used
            for j in range(int(cur_clip.VersionCount())):
                cur_ver = cur_clip.VersionGet(j)
                loader = cur_ver.GetLoader()
                if loader is None:
                    continue

                filepath = loader.Filename

                if os.path.basename(filepath).lower() == "standin.png":
                    projectname, shotname = filesystem.project_shot_from_path(filepath)
                    if shotname is not None:
                        cur_meta = cur_ver.Metadata(cur_ver.InPoint)
                        cur_meta['Data']['UserClip']['ShotName'] = shotname
                        cur_ver.Metadata(cur_ver.InPoint, cur_meta)
                        log.debug("Setting Metadata for {0}".format(shotname))

        self.app.UpdateUnlock(lock)

    # -------------------------------------------------------------------------------------
    def insert_media(self, shotname, filepath, only_matching=False):
        """docstring for insert_comp"""
        clipm = self.get_shot_clip(shotname)
        proj = self.app.ProjectGet()
        sub = proj.SubGet()
        track = sub.TrackGet()

        is_comp = os.path.splitext(filepath)[1].lower() == ".comp"

        if clipm is None:
            log.warning("Shot {0} not found in Generation project.".format(shotname))
            return False

        mat = self.PAT_VER.match(os.path.basename(filepath))
        if mat is not None:
            target_base, target_ver, target_post = mat.groups()

        index = 0

        for j in range(int(clipm.VersionCount())):
            cur_ver = clipm.VersionGet(j)
            loader = cur_ver.GetLoader()
            cur_filepath = loader.Filename
            if loader is None:
                continue

            if is_comp:
                cur_filepath = loader.RefFilename()

            if cur_filepath is None:
                continue

            if cur_filepath.lower() == filepath.lower():
                log.debug("Media {0} already exists".format(os.path.basename(filepath)))
                return False


            mat = self.PAT_VER.match(os.path.basename(cur_filepath))
            if mat is not None and target_ver is not None:
                base, ver, post = mat.groups()
                if int(ver) == int(target_ver)-1:
                    index = cur_ver.Version

        if only_matching:
            if not os.path.basename(filepath).lower().startswith(shotname.lower().replace(os.path.sep, "_")):
                log.debug("Skipping because not a shot media {0}".format(os.path.basename(filepath)))
                return False

        #lock = self.app.UpdateLock()

        for i, loader in proj.DropFiles(str(filepath)).items():
            log.debug("Inserting {0} at {1}".format(os.path.basename(filepath), index))
            # Latest one.
            last_ver = clipm.VersionGet(0)
            in_point = 0
            if last_ver is not None:
                in_point = last_ver.InPoint

            new_ver = clipm.VersionInsert(loader)
            #TODO: new_ver = clipm.VersionInsert(loader, index)
            new_ver.InPoint = in_point

        #self.app.UpdateUnlock(lock)
    
        return True

    # -------------------------------------------------------------------------------------
    def selected_versions(self, default=None):
        """docstring for selected_versions"""
        project = self.app.ProjectGet()
        if project is None:
            return default

        return project.SelectedVersions().values()

    # -------------------------------------------------------------------------------------
    def frame(self):
        """docstring for frame"""
        return self.app.PlayControl("set")

    # -------------------------------------------------------------------------------------
    def allow_changes(self, flash=False):
        """docstring for allow_changes"""
        proj = self.app.ProjectGet()
        if proj is None:
            return False

        return proj.AllowChanges(flash)

    # -------------------------------------------------------------------------------------
    def connect(self):
        """docstring for connect"""

        self.app = eyeon.scriptapp("Generation")

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

    #shot = "400"
    c.meta_from_standins()

    #c.insert_shot("shotproject3", shot, r"C:\projects\shotproject3\shots\{0}\standin.png".format(shot), r"C:\projects\shotproject3\Shots")

if __name__ == '__main__':
    main()
