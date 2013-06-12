#!/usr/bin/env python
#coding=utf-8
#? py

'''
add_shot_from_media.py
####################################

add_shot_from_media PySide interface controller. Makes use of the Designer generated _ui file.

:copyright: 2013 by eyeon Software Inc., eyeon Software Inc., see AUTHORS for more details
:license: Some rights reserved, see LICENSE for more details
'''

import glob
import os
import re
import sys

from PySide.QtCore import *
from PySide.QtGui import *

import epp.helper.osplus as osplus
import epp.helper.xml.settings as settings
from epp.ui.add_shot_from_media_ui import Ui_dlgAddShotFromMedia
from epp.__INFO__ import DEBUG, __VERSION__
from epp.model.format import Format
import epp.bin.epp_addshotfrommedia as control
from epp.gen.controller import gen_controller
from epp.helper.xml.dir_query import DirQuery
import epp.helper.log as log

class AddShotFromMediaDialog(Ui_dlgAddShotFromMedia, QDialog):
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
        """ Constructor.
        """
        super(AddShotFromMediaDialog, self).__init__()
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
            log.error("Could not find EPP ROOT directory.\n{0}".format(epp_root), True)
            return False

        self.settings = settings.XMLSettings(os.path.join(epp_root, "config.xml") )
        self.PROJECTROOT = self.settings.get("paths", "projectdir")
        if not self.PROJECTROOT.endswith(os.path.sep):
            self.PROJECTROOT = self.PROJECTROOT + os.path.sep 

        if self.PROJECTROOT is None:
            log.error("No Project Directory configured in config.xml.", True)
            return False


        self._setup_header(epp_root)
        #self._setup_name_widget(epp_root)
        self._setup_status()

        # Require Generation
        if not self._setup_generation():
            msg = "Could not establish connection with Generation. Make sure it is running."
            log.error(msg, True)
            return False

        # Need edit rights for this one!
        if not self._gen.allow_changes(True):
            return False

        if not self._setup_project():
            msg = "Project directory from Generation Project invalid: {0}".format(self.PROJECTDIR)
            log.error(msg, True)
            return False

        if not self._setup_shot():
            msg = "Project directory from Generation Project invald: {0}".format(self.PROJECTDIR)
            log.error(msg, True)
            return False

        selected_versions = self._gen.selected_versions()
        if len(selected_versions) < 1:
            msg = "No versions selected."
            log.error(msg, True)
            return False

        meta = selected_versions[0].Metadata(selected_versions[0].InPoint)
        self.preview_path = meta['Data']['File']['Path']

        if not self._setup_patterns(epp_root):
            msg = "No parsing patterns found."
            log.warning(msg)
            return False

        # We can't work without structs
        if not self._setup_structs(epp_root):
            msg = "Could not find directory structure files in templates.\n{0}".format(os.path.join(epp_root, "templates", "shot_dirs"))
            log.error(msg, True)
            return False

        return True

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
    def _setup_patterns(self, epp_root):
        """docstring for _setup_patterns"""
        self.patterns = self.settings.findall("shotpattern", "pattern")

        self.cmbParsingPattern.clear()

        for name, pattern in self.patterns.items():
            self.cmbParsingPattern.addItem(name, pattern)

        if len(self.patterns) < 1:
            return False

        self.cmbParsingPattern.currentIndexChanged[str].connect(self._pattern_changed)

        # Initial Preview
        self._pattern_changed(self.cmbParsingPattern.currentText())

        return True

    # -------------------------------------------------------------------------------------
    def _pattern_changed(self, new_pattern):
        """docstring for _pattern_changed"""
        self.PAT = re.compile(self.patterns[new_pattern])

        self.lblNamePreview.setText(self.get_shotname(self.preview_path))

    # -------------------------------------------------------------------------------------
    def get_shotname(self, path):
        """docstring for get_shotname"""
        pass        
        mat = self.PAT.findall(path)
        if len(mat):
            shotname = mat[0]
        else:
            shotname = path
        return shotname

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

        return True


    # -------------------------------------------------------------------------------------
    def _setup_generation(self):
        """docstring for _setup_generation"""
        self._gen = gen_controller()

        return self._gen.status()

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



    # -------------------------------------------------------------------------------------
    def _validate_name(self, text):
        """docstring for _validate_name"""
        pass
            
    # -------------------------------------------------------------------------------------
    def _replace_whitespaces(self, text):
        """docstring for _replace_whitespaces"""
        cur = self.plugName.cursorPosition()
        self.plugName.setText(text.replace(" ", "_"))
        self.plugName.setCursorPosition(cur)
        
    # -------------------------------------------------------------------------------------
    def _setup_structs(self, epp_root):
        """Setup controls for Directory Strucutre"""

        xml_shot_dir_pat = os.path.join(epp_root, "templates", "shot_dirs", "*.xml")

        xml_shot_dirs = glob.glob(xml_shot_dir_pat)

        if len(xml_shot_dirs) < 1:
            # No shot Dirs defined
            return False

        for template in sorted(xml_shot_dirs):
            template_name = os.path.splitext(os.path.basename(template))[0]
            self.cmbDirStructure.addItem(template_name)

        return True

    # -------------------------------------------------------------------------------------
    def accept(self):
        """
        Check the connection.
        """
        if not self._gen.status(True):
            log.error("Could not establish connection with Generation. Make sure it is running.", True)
            return

        # Need edit rights for this one!
        if not self._gen.allow_changes(True):
            return 
        
        selected_versions = self._gen.selected_versions()
        if len(selected_versions) < 1:
            msg = "No versions selected."
            log.error(msg, True)
            return

        ignore = False
        for version in selected_versions:

            meta = version.Metadata(version.InPoint)
            path = meta['Data']['File']['Path']

            shotname = self.get_shotname(path)
            ret, msg = control.add_shot_from_media(self.PROJECTNAME, shotname, self.cmbDirStructure.currentText()+".xml", self._gen, self.cmbInsertPosition.currentIndex()+3, version.GetSlotClip())
            if not ret:
                log.error(msg)
                if not ignore:
                    ret = QMessageBox.critical(self, "Error", msg+"\nIgnore?", QMessageBox.Yes | QMessageBox.YesToAll | QMessageBox.Cancel)
                    if ret == QMessageBox.Cancel:
                        return
                    elif ret == QMessageBox.YesToAll:
                        ignore = True
            else:
                log.info(msg)

        super(AddShotFromMediaDialog, self).accept()

# -------------------------------------------------------------------------------------
def main():
    """docstring for main"""
    app = QApplication([])
    app.setStyle(QStyleFactory.create("plastique") )
    palette = QPalette(QColor(62, 62, 62), QColor(62, 62, 62))
    palette.setColor(palette.Highlight, QColor(255*0.6, 198*0.6, 0))
    app.setPalette(palette)

    apd = AddShotFromMediaDialog()
    if apd.STATUS:
        if DEBUG:
            apd.setWindowTitle(apd.windowTitle() + " v" + __VERSION__)
        apd.show()
        sys.exit(app.exec_())
        
if __name__ == '__main__':
    main()
