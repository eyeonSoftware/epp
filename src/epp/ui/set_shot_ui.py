# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\eyeon\repos\epp\src\_ui\set_shot.ui'
#
# Created: Wed Feb 20 18:08:17 2013
#      by: pyside-uic 0.2.14 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_dlgSetShot(object):
    def setupUi(self, dlgSetShot):
        dlgSetShot.setObjectName("dlgSetShot")
        dlgSetShot.resize(425, 405)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/epp_128.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        dlgSetShot.setWindowIcon(icon)
        self.verticalLayout_2 = QtGui.QVBoxLayout(dlgSetShot)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.lblHeader = QtGui.QLabel(dlgSetShot)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(14)
        self.lblHeader.setFont(font)
        self.lblHeader.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTop|QtCore.Qt.AlignTrailing)
        self.lblHeader.setMargin(10)
        self.lblHeader.setObjectName("lblHeader")
        self.verticalLayout_2.addWidget(self.lblHeader)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setContentsMargins(12, 9, 15, 24)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout1 = QtGui.QGridLayout()
        self.gridLayout1.setObjectName("gridLayout1")
        self._lblName = QtGui.QLabel(dlgSetShot)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self._lblName.sizePolicy().hasHeightForWidth())
        self._lblName.setSizePolicy(sizePolicy)
        self._lblName.setMinimumSize(QtCore.QSize(120, 0))
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self._lblName.setFont(font)
        self._lblName.setObjectName("_lblName")
        self.gridLayout1.addWidget(self._lblName, 3, 0, 1, 1)
        self._lblProject = QtGui.QLabel(dlgSetShot)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self._lblProject.sizePolicy().hasHeightForWidth())
        self._lblProject.setSizePolicy(sizePolicy)
        self._lblProject.setMinimumSize(QtCore.QSize(120, 0))
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self._lblProject.setFont(font)
        self._lblProject.setObjectName("_lblProject")
        self.gridLayout1.addWidget(self._lblProject, 1, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 10, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.gridLayout1.addItem(spacerItem, 2, 0, 1, 1)
        self.cmbProject = QtGui.QComboBox(dlgSetShot)
        self.cmbProject.setObjectName("cmbProject")
        self.gridLayout1.addWidget(self.cmbProject, 1, 1, 1, 1)
        self.cmbShot = QtGui.QComboBox(dlgSetShot)
        self.cmbShot.setObjectName("cmbShot")
        self.gridLayout1.addWidget(self.cmbShot, 3, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout1)
        self.line = QtGui.QFrame(dlgSetShot)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.lblStatus = QtGui.QLabel(dlgSetShot)
        self.lblStatus.setStyleSheet("")
        self.lblStatus.setOpenExternalLinks(True)
        self.lblStatus.setObjectName("lblStatus")
        self.verticalLayout.addWidget(self.lblStatus)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.butSet = QtGui.QPushButton(dlgSetShot)
        self.butSet.setObjectName("butSet")
        self.horizontalLayout_2.addWidget(self.butSet)
        self.butCancel = QtGui.QPushButton(dlgSetShot)
        self.butCancel.setObjectName("butCancel")
        self.horizontalLayout_2.addWidget(self.butCancel)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(dlgSetShot)
        QtCore.QObject.connect(self.butSet, QtCore.SIGNAL("clicked()"), dlgSetShot.accept)
        QtCore.QObject.connect(self.butCancel, QtCore.SIGNAL("clicked()"), dlgSetShot.reject)
        QtCore.QMetaObject.connectSlotsByName(dlgSetShot)
        dlgSetShot.setTabOrder(self.butSet, self.butCancel)

    def retranslateUi(self, dlgSetShot):
        dlgSetShot.setWindowTitle(QtGui.QApplication.translate("dlgSetShot", "Set Project/Shot", None, QtGui.QApplication.UnicodeUTF8))
        self.lblHeader.setText(QtGui.QApplication.translate("dlgSetShot", "Set Project/Shot", None, QtGui.QApplication.UnicodeUTF8))
        self._lblName.setToolTip(QtGui.QApplication.translate("dlgSetShot", "Project name and also the projects root directory name", None, QtGui.QApplication.UnicodeUTF8))
        self._lblName.setWhatsThis(QtGui.QApplication.translate("dlgSetShot", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">The </span><span style=\" font-size:8pt; font-weight:600;\">Name</span><span style=\" font-size:8pt;\"> for the project needs to be set based on studio conventions. This name is also used for the root folder of the project. Make sure it is file system safe and does not contain invalid characters. The default widget limits input to valid characters. Already existing project names can not be used to prevent data loss through overwriting.</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self._lblName.setText(QtGui.QApplication.translate("dlgSetShot", "Shot", None, QtGui.QApplication.UnicodeUTF8))
        self._lblProject.setToolTip(QtGui.QApplication.translate("dlgSetShot", "Format Template for production.", None, QtGui.QApplication.UnicodeUTF8))
        self._lblProject.setWhatsThis(QtGui.QApplication.translate("dlgSetShot", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">The <span style=\" font-weight:600;\">Format Templates</span> are presets of Width, Height, Framerage (FPS) and Aspect Ratios for a Production. They are stored in your <span style=\" font-style:italic;\">epp_root\\templates\\formats.xml</span> file. As starting point formats can be imported during install of epp from eyeon Fusion.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self._lblProject.setText(QtGui.QApplication.translate("dlgSetShot", "Project", None, QtGui.QApplication.UnicodeUTF8))
        self.lblStatus.setStatusTip(QtGui.QApplication.translate("dlgSetShot", "Warning Status", None, QtGui.QApplication.UnicodeUTF8))
        self.lblStatus.setText(QtGui.QApplication.translate("dlgSetShot", "WARINING", None, QtGui.QApplication.UnicodeUTF8))
        self.butSet.setStatusTip(QtGui.QApplication.translate("dlgSetShot", "Create Project and Directories", None, QtGui.QApplication.UnicodeUTF8))
        self.butSet.setText(QtGui.QApplication.translate("dlgSetShot", "Set", None, QtGui.QApplication.UnicodeUTF8))
        self.butCancel.setStatusTip(QtGui.QApplication.translate("dlgSetShot", "Cancel the operation", None, QtGui.QApplication.UnicodeUTF8))
        self.butCancel.setText(QtGui.QApplication.translate("dlgSetShot", "Cancel", None, QtGui.QApplication.UnicodeUTF8))

import epp_rc
