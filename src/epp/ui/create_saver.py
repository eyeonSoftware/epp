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
from epp.ui.create_saver_ui import Ui_dlgCreateSaver
from epp.__INFO__ import DEBUG, __VERSION__
from epp.fu.controller import fu_controller
from epp.helper.shortcuts import shot_root_path, shot_id_path
import epp.helper.filesystem as filesystem

class CreateSaverDialog(Ui_dlgCreateSaver, QDialog):
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

    PAT_VER = re.compile(r"(.+)_[vV](\d+)(.+)")
    PAT_PRE_VERSION = re.compile(r"""(.*)[^a-zA-Z0-9][vV](\d+)""")

    def __init__(self, parent=None):
        """
        Constructor.
        """
        super(CreateSaverDialog, self).__init__()
        self.setupUi(self)

        self.invalid_message = ""
        self._last_state = False

        self.valid_projectname = False
        self.valid_shotname = False
        #self.valid_compname = False
        self.SAVER_FILEPATH = ""                
        self.COMPOUTPUT_ROOT_DIR = ""

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

        # Make sure enter does not add to combo box
        #self.cmbName.installEventFilter(self)

        self.cmbProject.currentIndexChanged.connect(self._validate_path)
        self.cmbFormat.currentIndexChanged.connect(self._validate_path)

        #self.cmbShot.currentIndexChanged.connect(self.update_names)
        self.cmbShot.currentIndexChanged.connect(self._validate_path)

        self.lneName.textChanged.connect(self._validate_path)
        #self.cmbName.lineEdit().textChanged.connect(self._get_last_version)

        self.spnVersion.valueChanged.connect(self._validate_path)


        ret = self._setup_defaults()
        if not ret[0]:
            QMessageBox.critical(self, "Error", ret[1])
            return False

        self._setup_formats()

        self.butMatch.clicked.connect(self._match_version)
        self.butMatchName.clicked.connect(self._match_name)

        return True

    # -------------------------------------------------------------------------------------
    def _match_version(self):
        """docstring for _match_version"""
        comp_filename = os.path.basename(self.comp.GetAttrs("COMPS_FileName"))
        comp_versions = self._fu.get_version(comp_filename)
        version = int(comp_versions[0])

        self.spnVersion.setValue(version)

    # -------------------------------------------------------------------------------------
    def _match_name(self):
        """docstring for _match_version"""

        comp_filename = os.path.splitext(os.path.basename(self.comp.GetAttrs("COMPS_FileName")))[0]
        mat = self.PAT_PRE_VERSION.match(comp_filename)
        if mat is not None:
            self.lneName.setText(mat.group(1))
        else:
            self.lneName.setText(comp_filename)

    # -------------------------------------------------------------------------------------
    def _setup_formats(self):
        """docstring for """

        formats = self._fu.get_save_formats()

        self.cmbFormat.clear()

        def_ext = self.metadata.get("recent_format", ".exr")

        # Default to exr
        def_idx = 0

        i = 0
        for name, ext in sorted(formats.items()):

            self.cmbFormat.addItem("{0} ({1})".format(name, ext), ext)

            if ext.lower() == def_ext.lower():
                def_idx = i

            i += 1

        self.cmbFormat.setCurrentIndex(def_idx)


    # -------------------------------------------------------------------------------------
    def _setup_defaults(self):
        """docstring for update_name"""
        self._fu = fu_controller()

        ret = self._fu.get_comp()


        # No connection of composition?
        if ret[0] == False:
            return ret

        self.comp = ret[1]

        # Need metadata for find out about comps project and shot.
        # TODO: Maybe worth parsing the path from XML?
        ret = self._fu.get_meta("epp", self.comp)

        if ret[0] == False:
            return ret

        self.metadata = ret[1]

        if self.metadata is not None:
            project = self.metadata.get("project")
            shot = self.metadata.get("shot")

        if self.metadata is None or project is None or shot is None:
            return (False, "Not an epp composition. Metada missing.")

        idx = self.cmbProject.findText(project)
        if idx > -1:
            self.cmbProject.setCurrentIndex(idx)

        idx = self.cmbShot.findText(shot)
        if idx > -1:
            self.cmbShot.setCurrentIndex(idx)

        self.lneName.setText(shot)            


        self._match_name()
            
        self._match_version()

        return (True, "")

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



    # -------------------------------------------------------------------------------------
    def _validate_path(self, text):
        """docstring for _validate_path"""

        cur_project = self.cmbProject.currentText()
        cur_shot = self.cmbShot.currentText()
        self.COMPOUTPUT_ROOT_DIR = shot_id_path(cur_project, cur_shot, "compoutput")
        valid_dir = os.path.isdir(self.COMPOUTPUT_ROOT_DIR)

        text = self.lneName.text()
        valid_name = len(text) > 0
        file_exists = False
        self.SAVER_FILEPATH = ""

        if not self.valid_projectname:
            self.invalid_message = "<html><head><style type=text/css>a {{ color: white; }}\n a:link {{color:white; text-decoration:none; }}\n a:hover {{ color:#ffcc00; text-decoration:underline; }}</style></head><body><font color='#ffaa00'>No project found.</font>"
        elif not self.valid_shotname:
            self.invalid_message = "<html><head><style type=text/css>a {{ color: white; }}\n a:link {{color:white; text-decoration:none; }}\n a:hover {{ color:#ffcc00; text-decoration:underline; }}</style></head><body><font color='#ffaa00'>No shot found.</font>"
        #elif not self.valid_compname:
        #    self.invalid_message = "<font color='#ffaa00'>Composition location not found in shot template.</font>"
        elif not valid_name:
            self.invalid_message = "<font color='#ffaa00'>Invalid Name</font>"
        elif not valid_dir:
            self.invalid_message = "<font color='#ffaa00'>No composition ouput path found in shot template.</font>"
        else:            
            filename = u"{0}_v{1:03d}_".format(text, self.spnVersion.value())

            saver_filedir = os.path.join(self.COMPOUTPUT_ROOT_DIR, filename)
            self.SAVER_FILEPATH = os.path.join(saver_filedir, filename + str(self.cmbFormat.itemData(self.cmbFormat.currentIndex())))
            if os.path.isdir(saver_filedir):
                file_exists = True
                self.invalid_message = "<font color='#ffaa00'>Warning: Output directory already exists.</font>"

        self.lblPreview.setText(os.path.basename(self.SAVER_FILEPATH))
        cur_state = valid_name and self.valid_projectname and self.valid_shotname and valid_dir

        if not cur_state or file_exists:
            self.lblStatus.setText(self.invalid_message)
            self._status_fade.setDirection(QAbstractAnimation.Forward)
            self.compfilepath = ""
        else:
            self._status_fade.setDirection(QAbstractAnimation.Backward)

        # Does not account for file exists
        self.butCreate.setEnabled(cur_state)

        if (cur_state and not file_exists) != self._last_state:
            self._status_fade.start()

        self._last_state = (cur_state and not file_exists)
            
    # -------------------------------------------------------------------------------------
    def accept(self):
        """
        Check the connection.
        """

        if not self._fu.status(True):
            QMessageBox.critical(self, "Error", "Fusion not running.")
            return

        if os.path.isdir(os.path.dirname(self.SAVER_FILEPATH)):
            ret = QMessageBox.information(self, "Question", "Output directory does already exist.\nOverwrite '{0}'?".format(os.path.dirname(self.SAVER_FILEPATH)), QMessageBox.Yes | QMessageBox.No)
            if ret == QMessageBox.No:
                return

        #ret = self._fu.save_comp(self.COMPOUTPUT_FILEPATH)
        ret = self._fu.create_saver(self.SAVER_FILEPATH, comp=self.comp)

        if not ret[0]:
            QMessageBox.critical(self, "Error", ret[1])
            return

        # Try to save last used format
        # Not important so we don't check for results or save comp afterwards.
        self._fu.set_meta({"recent_format": str(self.cmbFormat.itemData(self.cmbFormat.currentIndex())) }, "epp", add=True)

        super(CreateSaverDialog, self).accept()

# -------------------------------------------------------------------------------------
def main():
    """docstring for main"""
    app = QApplication([])
    app.setStyle(QStyleFactory.create("plastique") )
    palette = QPalette(QColor(62, 62, 62), QColor(62, 62, 62))
    palette.setColor(palette.Highlight, QColor(255*0.6, 198*0.6, 0))
    app.setPalette(palette)

    apd = CreateSaverDialog()
    if apd.STATUS:
        if DEBUG:
            apd.setWindowTitle(apd.windowTitle() + " v" + __VERSION__)
        apd.show()
        sys.exit(app.exec_())
        
            



if __name__ == '__main__':
    main()
