# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'import_dialog_base.ui'
#
# Created: Wed Feb 13 15:22:21 2013
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ImportDialogBase(object):
    def setupUi(self, ImportDialogBase):
        ImportDialogBase.setObjectName(_fromUtf8("ImportDialogBase"))
        ImportDialogBase.resize(629, 473)
        self.buttonBox = QtGui.QDialogButtonBox(ImportDialogBase)
        self.buttonBox.setGeometry(QtCore.QRect(250, 410, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.groupBox = QtGui.QGroupBox(ImportDialogBase)
        self.groupBox.setGeometry(QtCore.QRect(320, 20, 281, 181))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.formLayout_2 = QtGui.QFormLayout(self.groupBox)
        self.formLayout_2.setFieldGrowthPolicy(QtGui.QFormLayout.FieldsStayAtSizeHint)
        self.formLayout_2.setObjectName(_fromUtf8("formLayout_2"))
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.minLongitude = QtGui.QLineEdit(self.groupBox)
        self.minLongitude.setObjectName(_fromUtf8("minLongitude"))
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.FieldRole, self.minLongitude)
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.minLatitude = QtGui.QLineEdit(self.groupBox)
        self.minLatitude.setObjectName(_fromUtf8("minLatitude"))
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.FieldRole, self.minLatitude)
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.formLayout_2.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_3)
        self.maxLongitude = QtGui.QLineEdit(self.groupBox)
        self.maxLongitude.setObjectName(_fromUtf8("maxLongitude"))
        self.formLayout_2.setWidget(2, QtGui.QFormLayout.FieldRole, self.maxLongitude)
        self.label_4 = QtGui.QLabel(self.groupBox)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.formLayout_2.setWidget(3, QtGui.QFormLayout.LabelRole, self.label_4)
        self.maxLatitude = QtGui.QLineEdit(self.groupBox)
        self.maxLatitude.setObjectName(_fromUtf8("maxLatitude"))
        self.formLayout_2.setWidget(3, QtGui.QFormLayout.FieldRole, self.maxLatitude)
        self.groupBox_2 = QtGui.QGroupBox(ImportDialogBase)
        self.groupBox_2.setGeometry(QtCore.QRect(20, 243, 581, 151))
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.formLayout = QtGui.QFormLayout(self.groupBox_2)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.regionLabel = QtGui.QLabel(self.groupBox_2)
        self.regionLabel.setObjectName(_fromUtf8("regionLabel"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.regionLabel)
        self.cbxRegion = QtGui.QComboBox(self.groupBox_2)
        self.cbxRegion.setObjectName(_fromUtf8("cbxRegion"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.cbxRegion)
        self.presetLabel = QtGui.QLabel(self.groupBox_2)
        self.presetLabel.setObjectName(_fromUtf8("presetLabel"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.presetLabel)
        self.cbxPreset = QtGui.QComboBox(self.groupBox_2)
        self.cbxPreset.setObjectName(_fromUtf8("cbxPreset"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.cbxPreset)
        self.outputDirectoryLabel = QtGui.QLabel(self.groupBox_2)
        self.outputDirectoryLabel.setObjectName(_fromUtf8("outputDirectoryLabel"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.outputDirectoryLabel)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.outDir = QtGui.QLineEdit(self.groupBox_2)
        self.outDir.setText(_fromUtf8(""))
        self.outDir.setObjectName(_fromUtf8("outDir"))
        self.horizontalLayout.addWidget(self.outDir)
        self.pBtnDir = QtGui.QToolButton(self.groupBox_2)
        self.pBtnDir.setObjectName(_fromUtf8("pBtnDir"))
        self.horizontalLayout.addWidget(self.pBtnDir)
        self.formLayout.setLayout(2, QtGui.QFormLayout.FieldRole, self.horizontalLayout)

        self.retranslateUi(ImportDialogBase)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ImportDialogBase.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ImportDialogBase.reject)
        QtCore.QMetaObject.connectSlotsByName(ImportDialogBase)

    def retranslateUi(self, ImportDialogBase):
        ImportDialogBase.setWindowTitle(QtGui.QApplication.translate("ImportDialogBase", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("ImportDialogBase", "Coordinate", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ImportDialogBase", "Min. Longitude", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("ImportDialogBase", "Min. Latitude", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("ImportDialogBase", "Max. Longitude", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("ImportDialogBase", "Max. Latitude", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("ImportDialogBase", "Options", None, QtGui.QApplication.UnicodeUTF8))
        self.regionLabel.setText(QtGui.QApplication.translate("ImportDialogBase", "Region", None, QtGui.QApplication.UnicodeUTF8))
        self.presetLabel.setText(QtGui.QApplication.translate("ImportDialogBase", "Preset", None, QtGui.QApplication.UnicodeUTF8))
        self.outputDirectoryLabel.setText(QtGui.QApplication.translate("ImportDialogBase", "Output Directory", None, QtGui.QApplication.UnicodeUTF8))
        self.pBtnDir.setText(QtGui.QApplication.translate("ImportDialogBase", "...", None, QtGui.QApplication.UnicodeUTF8))

