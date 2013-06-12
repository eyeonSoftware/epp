#!/usr/bin/env python
#coding=utf-8
#? py

'''
update_shot.py
####################################

set_shot PySide interface controller. Makes use of the Designer generated _ui file.

:copyright: 2013 by eyeon Software Inc., eyeon Software Inc., see AUTHORS for more details
:license: Some rights reserved, see LICENSE for more details
'''

import os
import re
import sys
import lxml.etree as etree

from PySide.QtCore import *
from PySide.QtGui import *

import epp.helper.log as log
import epp.helper.osplus as osplus
import epp.helper.xml.settings as settings
import epp.helper.filesystem as filesystem
from epp.ui.update_shot_ui import Ui_dlgUpdateShot
from epp.__INFO__ import DEBUG, __VERSION__
from epp.helper.shortcuts import shot_root_path
from epp.gen.controller import gen_controller
from epp.helper.xml.dir_query import DirQuery

class UpdateShotDialog(Ui_dlgUpdateShot, QDialog):
    """
    This class represents 
    """

    # -------------------------------------------------------------------------------------
    def PROJECTNAME():
        doc = "The PROJECTNAME property."
        def fget(self):
            return self._PROJECTNAME
        def fset(self, value):
            if isinstance(value, basestring):
                self.lblProject.setText(value)
            self._PROJECTNAME = value
        return locals()
    PROJECTNAME = property(**PROJECTNAME())

    def __init__(self, parent=None):
        """
        Constructor.
        """
        super(UpdateShotDialog, self).__init__()
        self.setupUi(self)

        self.STATUS = self._setup()


        try:
            if DEBUG:
                self._setup_debug()
        except NameError:
            pass
        
    # -------------------------------------------------------------------------------------
    def _setup_debug(self):
        """
        
        """
        pass
        
    # -------------------------------------------------------------------------------------
    def _setup(self):
        """
        Setup the widgets
        """

        epp_root = osplus.get_env("EPP_ROOT")

        if not os.path.isdir(epp_root):
            QMessageBox.critical(self, "Error", "Could not find EPP ROOT directory.\n{0}".format(epp_root))
            return False

        self.settings = settings.XMLSettings(os.path.join(epp_root, "config.xml") )
        self.PROJECTROOT = self.settings.get("paths", "projectdir")

        if self.PROJECTROOT is None:
            QMessageBox.critical(self, "Error", "No Project Directory configured in config.xml.")
            return False

        self._setup_header(epp_root)
        self._setup_status()


        # Require Generation
        if not self._setup_generation():
            msg = "Could not establish connection with Generation. Make sure it is running."
            log.error(msg, True)
            return False

        # Need edit rights for this one!
        if not self._gen.allow_changes(True):
            log.warning("Project locked.")
            return False

        if not self._setup_project():
            msg = "Project directory from Generation Project invalid: {0}".format(self.PROJECTDIR)
            log.error(msg, True)
            return False


        if not self._setup_shot():
            msg = "Project directory from Generation Project invald: {0}".format(self.PROJECTDIR)
            log.error(msg, True)
            return False

        return True

    # -------------------------------------------------------------------------------------
    def _setup_generation(self):
        """docstring for _setup_generation"""
        self._gen = gen_controller()

        return self._gen.status()

    # -------------------------------------------------------------------------------------
    def _setup_project(self):
        """docstring for set_project"""

        proj = self._gen.app.ActiveProject

        self.PROJECTNAME = proj.Name
        self.PROJECTDIR = ""
        self.GENFILEPATH = proj.Filename

        # BUG? X:dir\dir instead of X:\dir\dir
        pa_frontslash = re.compile(r"(\w:)([^\\].*)$")
        self.GENFILEPATH = pa_frontslash.subn(r'\1\\\2', self.GENFILEPATH)[0]

        if self.GENFILEPATH is None:
            return False

        # Find the projectname in the filename
        index = self.GENFILEPATH.lower().find(self.PROJECTNAME.lower().split("_")[0])
        if index < 0:
            return False

        index += len(self.PROJECTNAME)

        self.PROJECTDIR = self.GENFILEPATH[:index].rstrip(os.path.sep)

        if not self.PROJECTDIR.lower().startswith(self.PROJECTROOT.lower()):
            return False

        # proj:SaveAs does not set the proj.Filename
        if not os.path.isdir(self.PROJECTDIR): #or not self.GENFILEPATH.lower().startswith(self.PROJECTDIR.lower()):
            return False


        return True

    # -------------------------------------------------------------------------------------
    def _setup_shot(self):
        """Setup the shot directory."""

        project_template = os.path.join(self.PROJECTDIR, "project_template.xml")
        project_vars = os.path.join(self.PROJECTDIR, "project_vars.xml")

        if not os.path.isfile(project_template):
            return False

        # Optional
        if not os.path.isfile(project_vars):
            project_vars = None
        else:
            # The project name right now does not include \\ so query it!
            projectvars = settings.XMLSettings(project_vars)
            self.PROJECTNAME = projectvars.get("creationvars", "projectname")
        
        dq = DirQuery(project_template, project_vars)

        try:
            self.SHOTDIR = dq.get_path("shots", self.PROJECTROOT)
        except:
            self.SHOTDIR = None
            return False

        if not self.SHOTDIR.lower().startswith(self.PROJECTDIR.lower()):
            return False

        self.update_shots()

        return True


    # -------------------------------------------------------------------------------------
    def update_shots(self):
        """docstring for update_project"""
        self.cmbShot.clear()

        self.cmbShot.addItem("[ALL SHOTS]", "*")

        sort = False
        if self.settings.get("preferences", "shotlistsort", "True", create=True).strip().lower() in ['true', '1', 'yes', 'on']:
            sort = True
        
        cur_project = self.PROJECTNAME
        project_shots = os.path.join(self.PROJECTROOT, cur_project, "project_shots.xml")
        
        shot_root_dir = shot_root_path(cur_project)

        if shot_root_dir == "":
            self.valid_shotname = False
            return

        shot_dict = {}
        if os.path.isfile(project_shots):
            with open(project_shots, 'rt') as f:
                tree = etree.parse(f)
                
                for item in tree.findall(".//shot"):

                    shot_dir = os.path.join(shot_root_dir, item.text.strip('"'))
                    if os.path.isdir(shot_dir):
                        shot_dict[item.attrib["name"]] = shot_dir
    
        if sort:
            for key in sorted(shot_dict.keys()):
                self.cmbShot.addItem(key, shot_dict[key])
        else:                
            for key in shot_dict.keys():
                self.cmbShot.addItem(key, shot_dict[key])

        if self.cmbShot.count() < 1:
            self.valid_shotname = False
        else:
            self.valid_shotname = True

    # -------------------------------------------------------------------------------------
    def _setup_header(self, epp_root):
        """docstring for _setup_header"""
        header_filepath = os.path.join(epp_root, "templates", "images", "header.png")

        if os.path.isfile(header_filepath):
            """
            pix = QPixmap()
            pix.load(header_filepath)
            self.lblHeader.setPixmap(pix)
            """
            self.lblHeader.setStyleSheet("QLabel {{ background-image: url({0});}}".format(header_filepath.replace("\\", "/")))
            self.lblHeader.setMinimumHeight(96)
            self.setMaximumWidth(540)

    # -------------------------------------------------------------------------------------
    def _setup_status(self):
        """docstring for """
        self.lblStatus.setText("")
        fx = QGraphicsOpacityEffect(self.lblStatus)
        self.lblStatus.setGraphicsEffect(fx)
        self._status_fade  = QPropertyAnimation(fx, "opacity");
        self._status_fade.setDuration(250)
        self._status_fade.setStartValue(0.0)
        self._status_fade.setEndValue(1.0)
        self._last_valid_name = True
        self.valid_projectname = False
        self.valid_shotname = False

    # -------------------------------------------------------------------------------------
    def _validate_name(self, text):
        """docstring for _validate_name"""
        valid_name = len(text) > 0

        text = self.plugName.text()

        if not valid_name:
            self.lblStatus.setText("<font color='#ffaa00'>Invalid Shot Name</font>")
            self._status_fade.setDirection(QAbstractAnimation.Forward)
        else:
            self._status_fade.setDirection(QAbstractAnimation.Backward)

            shot_dir = os.path.join(self.SHOTDIR, text)
            if os.path.isdir(shot_dir):
                self.lblStatus.setText("<html><head><style type=text/css>a {{ color: white; }}\n a:link {{color:white; text-decoration:none; }}\n a:hover {{ color:#ffcc00; text-decoration:underline; }}</style></head><body><font color='#ffaa00'>Shot Directory already exists:</font> <a href='file:///{0}'>{0}</a></body></html>".format(shot_dir, shot_dir.replace("\\", "/")))
                valid_name = False
                self._status_fade.setDirection(QAbstractAnimation.Forward)
            else:
                self._status_fade.setDirection(QAbstractAnimation.Backward)

        if self._last_valid_name != valid_name:
            self._status_fade.start()
        
        self._last_valid_name = valid_name

        self.butAdd.setEnabled(valid_name) 
            

        
    # -------------------------------------------------------------------------------------
    def accept(self):
        """
        Check the connection.
        """
        projectname = self.PROJECTNAME
        shotname = self.cmbShot.currentText()
        shot_data = self.cmbShot.itemData(self.cmbShot.currentIndex())

        if not self._gen.status():
            log.error("Generation not running", True)
            return

        log.info("Importing Comps from {0} - {1}".format(projectname, shotname))

        if shot_data == "*":
            shots = filesystem.shots(self.PROJECTROOT, projectname)
        else:
            shots = {shotname:""}
        
        for cur_shotname, cur_shotdir in shots.items():
            comps = filesystem.comps(projectname, cur_shotname)
            for comp in comps:
                log.debug("Inserting {0}".format(comp))
                comp = str(comp)
                self._gen.insert_media(cur_shotname, comp, self.chkShotLike.isChecked())

        super(UpdateShotDialog, self).accept()

# -------------------------------------------------------------------------------------
def main():
    """docstring for main"""
    app = QApplication([])
    app.setStyle(QStyleFactory.create("plastique") )
    palette = QPalette(QColor(62, 62, 62), QColor(62, 62, 62))
    palette.setColor(palette.Highlight, QColor(255*0.6, 198*0.6, 0))
    app.setPalette(palette)

    apd = UpdateShotDialog()
    if apd.STATUS:
        if DEBUG:
            apd.setWindowTitle(apd.windowTitle() + " v" + __VERSION__)
        apd.show()
        sys.exit(app.exec_())
        
            



if __name__ == '__main__':
    main()
