# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'is_help_base.ui'
#
# Created: Wed Mar 28 11:30:12 2012
#      by: PyQt4 UI code generator 4.8.5
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ISHelpBase(object):
    def setupUi(self, ISHelpBase):
        ISHelpBase.setObjectName(_fromUtf8("ISHelpBase"))
        ISHelpBase.resize(727, 403)
        ISHelpBase.setWindowTitle(QtGui.QApplication.translate("ISHelpBase", "InaSAFE Help", None, QtGui.QApplication.UnicodeUTF8))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/inasafe/icon.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        ISHelpBase.setWindowIcon(icon)
        self.gridLayout = QtGui.QGridLayout(ISHelpBase)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.webView = QtWebKit.QWebView(ISHelpBase)
        self.webView.setUrl(QtCore.QUrl(_fromUtf8("about:blank")))
        self.webView.setObjectName(_fromUtf8("webView"))
        self.gridLayout.addWidget(self.webView, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ISHelpBase)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(ISHelpBase)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ISHelpBase.reject)
        QtCore.QMetaObject.connectSlotsByName(ISHelpBase)

    def retranslateUi(self, ISHelpBase):
        pass

from PyQt4 import QtWebKit
import gui.resources_rc
