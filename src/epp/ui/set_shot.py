#!/usr/bin/env python
#coding=utf-8
#? py

'''
set_shot.py
####################################

set_shot PySide interface controller. Makes use of the Designer generated _ui file.

:copyright: 2013 by eyeon Software Inc., eyeon Software Inc., see AUTHORS for more details
:license: Some rights reserved, see LICENSE for more details
'''

import glob
import os
import sys
import lxml.etree as etree

from PySide.QtCore import *
from PySide.QtGui import *

import epp.helper.log as log
import epp.helper.osplus as osplus
import epp.helper.xml.settings as settings
import epp.helper.filesystem as filesystem
from epp.fu.controller import fu_controller
from epp.helper.shortcuts import shot_id_path 
from epp.ui.set_shot_ui import Ui_dlgSetShot
from epp.__INFO__ import DEBUG, __VERSION__
import epp.bin.epp_addshot as control
from epp.helper.shortcuts import shot_root_path

class SetShotDialog(Ui_dlgSetShot, QDialog):
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
        super(SetShotDialog, self).__init__()
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

        self.cmbProject.currentIndexChanged.connect(self.update_shots)
        self.update_project()

        self._setup_defaults()

        return True

    # -------------------------------------------------------------------------------------
    def _setup_defaults(self):
        """docstring for _setup_defaults"""
        
        curproject = osplus.get_env("EPP_CURPROJECT")
        curshot = osplus.get_env("EPP_CURSHOT")

        if curproject != "":
            idx = self.cmbProject.findText(curproject, Qt.MatchExactly)

            if idx > -1:
                self.cmbProject.setCurrentIndex(idx)

        if curshot != "":
            idx = self.cmbShot.findText(curshot, Qt.MatchExactly)

            if idx > -1:
                self.cmbShot.setCurrentIndex(idx)

    # -------------------------------------------------------------------------------------
    def update_project(self):
        """docstring for update_project"""
        self.cmbProject.clear()

        # TODO: Could be slow on many folders ...
        for item in filesystem.projects(self.PROJECTROOT):
            curname, curdir = item
            if os.path.isdir(curdir):

                self.cmbProject.addItem(curname, curdir)

        if self.cmbProject.count() < 1:
            self.valid_projectname = False
        else:
            self.valid_projectname = True

    # -------------------------------------------------------------------------------------
    def update_shots(self):
        """docstring for update_project"""
        self.cmbShot.clear()

        sort = False
        if self.settings.get("preferences", "shotlistsort", "True", create=True).strip().lower() in ['true', '1', 'yes', 'on']:
            sort = True
        
        cur_project = self.cmbProject.currentText()
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
        cur_project = self.cmbProject.currentText()
        cur_shot = self.cmbShot.currentText()

        log.info("Setting project to " + cur_project)
        log.info("Setting shot to " + cur_shot)

        osplus.set_env("EPP_CURPROJECT", cur_project)
        osplus.set_env("EPP_CURSHOT", cur_shot)

        _fu = fu_controller()

        if not _fu.status(True):
            # No need for a dialog
            log.error("Fusion not running.", False)
        else:
            COMP_ROOT_DIR = shot_id_path(cur_project, cur_shot, "compositions")
            if os.path.isdir(COMP_ROOT_DIR):
                res = _fu.set_pathmap("Comps:", COMP_ROOT_DIR)
                log.info("Setting Comps: PathMap to {0} ({1})".format(COMP_ROOT_DIR, res[1]))

        super(SetShotDialog, self).accept()

# -------------------------------------------------------------------------------------
def main():
    """docstring for main"""
    app = QApplication([])
    app.setStyle(QStyleFactory.create("plastique") )
    palette = QPalette(QColor(62, 62, 62), QColor(62, 62, 62))
    palette.setColor(palette.Highlight, QColor(255*0.6, 198*0.6, 0))
    app.setPalette(palette)

    apd = SetShotDialog()
    if apd.STATUS:
        if DEBUG:
            apd.setWindowTitle(apd.windowTitle() + " v" + __VERSION__)
        apd.show()
        sys.exit(app.exec_())
        
            



if __name__ == '__main__':
    main()
