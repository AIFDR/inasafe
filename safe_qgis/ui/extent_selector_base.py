# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'extent_selector_base.ui'
#
# Created: Wed Oct 29 13:31:51 2014
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_ExtentSelectorBase(object):
    def setupUi(self, ExtentSelectorBase):
        ExtentSelectorBase.setObjectName(_fromUtf8("ExtentSelectorBase"))
        ExtentSelectorBase.resize(624, 29)
        font = QtGui.QFont()
        font.setPointSize(9)
        ExtentSelectorBase.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/inasafe/icon.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        ExtentSelectorBase.setWindowIcon(icon)
        self.horizontalLayout = QtGui.QHBoxLayout(ExtentSelectorBase)
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.x_minimum = QtGui.QDoubleSpinBox(ExtentSelectorBase)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.x_minimum.setFont(font)
        self.x_minimum.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.x_minimum.setDecimals(7)
        self.x_minimum.setMinimum(-999999999.0)
        self.x_minimum.setMaximum(999999999.0)
        self.x_minimum.setObjectName(_fromUtf8("x_minimum"))
        self.horizontalLayout.addWidget(self.x_minimum)
        self.y_minimum = QtGui.QDoubleSpinBox(ExtentSelectorBase)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.y_minimum.setFont(font)
        self.y_minimum.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.y_minimum.setDecimals(7)
        self.y_minimum.setMinimum(-999999999.0)
        self.y_minimum.setMaximum(999999999.0)
        self.y_minimum.setObjectName(_fromUtf8("y_minimum"))
        self.horizontalLayout.addWidget(self.y_minimum)
        self.x_maximum = QtGui.QDoubleSpinBox(ExtentSelectorBase)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.x_maximum.setFont(font)
        self.x_maximum.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.x_maximum.setDecimals(7)
        self.x_maximum.setMinimum(-999999999.0)
        self.x_maximum.setMaximum(999999999.0)
        self.x_maximum.setObjectName(_fromUtf8("x_maximum"))
        self.horizontalLayout.addWidget(self.x_maximum)
        self.y_maximum = QtGui.QDoubleSpinBox(ExtentSelectorBase)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.y_maximum.setFont(font)
        self.y_maximum.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.y_maximum.setDecimals(7)
        self.y_maximum.setMinimum(-999999999.0)
        self.y_maximum.setMaximum(999999999.0)
        self.y_maximum.setObjectName(_fromUtf8("y_maximum"))
        self.horizontalLayout.addWidget(self.y_maximum)
        self.cancel_button = QtGui.QToolButton(ExtentSelectorBase)
        self.cancel_button.setObjectName(_fromUtf8("cancel_button"))
        self.horizontalLayout.addWidget(self.cancel_button)
        self.ok_button = QtGui.QToolButton(ExtentSelectorBase)
        self.ok_button.setObjectName(_fromUtf8("ok_button"))
        self.horizontalLayout.addWidget(self.ok_button)

        self.retranslateUi(ExtentSelectorBase)
        QtCore.QMetaObject.connectSlotsByName(ExtentSelectorBase)

    def retranslateUi(self, ExtentSelectorBase):
        ExtentSelectorBase.setWindowTitle(_translate("ExtentSelectorBase", "InaSAFE Analysis Area", None))
        self.x_minimum.setPrefix(_translate("ExtentSelectorBase", "East: ", None))
        self.y_minimum.setPrefix(_translate("ExtentSelectorBase", "North: ", None))
        self.x_maximum.setPrefix(_translate("ExtentSelectorBase", "West: ", None))
        self.y_maximum.setPrefix(_translate("ExtentSelectorBase", "South: ", None))
        self.cancel_button.setText(_translate("ExtentSelectorBase", "Cancel", None))
        self.ok_button.setText(_translate("ExtentSelectorBase", "OK", None))

import resources_rc
