# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'impact_functions_doc_base.ui'
#
# Created: Tue Sep 11 09:35:47 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ImpactFunctionsDocBase(object):
    def setupUi(self, ImpactFunctionsDocBase):
        ImpactFunctionsDocBase.setObjectName(_fromUtf8("ImpactFunctionsDocBase"))
        ImpactFunctionsDocBase.resize(727, 403)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/inasafe/icon.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        ImpactFunctionsDocBase.setWindowIcon(icon)
        self.gridLayout = QtGui.QGridLayout(ImpactFunctionsDocBase)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.webView = QtWebKit.QWebView(ImpactFunctionsDocBase)
        self.webView.setUrl(QtCore.QUrl(_fromUtf8("about:blank")))
        self.webView.setObjectName(_fromUtf8("webView"))
        self.gridLayout.addWidget(self.webView, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ImpactFunctionsDocBase)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(ImpactFunctionsDocBase)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ImpactFunctionsDocBase.reject)
        QtCore.QMetaObject.connectSlotsByName(ImpactFunctionsDocBase)

    def retranslateUi(self, ImpactFunctionsDocBase):
        ImpactFunctionsDocBase.setWindowTitle(QtGui.QApplication.translate("ImpactFunctionsDocBase", "InaSAFE Impact Functions", None, QtGui.QApplication.UnicodeUTF8))

from PyQt4 import QtWebKit
import resources_rc
