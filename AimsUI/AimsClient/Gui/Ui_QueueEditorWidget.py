# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AimsUI/AimsClient/Gui/Ui_QueueEditorWidget.ui'
#
# Created: Wed May  4 12:29:02 2016
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

class Ui_QueueEditorWidget(object):
    def setupUi(self, QueueEditorWidget):
        QueueEditorWidget.setObjectName(_fromUtf8("QueueEditorWidget"))
        QueueEditorWidget.resize(400, 1095)
        self.verticalLayout = QtGui.QVBoxLayout(QueueEditorWidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.scrollArea = QtGui.QScrollArea(QueueEditorWidget)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, -51, 364, 1161))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.splitter = QtGui.QSplitter(self.scrollAreaWidgetContents)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.gridLayoutWidget_7 = QtGui.QWidget(self.splitter)
        self.gridLayoutWidget_7.setObjectName(_fromUtf8("gridLayoutWidget_7"))
        self.gridLayout_14 = QtGui.QGridLayout(self.gridLayoutWidget_7)
        self.gridLayout_14.setMargin(0)
        self.gridLayout_14.setObjectName(_fromUtf8("gridLayout_14"))
        self.label_24 = QtGui.QLabel(self.gridLayoutWidget_7)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_24.sizePolicy().hasHeightForWidth())
        self.label_24.setSizePolicy(sizePolicy)
        self.label_24.setMinimumSize(QtCore.QSize(0, 0))
        self.label_24.setMaximumSize(QtCore.QSize(75, 16777215))
        self.label_24.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label_24.setWordWrap(True)
        self.label_24.setObjectName(_fromUtf8("label_24"))
        self.gridLayout_14.addWidget(self.label_24, 1, 0, 1, 1)
        self.label = QtGui.QLabel(self.gridLayoutWidget_7)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setMinimumSize(QtCore.QSize(0, 0))
        self.label.setMaximumSize(QtCore.QSize(75, 16777215))
        self.label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_14.addWidget(self.label, 0, 0, 1, 1)
        self.scrollArea_2 = QtGui.QScrollArea(self.gridLayoutWidget_7)
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollArea_2.setObjectName(_fromUtf8("scrollArea_2"))
        self.scrollAreaWidgetContents_2 = QtGui.QWidget()
        self.scrollAreaWidgetContents_2.setGeometry(QtCore.QRect(0, 0, 269, 76))
        self.scrollAreaWidgetContents_2.setObjectName(_fromUtf8("scrollAreaWidgetContents_2"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.scrollAreaWidgetContents_2)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.uWarning = QtGui.QLabel(self.scrollAreaWidgetContents_2)
        self.uWarning.setText(_fromUtf8(""))
        self.uWarning.setWordWrap(True)
        self.uWarning.setObjectName(_fromUtf8("uWarning"))
        self.verticalLayout_4.addWidget(self.uWarning)
        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_2)
        self.gridLayout_14.addWidget(self.scrollArea_2, 0, 1, 1, 1)
        self.scrollArea_4 = QtGui.QScrollArea(self.gridLayoutWidget_7)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollArea_4.sizePolicy().hasHeightForWidth())
        self.scrollArea_4.setSizePolicy(sizePolicy)
        self.scrollArea_4.setMaximumSize(QtCore.QSize(16777215, 40))
        self.scrollArea_4.setWidgetResizable(True)
        self.scrollArea_4.setObjectName(_fromUtf8("scrollArea_4"))
        self.scrollAreaWidgetContents_7 = QtGui.QWidget()
        self.scrollAreaWidgetContents_7.setGeometry(QtCore.QRect(0, 0, 269, 38))
        self.scrollAreaWidgetContents_7.setObjectName(_fromUtf8("scrollAreaWidgetContents_7"))
        self.verticalLayout_7 = QtGui.QVBoxLayout(self.scrollAreaWidgetContents_7)
        self.verticalLayout_7.setObjectName(_fromUtf8("verticalLayout_7"))
        self.uNotes = QtGui.QLabel(self.scrollAreaWidgetContents_7)
        self.uNotes.setText(_fromUtf8(""))
        self.uNotes.setWordWrap(True)
        self.uNotes.setObjectName(_fromUtf8("uNotes"))
        self.verticalLayout_7.addWidget(self.uNotes)
        self.scrollArea_4.setWidget(self.scrollAreaWidgetContents_7)
        self.gridLayout_14.addWidget(self.scrollArea_4, 1, 1, 1, 1)
        self.gridLayoutWidget_8 = QtGui.QWidget(self.splitter)
        self.gridLayoutWidget_8.setObjectName(_fromUtf8("gridLayoutWidget_8"))
        self.gridLayout_15 = QtGui.QGridLayout(self.gridLayoutWidget_8)
        self.gridLayout_15.setMargin(0)
        self.gridLayout_15.setObjectName(_fromUtf8("gridLayout_15"))
        self.uPrefix = QtGui.QLineEdit(self.gridLayoutWidget_8)
        self.uPrefix.setMinimumSize(QtCore.QSize(0, 0))
        self.uPrefix.setText(_fromUtf8(""))
        self.uPrefix.setObjectName(_fromUtf8("uPrefix"))
        self.gridLayout_15.addWidget(self.uPrefix, 6, 1, 1, 1)
        self.uAlpha = QtGui.QLineEdit(self.gridLayoutWidget_8)
        self.uAlpha.setMinimumSize(QtCore.QSize(0, 0))
        self.uAlpha.setText(_fromUtf8(""))
        self.uAlpha.setObjectName(_fromUtf8("uAlpha"))
        self.gridLayout_15.addWidget(self.uAlpha, 8, 1, 1, 1)
        self.uRoadPrefix = QtGui.QLineEdit(self.gridLayoutWidget_8)
        self.uRoadPrefix.setText(_fromUtf8(""))
        self.uRoadPrefix.setObjectName(_fromUtf8("uRoadPrefix"))
        self.gridLayout_15.addWidget(self.uRoadPrefix, 13, 1, 1, 1)
        self.uRoadSuffix = QtGui.QLineEdit(self.gridLayoutWidget_8)
        self.uRoadSuffix.setText(_fromUtf8(""))
        self.uRoadSuffix.setObjectName(_fromUtf8("uRoadSuffix"))
        self.gridLayout_15.addWidget(self.uRoadSuffix, 16, 1, 1, 1)
        self.uLevelValue = QtGui.QLineEdit(self.gridLayoutWidget_8)
        self.uLevelValue.setMinimumSize(QtCore.QSize(0, 0))
        self.uLevelValue.setText(_fromUtf8(""))
        self.uLevelValue.setObjectName(_fromUtf8("uLevelValue"))
        self.gridLayout_15.addWidget(self.uLevelValue, 3, 1, 1, 1)
        self.label_102 = QtGui.QLabel(self.gridLayoutWidget_8)
        self.label_102.setObjectName(_fromUtf8("label_102"))
        self.gridLayout_15.addWidget(self.label_102, 9, 0, 1, 1)
        self.label_114 = QtGui.QLabel(self.gridLayoutWidget_8)
        self.label_114.setObjectName(_fromUtf8("label_114"))
        self.gridLayout_15.addWidget(self.label_114, 3, 0, 1, 1)
        self.uBase = QtGui.QLineEdit(self.gridLayoutWidget_8)
        self.uBase.setMinimumSize(QtCore.QSize(0, 0))
        self.uBase.setText(_fromUtf8(""))
        self.uBase.setObjectName(_fromUtf8("uBase"))
        self.gridLayout_15.addWidget(self.uBase, 7, 1, 1, 1)
        self.uHigh = QtGui.QLineEdit(self.gridLayoutWidget_8)
        self.uHigh.setMinimumSize(QtCore.QSize(0, 0))
        self.uHigh.setText(_fromUtf8(""))
        self.uHigh.setObjectName(_fromUtf8("uHigh"))
        self.gridLayout_15.addWidget(self.uHigh, 9, 1, 1, 1)
        self.label_103 = QtGui.QLabel(self.gridLayoutWidget_8)
        self.label_103.setObjectName(_fromUtf8("label_103"))
        self.gridLayout_15.addWidget(self.label_103, 15, 0, 1, 1)
        self.uWaterName = QtGui.QLineEdit(self.gridLayoutWidget_8)
        self.uWaterName.setText(_fromUtf8(""))
        self.uWaterName.setObjectName(_fromUtf8("uWaterName"))
        self.gridLayout_15.addWidget(self.uWaterName, 17, 1, 1, 1)
        self.label_105 = QtGui.QLabel(self.gridLayoutWidget_8)
        self.label_105.setMaximumSize(QtCore.QSize(175, 16777215))
        self.label_105.setObjectName(_fromUtf8("label_105"))
        self.gridLayout_15.addWidget(self.label_105, 0, 0, 1, 1)
        self.label_116 = QtGui.QLabel(self.gridLayoutWidget_8)
        self.label_116.setObjectName(_fromUtf8("label_116"))
        self.gridLayout_15.addWidget(self.label_116, 7, 0, 1, 1)
        self.uLevelType = QtGui.QComboBox(self.gridLayoutWidget_8)
        self.uLevelType.setObjectName(_fromUtf8("uLevelType"))
        self.gridLayout_15.addWidget(self.uLevelType, 2, 1, 1, 1)
        self.label_107 = QtGui.QLabel(self.gridLayoutWidget_8)
        self.label_107.setMaximumSize(QtCore.QSize(175, 16777215))
        self.label_107.setObjectName(_fromUtf8("label_107"))
        self.gridLayout_15.addWidget(self.label_107, 5, 0, 1, 1)
        self.uUnit = QtGui.QLineEdit(self.gridLayoutWidget_8)
        self.uUnit.setMinimumSize(QtCore.QSize(0, 0))
        self.uUnit.setText(_fromUtf8(""))
        self.uUnit.setObjectName(_fromUtf8("uUnit"))
        self.gridLayout_15.addWidget(self.uUnit, 5, 1, 1, 1)
        self.uUnitType = QtGui.QComboBox(self.gridLayoutWidget_8)
        self.uUnitType.setObjectName(_fromUtf8("uUnitType"))
        self.gridLayout_15.addWidget(self.uUnitType, 4, 1, 1, 1)
        self.uRoadName = QtGui.QLineEdit(self.gridLayoutWidget_8)
        self.uRoadName.setText(_fromUtf8(""))
        self.uRoadName.setObjectName(_fromUtf8("uRoadName"))
        self.gridLayout_15.addWidget(self.uRoadName, 14, 1, 1, 1)
        self.label_108 = QtGui.QLabel(self.gridLayoutWidget_8)
        self.label_108.setMaximumSize(QtCore.QSize(175, 16777215))
        self.label_108.setObjectName(_fromUtf8("label_108"))
        self.gridLayout_15.addWidget(self.label_108, 13, 0, 1, 1)
        self.label_109 = QtGui.QLabel(self.gridLayoutWidget_8)
        self.label_109.setObjectName(_fromUtf8("label_109"))
        self.gridLayout_15.addWidget(self.label_109, 8, 0, 1, 1)
        self.label_110 = QtGui.QLabel(self.gridLayoutWidget_8)
        self.label_110.setObjectName(_fromUtf8("label_110"))
        self.gridLayout_15.addWidget(self.label_110, 16, 0, 1, 1)
        self.label_111 = QtGui.QLabel(self.gridLayoutWidget_8)
        self.label_111.setObjectName(_fromUtf8("label_111"))
        self.gridLayout_15.addWidget(self.label_111, 12, 0, 1, 1)
        self.label_112 = QtGui.QLabel(self.gridLayoutWidget_8)
        self.label_112.setObjectName(_fromUtf8("label_112"))
        self.gridLayout_15.addWidget(self.label_112, 6, 0, 1, 1)
        self.label_113 = QtGui.QLabel(self.gridLayoutWidget_8)
        self.label_113.setObjectName(_fromUtf8("label_113"))
        self.gridLayout_15.addWidget(self.label_113, 2, 0, 1, 1)
        self.label_115 = QtGui.QLabel(self.gridLayoutWidget_8)
        self.label_115.setMaximumSize(QtCore.QSize(175, 16777215))
        self.label_115.setObjectName(_fromUtf8("label_115"))
        self.gridLayout_15.addWidget(self.label_115, 14, 0, 1, 1)
        self.label_117 = QtGui.QLabel(self.gridLayoutWidget_8)
        self.label_117.setMaximumSize(QtCore.QSize(175, 16777215))
        self.label_117.setObjectName(_fromUtf8("label_117"))
        self.gridLayout_15.addWidget(self.label_117, 4, 0, 1, 1)
        self.label_118 = QtGui.QLabel(self.gridLayoutWidget_8)
        self.label_118.setObjectName(_fromUtf8("label_118"))
        self.gridLayout_15.addWidget(self.label_118, 17, 0, 1, 1)
        self.label_119 = QtGui.QLabel(self.gridLayoutWidget_8)
        self.label_119.setObjectName(_fromUtf8("label_119"))
        self.gridLayout_15.addWidget(self.label_119, 18, 0, 1, 1)
        self.label_120 = QtGui.QLabel(self.gridLayoutWidget_8)
        self.label_120.setText(_fromUtf8(""))
        self.label_120.setObjectName(_fromUtf8("label_120"))
        self.gridLayout_15.addWidget(self.label_120, 19, 0, 1, 1)
        self.uAddressType = QtGui.QComboBox(self.gridLayoutWidget_8)
        self.uAddressType.setObjectName(_fromUtf8("uAddressType"))
        self.gridLayout_15.addWidget(self.uAddressType, 0, 1, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.uRclId = QtGui.QLineEdit(self.gridLayoutWidget_8)
        self.uRclId.setObjectName(_fromUtf8("uRclId"))
        self.horizontalLayout.addWidget(self.uRclId)
        self.uGetRclToolButton = QtGui.QToolButton(self.gridLayoutWidget_8)
        self.uGetRclToolButton.setMinimumSize(QtCore.QSize(24, 0))
        self.uGetRclToolButton.setMaximumSize(QtCore.QSize(24, 16777215))
        self.uGetRclToolButton.setObjectName(_fromUtf8("uGetRclToolButton"))
        self.horizontalLayout.addWidget(self.uGetRclToolButton)
        self.gridLayout_15.addLayout(self.horizontalLayout, 12, 1, 1, 1)
        self.uExternalAddId = QtGui.QLineEdit(self.gridLayoutWidget_8)
        self.uExternalAddId.setObjectName(_fromUtf8("uExternalAddId"))
        self.gridLayout_15.addWidget(self.uExternalAddId, 11, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.gridLayoutWidget_8)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_15.addWidget(self.label_2, 10, 0, 1, 1)
        self.uExternalIdScheme = QtGui.QLineEdit(self.gridLayoutWidget_8)
        self.uExternalIdScheme.setText(_fromUtf8(""))
        self.uExternalIdScheme.setObjectName(_fromUtf8("uExternalIdScheme"))
        self.gridLayout_15.addWidget(self.uExternalIdScheme, 10, 1, 1, 1)
        self.label_3 = QtGui.QLabel(self.gridLayoutWidget_8)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_15.addWidget(self.label_3, 11, 0, 1, 1)
        self.uRoadTypeName = QtGui.QLineEdit(self.gridLayoutWidget_8)
        self.uRoadTypeName.setText(_fromUtf8(""))
        self.uRoadTypeName.setObjectName(_fromUtf8("uRoadTypeName"))
        self.gridLayout_15.addWidget(self.uRoadTypeName, 15, 1, 1, 1)
        self.uWaterRouteName = QtGui.QLineEdit(self.gridLayoutWidget_8)
        self.uWaterRouteName.setText(_fromUtf8(""))
        self.uWaterRouteName.setObjectName(_fromUtf8("uWaterRouteName"))
        self.gridLayout_15.addWidget(self.uWaterRouteName, 18, 1, 1, 1)
        self.ulifeCycle = QtGui.QComboBox(self.gridLayoutWidget_8)
        self.ulifeCycle.setObjectName(_fromUtf8("ulifeCycle"))
        self.gridLayout_15.addWidget(self.ulifeCycle, 1, 1, 1, 1)
        self.label_4 = QtGui.QLabel(self.gridLayoutWidget_8)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout_15.addWidget(self.label_4, 1, 0, 1, 1)
        self.verticalLayout_2.addWidget(self.splitter)
        self.label_121 = QtGui.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_121.setFont(font)
        self.label_121.setObjectName(_fromUtf8("label_121"))
        self.verticalLayout_2.addWidget(self.label_121)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.gridLayout_13 = QtGui.QGridLayout()
        self.gridLayout_13.setObjectName(_fromUtf8("gridLayout_13"))
        self.uExtObjectIdScheme = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        self.uExtObjectIdScheme.setObjectName(_fromUtf8("uExtObjectIdScheme"))
        self.gridLayout_13.addWidget(self.uExtObjectIdScheme, 4, 1, 1, 1)
        self.label_94 = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.label_94.setObjectName(_fromUtf8("label_94"))
        self.gridLayout_13.addWidget(self.label_94, 5, 0, 1, 1)
        self.label_92 = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.label_92.setMinimumSize(QtCore.QSize(130, 0))
        self.label_92.setObjectName(_fromUtf8("label_92"))
        self.gridLayout_13.addWidget(self.label_92, 1, 0, 1, 1)
        self.label_93 = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.label_93.setObjectName(_fromUtf8("label_93"))
        self.gridLayout_13.addWidget(self.label_93, 8, 0, 1, 1)
        self.uCertificateOfTitle = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        self.uCertificateOfTitle.setText(_fromUtf8(""))
        self.uCertificateOfTitle.setObjectName(_fromUtf8("uCertificateOfTitle"))
        self.gridLayout_13.addWidget(self.uCertificateOfTitle, 7, 1, 1, 1)
        self.uAppellation = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        self.uAppellation.setText(_fromUtf8(""))
        self.uAppellation.setObjectName(_fromUtf8("uAppellation"))
        self.gridLayout_13.addWidget(self.uAppellation, 8, 1, 1, 1)
        self.uExternalObjectId = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        self.uExternalObjectId.setText(_fromUtf8(""))
        self.uExternalObjectId.setObjectName(_fromUtf8("uExternalObjectId"))
        self.gridLayout_13.addWidget(self.uExternalObjectId, 5, 1, 1, 1)
        self.uValuationReference = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        self.uValuationReference.setText(_fromUtf8(""))
        self.uValuationReference.setObjectName(_fromUtf8("uValuationReference"))
        self.gridLayout_13.addWidget(self.uValuationReference, 6, 1, 1, 1)
        self.label_95 = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.label_95.setObjectName(_fromUtf8("label_95"))
        self.gridLayout_13.addWidget(self.label_95, 7, 0, 1, 1)
        self.uObjectName = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        self.uObjectName.setText(_fromUtf8(""))
        self.uObjectName.setObjectName(_fromUtf8("uObjectName"))
        self.gridLayout_13.addWidget(self.uObjectName, 2, 1, 1, 1)
        self.label_96 = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.label_96.setObjectName(_fromUtf8("label_96"))
        self.gridLayout_13.addWidget(self.label_96, 2, 0, 1, 1)
        self.label_97 = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.label_97.setObjectName(_fromUtf8("label_97"))
        self.gridLayout_13.addWidget(self.label_97, 4, 0, 1, 1)
        self.label_98 = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.label_98.setObjectName(_fromUtf8("label_98"))
        self.gridLayout_13.addWidget(self.label_98, 6, 0, 1, 1)
        self.uObjectType = QtGui.QComboBox(self.scrollAreaWidgetContents)
        self.uObjectType.setObjectName(_fromUtf8("uObjectType"))
        self.gridLayout_13.addWidget(self.uObjectType, 1, 1, 1, 1)
        self.label_99 = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.label_99.setObjectName(_fromUtf8("label_99"))
        self.gridLayout_13.addWidget(self.label_99, 3, 0, 1, 1)
        self.uPositionType = QtGui.QComboBox(self.scrollAreaWidgetContents)
        self.uPositionType.setObjectName(_fromUtf8("uPositionType"))
        self.gridLayout_13.addWidget(self.uPositionType, 3, 1, 1, 1)
        self.label_5 = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout_13.addWidget(self.label_5, 9, 0, 1, 1)
        self.uMblkOverride = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        self.uMblkOverride.setObjectName(_fromUtf8("uMblkOverride"))
        self.gridLayout_13.addWidget(self.uMblkOverride, 9, 1, 1, 1)
        self.label_6 = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout_13.addWidget(self.label_6, 0, 0, 1, 1)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.uUpdatePosButton = QtGui.QPushButton(self.scrollAreaWidgetContents)
        self.uUpdatePosButton.setMinimumSize(QtCore.QSize(24, 0))
        self.uUpdatePosButton.setMaximumSize(QtCore.QSize(24, 16777215))
        self.uUpdatePosButton.setObjectName(_fromUtf8("uUpdatePosButton"))
        self.horizontalLayout_3.addWidget(self.uUpdatePosButton)
        self.gridLayout_13.addLayout(self.horizontalLayout_3, 0, 1, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout_13)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)

        self.retranslateUi(QueueEditorWidget)
        QtCore.QMetaObject.connectSlotsByName(QueueEditorWidget)

    def retranslateUi(self, QueueEditorWidget):
        QueueEditorWidget.setWindowTitle(_translate("QueueEditorWidget", "Form", None))
        self.label_24.setText(_translate("QueueEditorWidget", "Source Notes:", None))
        self.label.setText(_translate("QueueEditorWidget", "Warnings:", None))
        self.label_102.setText(_translate("QueueEditorWidget", "Number High:", None))
        self.label_114.setText(_translate("QueueEditorWidget", "Level Value:", None))
        self.label_103.setText(_translate("QueueEditorWidget", "Road Type:", None))
        self.label_105.setText(_translate("QueueEditorWidget", "Address Type:", None))
        self.label_116.setText(_translate("QueueEditorWidget", "Base Number:", None))
        self.label_107.setText(_translate("QueueEditorWidget", "Unit Value:", None))
        self.label_108.setText(_translate("QueueEditorWidget", "Road Prefix:", None))
        self.label_109.setText(_translate("QueueEditorWidget", "Number Suffix:", None))
        self.label_110.setText(_translate("QueueEditorWidget", "Road Suffix:", None))
        self.label_111.setText(_translate("QueueEditorWidget", "RCL Id:", None))
        self.label_112.setText(_translate("QueueEditorWidget", "Number Prefix:", None))
        self.label_113.setText(_translate("QueueEditorWidget", "Level Type:", None))
        self.label_115.setText(_translate("QueueEditorWidget", "Road Name:", None))
        self.label_117.setText(_translate("QueueEditorWidget", "Unit Type:", None))
        self.label_118.setText(_translate("QueueEditorWidget", "Water Route:", None))
        self.label_119.setText(_translate("QueueEditorWidget", "Water Name:", None))
        self.uGetRclToolButton.setText(_translate("QueueEditorWidget", ">", None))
        self.label_2.setText(_translate("QueueEditorWidget", "Ext. Add  Id Scheme:", None))
        self.label_3.setText(_translate("QueueEditorWidget", "Ext. Add  Id:", None))
        self.label_4.setText(_translate("QueueEditorWidget", "Lifecycle:", None))
        self.label_121.setText(_translate("QueueEditorWidget", "Addressable Object:", None))
        self.label_94.setText(_translate("QueueEditorWidget", "Ext. Obj Id:", None))
        self.label_92.setText(_translate("QueueEditorWidget", "Object Type:", None))
        self.label_93.setText(_translate("QueueEditorWidget", "Appellation:", None))
        self.label_95.setText(_translate("QueueEditorWidget", "Cert. of Title:", None))
        self.label_96.setText(_translate("QueueEditorWidget", "Object Name:", None))
        self.label_97.setText(_translate("QueueEditorWidget", "Ext. Obj Id Scheme:", None))
        self.label_98.setText(_translate("QueueEditorWidget", "Val Ref:", None))
        self.label_99.setText(_translate("QueueEditorWidget", "Position Type:", None))
        self.label_5.setText(_translate("QueueEditorWidget", "Mblk Override:", None))
        self.label_6.setText(_translate("QueueEditorWidget", "Update Position:", None))
        self.uUpdatePosButton.setText(_translate("QueueEditorWidget", "+", None))

