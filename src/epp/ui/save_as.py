#!/usr/bin/env python
#coding=utf-8
#? py

'''
save_as.py
####################################

save_as PySide interface controller. Makes use of the Designer generated _ui file.

:copyright: 2013 by eyeon Software Inc., eyeon Software Inc., see AUTHORS for more details
:license: Some rights reserved, see LICENSE for more details
'''

import glob
import os
import re
import sys
import lxml.etree as etree

from PySide.QtCore import *
from PySide.QtGui import *

import epp.helper.osplus as osplus
import epp.helper.xml.settings as settings
import epp.helper.filesystem as filesystem
from epp.ui.save_as_ui import Ui_dlgSaveAs
from epp.__INFO__ import DEBUG, __VERSION__
from epp.fu.controller import fu_controller
from epp.helper.shortcuts import shot_root_path, shot_id_path, project_format_object
import epp.helper.log as log

class SaveAsDialog(Ui_dlgSaveAs, QDialog):
    """
    This class represents 
    """

    PAT_VER = re.compile(r"(.+)_[vV](\d+)(.+)")

    def __init__(self, parent=None):
        """
        Constructor.
        """
        super(SaveAsDialog, self).__init__()
        self.setupUi(self)

        self.invalid_message = ""
        self._last_state = False

        self.valid_projectname = False
        self.valid_shotname = False
        self.valid_compname = False
        self.COMP_FILEPATH = ""                
        self.COMP_ROOT_DIR = ""

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

        _fu = fu_controller()
        if not _fu.status(True):
            log.error("Fusion not running.", True)
            return False

        epp_root = osplus.get_env("EPP_ROOT")

        if not os.path.isdir(epp_root):
            log.error("Could not find EPP ROOT directory.\n{0}".format(epp_root), True)
            return False

        self.settings = settings.XMLSettings(os.path.join(epp_root, "config.xml") )
        self.PROJECTROOT = self.settings.get("paths", "projectdir")

        if self.PROJECTROOT is None:
            log.error("No Project Directory configured in config.xml.", True)
            return False

        self._setup_header(epp_root)
        self._setup_status()

        self.cmbProject.currentIndexChanged.connect(self.update_shots)
        self.update_project()

        # Make sure enter does not add to combo box
        self.cmbName.installEventFilter(self)

        self.cmbProject.currentIndexChanged.connect(self._validate_path)

        self.cmbShot.currentIndexChanged.connect(self.update_names)
        self.cmbShot.currentIndexChanged.connect(self._validate_path)

        self.cmbName.currentIndexChanged.connect(self._validate_path)
        self.cmbName.lineEdit().textChanged.connect(self._validate_path)
        self.cmbName.lineEdit().textChanged.connect(self._get_last_version)

        self.spnVersion.valueChanged.connect(self._validate_path)
        self.butNext.clicked.connect(self._get_last_version)
        self._setup_defaults()
        self.update_names()

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
    def update_names(self):
        """docstring for update_project"""
        self.cmbName.clear()

        
        cur_project = self.cmbProject.currentText()
        cur_shot = self.cmbShot.currentText()
        if cur_project == "" or cur_shot == "":
            return
        
        self.COMP_ROOT_DIR = shot_id_path(cur_project, cur_shot, "compositions")

        if self.COMP_ROOT_DIR == "":
            self.valid_compname = False
            return

        self.valid_compname = True

        # TODO: More then comp
        for item in sorted(glob.glob(os.path.join(self.COMP_ROOT_DIR, "*.comp")), cmp=lambda x,y: cmp(os.path.basename(x).lower(), os.path.basename(y).lower())):
            if os.path.isfile(item):

                mat = self.PAT_VER.match(os.path.basename(item))

                if mat is not None:
                    base, ver, post = mat.groups()
                else:
                    base = item

                self.cmbName.addItem(base, item)


        # Dirty Hack
        self.cmbName.lineEdit().setText(self.cmbShot.currentText().replace("\\", "_"))
        self._get_last_version()

    # -------------------------------------------------------------------------------------
    def _get_last_version(self):
        """docstring for _get_last_version"""

        text = self.cmbName.currentText()

        last_ver = 1
        for item in sorted(glob.glob(os.path.join(self.COMP_ROOT_DIR, text+"_v*.comp")), cmp=lambda x,y: cmp(os.path.basename(x).lower(), os.path.basename(y).lower())):
            if os.path.isfile(item):

                mat = self.PAT_VER.match(os.path.basename(item))
                if mat is not None:
                    base, ver, post = mat.groups()
                    last_ver = max(last_ver, int(ver)+1)

        self.spnVersion.setValue(last_ver)                
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



    # -------------------------------------------------------------------------------------
    def _validate_path(self, text):
        """docstring for _validate_path"""

        text = self.cmbName.currentText()
        valid_name = len(text) > 0
        file_exists = False
        self.COMP_FILEPATH = ""

        if not self.valid_projectname:
            self.invalid_message = "<html><head><style type=text/css>a {{ color: white; }}\n a:link {{color:white; text-decoration:none; }}\n a:hover {{ color:#ffcc00; text-decoration:underline; }}</style></head><body><font color='#ffaa00'>No project found.</font>"
        elif not self.valid_shotname:
            self.invalid_message = "<html><head><style type=text/css>a {{ color: white; }}\n a:link {{color:white; text-decoration:none; }}\n a:hover {{ color:#ffcc00; text-decoration:underline; }}</style></head><body><font color='#ffaa00'>No shot found.</font>"
        elif not self.valid_compname:
            self.invalid_message = "<font color='#ffaa00'>Composition location not found in shot template.</font>"
        elif not valid_name:
            self.invalid_message = "<font color='#ffaa00'>Invalid Name</font>"
        else:            
            filename = u"{0}_v{1:03d}.comp".format(text, self.spnVersion.value())


            comp_filepath = os.path.join(self.COMP_ROOT_DIR, filename)
            self.COMP_FILEPATH = comp_filepath
            if os.path.isfile(comp_filepath):
                file_exists = True
                self.invalid_message = "<font color='#ffaa00'>Warning: File already exists.</font>"

        self.lblPreview.setText(os.path.basename(self.COMP_FILEPATH))
        cur_state = valid_name and self.valid_projectname and self.valid_shotname and self.valid_compname

        if not cur_state or file_exists:
            self.lblStatus.setText(self.invalid_message)
            self._status_fade.setDirection(QAbstractAnimation.Forward)
            self.compfilepath = ""
        else:
            self._status_fade.setDirection(QAbstractAnimation.Backward)

        # Does not account for file exists
        self.butSave.setEnabled(cur_state)

        if (cur_state and not file_exists) != self._last_state:
            self._status_fade.start()

        self._last_state = (cur_state and not file_exists)
            
    # -------------------------------------------------------------------------------------
    def eventFilter(self, object_, event):
        """
        Make sure enter does not add to combo box
        """

        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
                return True

        return QWidget.eventFilter(self, object_, event)
            

        
    # -------------------------------------------------------------------------------------
    def accept(self):
        """
        Check the connection.
        """

        _fu = fu_controller()

        if not _fu.status(True):
            log.error("Fusion not running.", True)
            return

        if os.path.isfile(self.COMP_FILEPATH):
            ret = QMessageBox.information(self, "Question", "Composition does already exist.\nOverwrite '{0}'".format(os.path.basename(self.COMP_FILEPATH)), QMessageBox.Yes | QMessageBox.No)
            if ret == QMessageBox.No:
                return

        cur_project = self.cmbProject.currentText()
        cur_shot = self.cmbShot.currentText()

        ret = _fu.save_comp(self.COMP_FILEPATH, {"project": str(cur_project), "shot": str(cur_shot)})

        if not ret[0]:
            log.error(ret[1], True)
            return

        log.info("Saved Comp to {0}".format(self.COMP_FILEPATH))
        self.hide()

        if self.chkUpdateSavers.isChecked():
            ret = _fu.update_savers(self.spnVersion.value())

        if self.chkFormat.isChecked():
            _fu.set_format(project_format_object(cur_project))

        osplus.set_env("EPP_CURPROJECT", self.cmbProject.currentText())
        osplus.set_env("EPP_CURSHOT", self.cmbShot.currentText())

        COMP_ROOT_DIR = os.path.dirname(self.COMP_FILEPATH)
        if os.path.isdir(COMP_ROOT_DIR):
            res = _fu.set_pathmap("Comps:", COMP_ROOT_DIR)
            log.info("Setting Comps: PathMap to {0} ({1})".format(COMP_ROOT_DIR, res[1]))

        super(SaveAsDialog, self).accept()

# -------------------------------------------------------------------------------------
def main():
    """docstring for main"""
    # Fusion doesn't have argv so use []
    app = QApplication([])
    app.setStyle(QStyleFactory.create("plastique") )
    palette = QPalette(QColor(62, 62, 62), QColor(62, 62, 62))
    palette.setColor(palette.Highlight, QColor(255*0.6, 198*0.6, 0))
    app.setPalette(palette)

    apd = SaveAsDialog()
    if apd.STATUS:
        if DEBUG:
            apd.setWindowTitle(apd.windowTitle() + " v" + __VERSION__)
        apd.show()
        sys.exit(app.exec_())
        
if __name__ == '__main__':
    main()
