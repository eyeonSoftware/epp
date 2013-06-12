# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\eyeon\repos\epp\src\_ui\base_projectshot.ui'
#
# Created: Fri Apr 12 13:24:23 2013
#      by: pyside-uic 0.2.14 running on PySide 1.1.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_dlgProjectShot(object):
    def setupUi(self, dlgProjectShot):
        dlgProjectShot.setObjectName("dlgProjectShot")
        dlgProjectShot.resize(425, 405)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/epp_128.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        dlgProjectShot.setWindowIcon(icon)
        self.verticalLayout_2 = QtGui.QVBoxLayout(dlgProjectShot)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.lblHeader = QtGui.QLabel(dlgProjectShot)
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
        self._lblShot = QtGui.QLabel(dlgProjectShot)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self._lblShot.sizePolicy().hasHeightForWidth())
        self._lblShot.setSizePolicy(sizePolicy)
        self._lblShot.setMinimumSize(QtCore.QSize(120, 0))
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self._lblShot.setFont(font)
        self._lblShot.setObjectName("_lblShot")
        self.gridLayout1.addWidget(self._lblShot, 3, 0, 1, 1)
        self._lblProject = QtGui.QLabel(dlgProjectShot)
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
        self.cmbProject = QtGui.QComboBox(dlgProjectShot)
        self.cmbProject.setObjectName("cmbProject")
        self.gridLayout1.addWidget(self.cmbProject, 1, 1, 1, 1)
        self.cmbShot = QtGui.QComboBox(dlgProjectShot)
        self.cmbShot.setObjectName("cmbShot")
        self.gridLayout1.addWidget(self.cmbShot, 3, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout1)
        self.line = QtGui.QFrame(dlgProjectShot)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.lblStatus = QtGui.QLabel(dlgProjectShot)
        self.lblStatus.setStyleSheet("")
        self.lblStatus.setOpenExternalLinks(True)
        self.lblStatus.setObjectName("lblStatus")
        self.verticalLayout.addWidget(self.lblStatus)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.butAccept = QtGui.QPushButton(dlgProjectShot)
        self.butAccept.setObjectName("butAccept")
        self.horizontalLayout_2.addWidget(self.butAccept)
        self.butCancel = QtGui.QPushButton(dlgProjectShot)
        self.butCancel.setObjectName("butCancel")
        self.horizontalLayout_2.addWidget(self.butCancel)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(dlgProjectShot)
        QtCore.QObject.connect(self.butAccept, QtCore.SIGNAL("clicked()"), dlgProjectShot.accept)
        QtCore.QObject.connect(self.butCancel, QtCore.SIGNAL("clicked()"), dlgProjectShot.reject)
        QtCore.QMetaObject.connectSlotsByName(dlgProjectShot)
        dlgProjectShot.setTabOrder(self.butAccept, self.butCancel)

    def retranslateUi(self, dlgProjectShot):
        dlgProjectShot.setWindowTitle(QtGui.QApplication.translate("dlgProjectShot", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.lblHeader.setText(QtGui.QApplication.translate("dlgProjectShot", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self._lblShot.setToolTip(QtGui.QApplication.translate("dlgProjectShot", "Project name and also the projects root directory name", None, QtGui.QApplication.UnicodeUTF8))
        self._lblShot.setWhatsThis(QtGui.QApplication.translate("dlgProjectShot", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">The </span><span style=\" font-size:8pt; font-weight:600;\">Name</span><span style=\" font-size:8pt;\"> for the project needs to be set based on studio conventions. This name is also used for the root folder of the project. Make sure it is file system safe and does not contain invalid characters. The default widget limits input to valid characters. Already existing project names can not be used to prevent data loss through overwriting.</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self._lblShot.setText(QtGui.QApplication.translate("dlgProjectShot", "Shot", None, QtGui.QApplication.UnicodeUTF8))
        self._lblProject.setToolTip(QtGui.QApplication.translate("dlgProjectShot", "Format Template for production.", None, QtGui.QApplication.UnicodeUTF8))
        self._lblProject.setWhatsThis(QtGui.QApplication.translate("dlgProjectShot", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">The <span style=\" font-weight:600;\">Format Templates</span> are presets of Width, Height, Framerage (FPS) and Aspect Ratios for a Production. They are stored in your <span style=\" font-style:italic;\">epp_root\\templates\\formats.xml</span> file. As starting point formats can be imported during install of epp from eyeon Fusion.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self._lblProject.setText(QtGui.QApplication.translate("dlgProjectShot", "Project", None, QtGui.QApplication.UnicodeUTF8))
        self.lblStatus.setStatusTip(QtGui.QApplication.translate("dlgProjectShot", "Warning Status", None, QtGui.QApplication.UnicodeUTF8))
        self.lblStatus.setText(QtGui.QApplication.translate("dlgProjectShot", "WARNING", None, QtGui.QApplication.UnicodeUTF8))
        self.butAccept.setStatusTip(QtGui.QApplication.translate("dlgProjectShot", "Create Project and Directories", None, QtGui.QApplication.UnicodeUTF8))
        self.butAccept.setText(QtGui.QApplication.translate("dlgProjectShot", "Ok", None, QtGui.QApplication.UnicodeUTF8))
        self.butCancel.setStatusTip(QtGui.QApplication.translate("dlgProjectShot", "Cancel the operation", None, QtGui.QApplication.UnicodeUTF8))
        self.butCancel.setText(QtGui.QApplication.translate("dlgProjectShot", "Cancel", None, QtGui.QApplication.UnicodeUTF8))

import epp_rc
