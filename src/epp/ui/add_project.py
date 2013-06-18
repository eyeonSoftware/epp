#!/usr/bin/env python
#coding=utf-8
#? py

'''
add_project.py
####################################

add_project PySide interface controller. Makes use of the Designer generated _ui file.

:copyright: 2013 by eyeon Software Inc., eyeon Software Inc., see AUTHORS for more details
:license: Some rights reserved, see LICENSE for more details
'''

import glob
import os
import sys

from PySide.QtCore import *
from PySide.QtGui import *

import epp.helper.osplus as osplus
import epp.helper.xml.settings as settings
from epp.ui.add_project_ui import Ui_dlgAddProject
from epp import __INFO__
from epp.__INFO__ import DEBUG, __VERSION__
from epp.model.format import Format
import epp.bin.epp_addproject as control
from epp.gen.controller import gen_controller

class AddProjectDialog(Ui_dlgAddProject, QDialog):
    """
    This class represents 
    """
    def __init__(self, parent=None):
        """
        Constructor.
        """
        super(AddProjectDialog, self).__init__()
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
        self._setup_name_widget(epp_root)
        self._setup_formats(epp_root)
        self._setup_status()

        # Require Generation
        if not self._setup_generation():
            QMessageBox.critical(self, "Error", "Could not establish connection with Generation. Make sure it is running.")
            return False

        # We can't work without structs
        if not self._setup_structs(epp_root):
            QMessageBox.critical(self, "Error", "Could not find directory structure files in templates.\n{0}".format(os.path.join(epp_root, "templates", "project_dirs")))
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
        valid_name = len(text) > 0

        text = self.plugName.text()

        if not valid_name:
            self.lblStatus.setText("<font color='#ffaa00'>Invalid Project Name</font>")
            self._status_fade.setDirection(QAbstractAnimation.Forward)
        else:
            self._status_fade.setDirection(QAbstractAnimation.Backward)

            project_dir = os.path.join(self.PROJECTROOT, text)
            if os.path.isdir(project_dir):
                self.lblStatus.setText("<html><head><style type=text/css>a {{ color: white; }}\n a:link {{color:white; text-decoration:none; }}\n a:hover {{ color:#ffcc00; text-decoration:underline; }}</style></head><body><font color='#ffaa00'>Project Directory already exists:</font> <a href='file:///{0}'>{0}</a></body></html>".format(project_dir, project_dir.replace("\\", "/")))
                valid_name = False
                self._status_fade.setDirection(QAbstractAnimation.Forward)
            else:
                self._status_fade.setDirection(QAbstractAnimation.Backward)

        if self._last_valid_name != valid_name:
            self._status_fade.start()
        
        self._last_valid_name = valid_name

        self.butAdd.setEnabled(valid_name) 
            

    # -------------------------------------------------------------------------------------
    def _setup_name_widget(self, epp_root):
        """docstring for _setup_name_widget"""
        namewidget = self.settings.get("projectname", "widget", "QLineEdit", create=True)
        validation = self.settings.get("projectname", "validation", r"[a-zA-Z0-9_ \\]+", create=True)
        replace_whitespaces = self.settings.get("projectname", "replacewhitespace", "True", create=True).lower() in ["true", "on", "yes", "1"]
        mask = self.settings.get("projectname", "mask", "", create=True)
        try:
            maxlength = int(self.settings.get("projectname", "maxlength", "0", create=True))
        except ValueError:
            maxlength = 0

        # TODO Load Plugin
        self.plugName = None
        if False: #namewidget == "QLineEdit":
            pass
        else: #namewidget == "QLineEditValid": # Default
            self.plugName = QLineEdit(self)
            
            # Sanity helper: Return converted str instead of unicode to make gen happy
            # Normally should have inherited from QLineEdit but for this cheat I use this
            # instead.
            self.plugName.text = osplus.unitostr_decorator(self.plugName.text)

            # Mask overrides others 
            if len(mask.strip()) > 0:
                self.plugName.setInputMask(mask)
                # Get the best monospaced thing you can get
                font = QFont("Monospace");
                font.setStyleHint(QFont.TypeWriter)
                self.plugName.setFont(font)
                
            else:
                if maxlength > 0:
                    self.plugName.setMaxLength(maxlength)

                if len(validation.strip()) > 0:
                    rx = QRegExp(validation)
                    self.plugName.setValidator(QRegExpValidator(rx, self))

                if replace_whitespaces:
                    # Replace whitespace with _
                    self.plugName.textEdited.connect(self._replace_whitespaces)

        if self.plugName is not None:
            self.plugName.setToolTip(self._lblName.toolTip())
            self.plugName.setWhatsThis(self._lblName.whatsThis())

            self.butAdd.setEnabled(False)
            self.plugName.textChanged.connect(self._validate_name)
            self.gridLayout1.addWidget(self.plugName, 1, 2)

        self.plugName.setFocus()            

    # -------------------------------------------------------------------------------------
    def _replace_whitespaces(self, text):
        """docstring for _replace_whitespaces"""
        cur = self.plugName.cursorPosition()
        self.plugName.setText(text.replace(" ", "_"))
        self.plugName.setCursorPosition(cur)
        
    # -------------------------------------------------------------------------------------
    def _setup_structs(self, epp_root):
        """Setup controls for Directory Strucutre"""

        xml_project_dir_pat = os.path.join(epp_root, "templates", "project_dirs", "*.xml")

        xml_project_dirs = glob.glob(xml_project_dir_pat)

        if len(xml_project_dirs) < 1:
            # No Project Dirs defined
            return False

        for template in sorted(xml_project_dirs):
            template_name = os.path.splitext(os.path.basename(template))[0]
            self.cmbDirStructure.addItem(template_name)

        return True


    # -------------------------------------------------------------------------------------
    def _setup_formats(self, epp_root):
        """docstring for _setup_formats"""

        format_settings = settings.XMLSettings(os.path.join(epp_root, "templates", "formats.xml"), root="formats", cache=True)

        if len(format_settings) < 1:
            return

        self.cmbFormatTemplate.addItem("Custom")

        for cur_format in sorted(format_settings):
            if not "name" in cur_format[1].keys():
                continue
            cur_name = cur_format[1]['name']
            if cur_name.lower() == "custom":
                continue

            self.cmbFormatTemplate.addItem(cur_format[1]['name'])

        # For later access
        self.format_settings = format_settings

        # Events
        self.FORMAT_DIRTY = False
        self.LOCK = False
        self.spnWidth.valueChanged.connect(self._format_value_changed)
        self.spnHeight.valueChanged.connect(self._format_value_changed)
        self.spnFPS.valueChanged.connect(self._format_value_changed)
        self.spnFPS.valueChanged.connect(self._format_value_changed)
        self.spnAspectX.valueChanged.connect(self._format_value_changed)
        self.spnAspectY.valueChanged.connect(self._format_value_changed)

        self.cmbFormatTemplate.currentIndexChanged[str].connect(self._format_changed)

    # -------------------------------------------------------------------------------------
    def _format_changed(self, text):
        """The format itself was changed"""
        if text.lower() == "custom":
            return

        self.LOCK = True

        width = self.format_settings.get("format", "width", topic_attr={"name": text})
        height = self.format_settings.get("format", "height", topic_attr={"name": text})
        fps = self.format_settings.get("format", "framerate", topic_attr={"name": text})
        aspectx = self.format_settings.get("format", "aspectx", topic_attr={"name": text})
        aspecty = self.format_settings.get("format", "aspecty", topic_attr={"name": text})

        if width is not None:
            self.spnWidth.setValue(int(width))
        if height is not None:
            self.spnHeight.setValue(int(height))
        if fps is not None:
            self.spnFPS.setValue(float(fps))
        if aspectx is not None:
            self.spnAspectX.setValue(float(aspectx))
        if aspecty is not None:
            self.spnAspectY.setValue(float(aspecty))
        
        self.LOCK = False

    # -------------------------------------------------------------------------------------
    def _format_value_changed(self):
        """A value from the format has been changed"""
        if self.LOCK:
            return

        self.FORMAT_DIRTY = True
        self.cmbFormatTemplate.setCurrentIndex(0) # Custom

    # -------------------------------------------------------------------------------------
    def accept(self):
        """
        Check the connection.
        """
        if not self._gen.status(True):
            QMessageBox.critical(self, "Error", "Could not establish connection with Generation. Make sure it is running.")
            return

        project_format = Format(self.spnWidth.value(), self.spnHeight.value(), self.spnFPS.value(), self.spnAspectX.value(), self.spnAspectY.value(), self.cmbFormatTemplate.currentText())

        """
        print self.plugName.text()
        print self.cmbDirStructure.currentText()+".xml"
        print project_format
        """

        print self.plugName.text()
        ret, msg = control.add_project(self.plugName.text(), self.cmbDirStructure.currentText()+".xml", project_format, self._gen)

        if not ret:
            QMessageBox.critical(self, "Error", "Could not create Project.\n" + msg)
            return

        super(AddProjectDialog, self).accept()

# -------------------------------------------------------------------------------------
def main():
    """docstring for main"""
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("plastique") )
    palette = QPalette(QColor(62, 62, 62), QColor(62, 62, 62))
    palette.setColor(palette.Highlight, QColor(255*0.6, 198*0.6, 0))
    app.setPalette(palette)

    apd = AddProjectDialog()
    if apd.STATUS:
        if DEBUG:
            apd.setWindowTitle(apd.windowTitle() + " v" + __VERSION__)
        apd.show()
        sys.exit(app.exec_())
if __name__ == '__main__':
    main()
        
            


