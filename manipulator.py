# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'manipulator.ui'
#
# Created: Thu Jul  9 12:58:41 2015
#      by: PyQt4 UI code generator 4.11.3
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

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.setEnabled(True)
        MainWindow.resize(546, 960)
        MainWindow.setMinimumSize(QtCore.QSize(500, 700))
        MainWindow.setMaximumSize(QtCore.QSize(16777215, 16777215))
        MainWindow.setStyleSheet(_fromUtf8("background-color: rgb(226, 226, 226);"))
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout_3 = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout_3.setSpacing(9)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.gridFrame = QtGui.QFrame(self.centralwidget)
        self.gridFrame.setMinimumSize(QtCore.QSize(0, 0))
        self.gridFrame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.gridFrame.setFrameShadow(QtGui.QFrame.Plain)
        self.gridFrame.setObjectName(_fromUtf8("gridFrame"))
        self.gridLayout = QtGui.QGridLayout(self.gridFrame)
        self.gridLayout.setMargin(6)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_2 = QtGui.QLabel(self.gridFrame)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setStyleSheet(_fromUtf8("background-color: rgb(0, 196, 255);"))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 2)
        self.SM5_1PowerBtn = QtGui.QPushButton(self.gridFrame)
        self.SM5_1PowerBtn.setMaximumSize(QtCore.QSize(16777215, 24))
        self.SM5_1PowerBtn.setObjectName(_fromUtf8("SM5_1PowerBtn"))
        self.gridLayout.addWidget(self.SM5_1PowerBtn, 6, 1, 1, 1)
        self.connectBtn = QtGui.QPushButton(self.gridFrame)
        self.connectBtn.setMaximumSize(QtCore.QSize(16777215, 24))
        self.connectBtn.setCheckable(True)
        self.connectBtn.setDefault(False)
        self.connectBtn.setFlat(False)
        self.connectBtn.setObjectName(_fromUtf8("connectBtn"))
        self.gridLayout.addWidget(self.connectBtn, 3, 0, 1, 2)
        self.SM5_2PowerBtn = QtGui.QPushButton(self.gridFrame)
        self.SM5_2PowerBtn.setMaximumSize(QtCore.QSize(16777215, 24))
        self.SM5_2PowerBtn.setObjectName(_fromUtf8("SM5_2PowerBtn"))
        self.gridLayout.addWidget(self.SM5_2PowerBtn, 7, 1, 1, 1)
        self.label_3 = QtGui.QLabel(self.gridFrame)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 2, 1, 1, 1)
        self.label_4 = QtGui.QLabel(self.gridFrame)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 2, 0, 1, 1)
        self.label_7 = QtGui.QLabel(self.gridFrame)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout.addWidget(self.label_7, 8, 0, 1, 1)
        self.C843XYPowerBtn = QtGui.QPushButton(self.gridFrame)
        self.C843XYPowerBtn.setMaximumSize(QtCore.QSize(16777215, 24))
        self.C843XYPowerBtn.setCheckable(True)
        self.C843XYPowerBtn.setChecked(False)
        self.C843XYPowerBtn.setObjectName(_fromUtf8("C843XYPowerBtn"))
        self.gridLayout.addWidget(self.C843XYPowerBtn, 6, 0, 1, 1)
        self.horizontalWidget = QtGui.QWidget(self.gridFrame)
        self.horizontalWidget.setMinimumSize(QtCore.QSize(0, 0))
        self.horizontalWidget.setObjectName(_fromUtf8("horizontalWidget"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.horizontalWidget)
        self.horizontalLayout_2.setMargin(1)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.refLocationBtn = QtGui.QPushButton(self.horizontalWidget)
        self.refLocationBtn.setMaximumSize(QtCore.QSize(16777215, 24))
        self.refLocationBtn.setObjectName(_fromUtf8("refLocationBtn"))
        self.horizontalLayout_2.addWidget(self.refLocationBtn)
        self.refPositiveBtn = QtGui.QPushButton(self.horizontalWidget)
        self.refPositiveBtn.setMaximumSize(QtCore.QSize(16777215, 24))
        self.refPositiveBtn.setObjectName(_fromUtf8("refPositiveBtn"))
        self.horizontalLayout_2.addWidget(self.refPositiveBtn)
        self.refNegativeBtn = QtGui.QPushButton(self.horizontalWidget)
        self.refNegativeBtn.setMaximumSize(QtCore.QSize(16777215, 24))
        self.refNegativeBtn.setObjectName(_fromUtf8("refNegativeBtn"))
        self.horizontalLayout_2.addWidget(self.refNegativeBtn)
        self.gridLayout.addWidget(self.horizontalWidget, 9, 0, 1, 2)
        self.C843ZPowerBtn = QtGui.QPushButton(self.gridFrame)
        self.C843ZPowerBtn.setMaximumSize(QtCore.QSize(16777215, 24))
        self.C843ZPowerBtn.setObjectName(_fromUtf8("C843ZPowerBtn"))
        self.gridLayout.addWidget(self.C843ZPowerBtn, 7, 0, 1, 1)
        self.gridLayout_3.addWidget(self.gridFrame, 0, 0, 1, 2)
        self.gridFrame1 = QtGui.QFrame(self.centralwidget)
        self.gridFrame1.setMinimumSize(QtCore.QSize(0, 10))
        self.gridFrame1.setFrameShape(QtGui.QFrame.StyledPanel)
        self.gridFrame1.setFrameShadow(QtGui.QFrame.Plain)
        self.gridFrame1.setLineWidth(2)
        self.gridFrame1.setObjectName(_fromUtf8("gridFrame1"))
        self.gridLayout_8 = QtGui.QGridLayout(self.gridFrame1)
        self.gridLayout_8.setContentsMargins(9, 6, 6, 6)
        self.gridLayout_8.setObjectName(_fromUtf8("gridLayout_8"))
        self.label_13 = QtGui.QLabel(self.gridFrame1)
        self.label_13.setObjectName(_fromUtf8("label_13"))
        self.gridLayout_8.addWidget(self.label_13, 4, 0, 1, 1)
        self.horizontalWidget1 = QtGui.QWidget(self.gridFrame1)
        self.horizontalWidget1.setObjectName(_fromUtf8("horizontalWidget1"))
        self.horizontalLayout_7 = QtGui.QHBoxLayout(self.horizontalWidget1)
        self.horizontalLayout_7.setMargin(4)
        self.horizontalLayout_7.setObjectName(_fromUtf8("horizontalLayout_7"))
        self.minMaxXLocationValueLabel = QtGui.QLabel(self.horizontalWidget1)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.minMaxXLocationValueLabel.setFont(font)
        self.minMaxXLocationValueLabel.setObjectName(_fromUtf8("minMaxXLocationValueLabel"))
        self.horizontalLayout_7.addWidget(self.minMaxXLocationValueLabel)
        self.minMaxYLocationValueLabel = QtGui.QLabel(self.horizontalWidget1)
        self.minMaxYLocationValueLabel.setObjectName(_fromUtf8("minMaxYLocationValueLabel"))
        self.horizontalLayout_7.addWidget(self.minMaxYLocationValueLabel)
        self.minMaxZLocationValueLabel = QtGui.QLabel(self.horizontalWidget1)
        self.minMaxZLocationValueLabel.setObjectName(_fromUtf8("minMaxZLocationValueLabel"))
        self.horizontalLayout_7.addWidget(self.minMaxZLocationValueLabel)
        self.gridLayout_8.addWidget(self.horizontalWidget1, 2, 1, 1, 1)
        self.label_8 = QtGui.QLabel(self.gridFrame1)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_8.setFont(font)
        self.label_8.setStyleSheet(_fromUtf8("background-color: rgb(0, 196, 255);"))
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.gridLayout_8.addWidget(self.label_8, 0, 0, 1, 2)
        self.horizontalWidget2 = QtGui.QWidget(self.gridFrame1)
        self.horizontalWidget2.setObjectName(_fromUtf8("horizontalWidget2"))
        self.horizontalLayout_9 = QtGui.QHBoxLayout(self.horizontalWidget2)
        self.horizontalLayout_9.setMargin(4)
        self.horizontalLayout_9.setObjectName(_fromUtf8("horizontalLayout_9"))
        self.isXLocationValueLabel = QtGui.QLabel(self.horizontalWidget2)
        self.isXLocationValueLabel.setObjectName(_fromUtf8("isXLocationValueLabel"))
        self.horizontalLayout_9.addWidget(self.isXLocationValueLabel)
        self.isYLocationValueLabel = QtGui.QLabel(self.horizontalWidget2)
        self.isYLocationValueLabel.setObjectName(_fromUtf8("isYLocationValueLabel"))
        self.horizontalLayout_9.addWidget(self.isYLocationValueLabel)
        self.isZLocationValueLabel = QtGui.QLabel(self.horizontalWidget2)
        self.isZLocationValueLabel.setObjectName(_fromUtf8("isZLocationValueLabel"))
        self.horizontalLayout_9.addWidget(self.isZLocationValueLabel)
        self.gridLayout_8.addWidget(self.horizontalWidget2, 3, 1, 1, 1)
        self.horizontalWidget3 = QtGui.QWidget(self.gridFrame1)
        self.horizontalWidget3.setObjectName(_fromUtf8("horizontalWidget3"))
        self.horizontalLayout_8 = QtGui.QHBoxLayout(self.horizontalWidget3)
        self.horizontalLayout_8.setMargin(1)
        self.horizontalLayout_8.setObjectName(_fromUtf8("horizontalLayout_8"))
        self.setXLocationLineEdit = QtGui.QLineEdit(self.horizontalWidget3)
        self.setXLocationLineEdit.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 255);"))
        self.setXLocationLineEdit.setText(_fromUtf8(""))
        self.setXLocationLineEdit.setObjectName(_fromUtf8("setXLocationLineEdit"))
        self.horizontalLayout_8.addWidget(self.setXLocationLineEdit)
        self.setYLocationLineEdit = QtGui.QLineEdit(self.horizontalWidget3)
        self.setYLocationLineEdit.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 255);"))
        self.setYLocationLineEdit.setText(_fromUtf8(""))
        self.setYLocationLineEdit.setObjectName(_fromUtf8("setYLocationLineEdit"))
        self.horizontalLayout_8.addWidget(self.setYLocationLineEdit)
        self.setZLocationLineEdit = QtGui.QLineEdit(self.horizontalWidget3)
        self.setZLocationLineEdit.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 255);"))
        self.setZLocationLineEdit.setText(_fromUtf8(""))
        self.setZLocationLineEdit.setObjectName(_fromUtf8("setZLocationLineEdit"))
        self.horizontalLayout_8.addWidget(self.setZLocationLineEdit)
        self.gridLayout_8.addWidget(self.horizontalWidget3, 4, 1, 1, 1)
        self.horizontalWidget4 = QtGui.QWidget(self.gridFrame1)
        self.horizontalWidget4.setMinimumSize(QtCore.QSize(0, 0))
        self.horizontalWidget4.setObjectName(_fromUtf8("horizontalWidget4"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout(self.horizontalWidget4)
        self.horizontalLayout_4.setMargin(4)
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.label_22 = QtGui.QLabel(self.horizontalWidget4)
        self.label_22.setObjectName(_fromUtf8("label_22"))
        self.horizontalLayout_4.addWidget(self.label_22)
        self.label_21 = QtGui.QLabel(self.horizontalWidget4)
        self.label_21.setObjectName(_fromUtf8("label_21"))
        self.horizontalLayout_4.addWidget(self.label_21)
        self.label_20 = QtGui.QLabel(self.horizontalWidget4)
        self.label_20.setObjectName(_fromUtf8("label_20"))
        self.horizontalLayout_4.addWidget(self.label_20)
        self.gridLayout_8.addWidget(self.horizontalWidget4, 7, 1, 1, 1)
        self.horizontalWidget5 = QtGui.QWidget(self.gridFrame1)
        self.horizontalWidget5.setMinimumSize(QtCore.QSize(0, 0))
        self.horizontalWidget5.setObjectName(_fromUtf8("horizontalWidget5"))
        self.horizontalLayout_13 = QtGui.QHBoxLayout(self.horizontalWidget5)
        self.horizontalLayout_13.setMargin(1)
        self.horizontalLayout_13.setObjectName(_fromUtf8("horizontalLayout_13"))
        self.label_24 = QtGui.QLabel(self.horizontalWidget5)
        self.label_24.setObjectName(_fromUtf8("label_24"))
        self.horizontalLayout_13.addWidget(self.label_24)
        self.lineEdit_9 = QtGui.QLineEdit(self.horizontalWidget5)
        self.lineEdit_9.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 255);"))
        self.lineEdit_9.setObjectName(_fromUtf8("lineEdit_9"))
        self.horizontalLayout_13.addWidget(self.lineEdit_9)
        self.label_6 = QtGui.QLabel(self.horizontalWidget5)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.horizontalLayout_13.addWidget(self.label_6)
        self.lineEdit_10 = QtGui.QLineEdit(self.horizontalWidget5)
        self.lineEdit_10.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 255);"))
        self.lineEdit_10.setObjectName(_fromUtf8("lineEdit_10"))
        self.horizontalLayout_13.addWidget(self.lineEdit_10)
        self.gridLayout_8.addWidget(self.horizontalWidget5, 12, 0, 1, 2)
        self.label_23 = QtGui.QLabel(self.gridFrame1)
        self.label_23.setObjectName(_fromUtf8("label_23"))
        self.gridLayout_8.addWidget(self.label_23, 9, 0, 1, 1)
        self.horizontalWidget6 = QtGui.QWidget(self.gridFrame1)
        self.horizontalWidget6.setMinimumSize(QtCore.QSize(0, 0))
        self.horizontalWidget6.setObjectName(_fromUtf8("horizontalWidget6"))
        self.horizontalLayout_12 = QtGui.QHBoxLayout(self.horizontalWidget6)
        self.horizontalLayout_12.setMargin(1)
        self.horizontalLayout_12.setObjectName(_fromUtf8("horizontalLayout_12"))
        self.lineEdit_8 = QtGui.QLineEdit(self.horizontalWidget6)
        self.lineEdit_8.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 255);"))
        self.lineEdit_8.setObjectName(_fromUtf8("lineEdit_8"))
        self.horizontalLayout_12.addWidget(self.lineEdit_8)
        self.lineEdit_7 = QtGui.QLineEdit(self.horizontalWidget6)
        self.lineEdit_7.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 255);"))
        self.lineEdit_7.setObjectName(_fromUtf8("lineEdit_7"))
        self.horizontalLayout_12.addWidget(self.lineEdit_7)
        self.lineEdit_6 = QtGui.QLineEdit(self.horizontalWidget6)
        self.lineEdit_6.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 255);"))
        self.lineEdit_6.setObjectName(_fromUtf8("lineEdit_6"))
        self.horizontalLayout_12.addWidget(self.lineEdit_6)
        self.gridLayout_8.addWidget(self.horizontalWidget6, 9, 1, 1, 1)
        self.label_9 = QtGui.QLabel(self.gridFrame1)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.gridLayout_8.addWidget(self.label_9, 2, 0, 1, 1)
        self.pushButton_9 = QtGui.QPushButton(self.gridFrame1)
        self.pushButton_9.setMaximumSize(QtCore.QSize(16777215, 24))
        self.pushButton_9.setStyleSheet(_fromUtf8(""))
        self.pushButton_9.setCheckable(True)
        self.pushButton_9.setChecked(False)
        self.pushButton_9.setObjectName(_fromUtf8("pushButton_9"))
        self.gridLayout_8.addWidget(self.pushButton_9, 1, 0, 1, 2)
        self.horizontalWidget7 = QtGui.QWidget(self.gridFrame1)
        self.horizontalWidget7.setObjectName(_fromUtf8("horizontalWidget7"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.horizontalWidget7)
        self.horizontalLayout.setMargin(1)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.fineBtn = QtGui.QPushButton(self.horizontalWidget7)
        self.fineBtn.setMaximumSize(QtCore.QSize(16777215, 24))
        self.fineBtn.setIconSize(QtCore.QSize(16, 16))
        self.fineBtn.setCheckable(True)
        self.fineBtn.setObjectName(_fromUtf8("fineBtn"))
        self.buttonGroup = QtGui.QButtonGroup(MainWindow)
        self.buttonGroup.setObjectName(_fromUtf8("buttonGroup"))
        self.buttonGroup.addButton(self.fineBtn)
        self.horizontalLayout.addWidget(self.fineBtn)
        self.smallBtn = QtGui.QPushButton(self.horizontalWidget7)
        self.smallBtn.setMaximumSize(QtCore.QSize(16777215, 24))
        self.smallBtn.setCheckable(True)
        self.smallBtn.setObjectName(_fromUtf8("smallBtn"))
        self.buttonGroup.addButton(self.smallBtn)
        self.horizontalLayout.addWidget(self.smallBtn)
        self.MediumBtn = QtGui.QPushButton(self.horizontalWidget7)
        self.MediumBtn.setMaximumSize(QtCore.QSize(16777215, 24))
        self.MediumBtn.setCheckable(True)
        self.MediumBtn.setObjectName(_fromUtf8("MediumBtn"))
        self.buttonGroup.addButton(self.MediumBtn)
        self.horizontalLayout.addWidget(self.MediumBtn)
        self.coarseBtn = QtGui.QPushButton(self.horizontalWidget7)
        self.coarseBtn.setMaximumSize(QtCore.QSize(16777215, 24))
        self.coarseBtn.setCheckable(True)
        self.coarseBtn.setObjectName(_fromUtf8("coarseBtn"))
        self.buttonGroup.addButton(self.coarseBtn)
        self.horizontalLayout.addWidget(self.coarseBtn)
        self.gridLayout_8.addWidget(self.horizontalWidget7, 5, 0, 1, 2)
        self.label_17 = QtGui.QLabel(self.gridFrame1)
        self.label_17.setObjectName(_fromUtf8("label_17"))
        self.gridLayout_8.addWidget(self.label_17, 3, 0, 1, 1)
        self.horizontalWidget8 = QtGui.QWidget(self.gridFrame1)
        self.horizontalWidget8.setMinimumSize(QtCore.QSize(0, 0))
        self.horizontalWidget8.setObjectName(_fromUtf8("horizontalWidget8"))
        self.horizontalLayout_11 = QtGui.QHBoxLayout(self.horizontalWidget8)
        self.horizontalLayout_11.setMargin(2)
        self.horizontalLayout_11.setObjectName(_fromUtf8("horizontalLayout_11"))
        self.label_18 = QtGui.QLabel(self.horizontalWidget8)
        self.label_18.setObjectName(_fromUtf8("label_18"))
        self.horizontalLayout_11.addWidget(self.label_18)
        self.stepLineEdit = QtGui.QLineEdit(self.horizontalWidget8)
        self.stepLineEdit.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 255);"))
        self.stepLineEdit.setObjectName(_fromUtf8("stepLineEdit"))
        self.horizontalLayout_11.addWidget(self.stepLineEdit)
        self.label_19 = QtGui.QLabel(self.horizontalWidget8)
        self.label_19.setObjectName(_fromUtf8("label_19"))
        self.horizontalLayout_11.addWidget(self.label_19)
        self.speedLineEdit = QtGui.QLineEdit(self.horizontalWidget8)
        self.speedLineEdit.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 255);"))
        self.speedLineEdit.setObjectName(_fromUtf8("speedLineEdit"))
        self.horizontalLayout_11.addWidget(self.speedLineEdit)
        self.gridLayout_8.addWidget(self.horizontalWidget8, 6, 0, 1, 2)
        self.label = QtGui.QLabel(self.gridFrame1)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_8.addWidget(self.label, 7, 0, 1, 1)
        self.horizontalWidget9 = QtGui.QWidget(self.gridFrame1)
        self.horizontalWidget9.setMinimumSize(QtCore.QSize(0, 0))
        self.horizontalWidget9.setObjectName(_fromUtf8("horizontalWidget9"))
        self.horizontalLayout_6 = QtGui.QHBoxLayout(self.horizontalWidget9)
        self.horizontalLayout_6.setMargin(0)
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        self.pushButton_14 = QtGui.QPushButton(self.horizontalWidget9)
        self.pushButton_14.setMinimumSize(QtCore.QSize(0, 0))
        self.pushButton_14.setMaximumSize(QtCore.QSize(16777215, 24))
        self.pushButton_14.setIconSize(QtCore.QSize(16, 16))
        self.pushButton_14.setCheckable(True)
        self.pushButton_14.setObjectName(_fromUtf8("pushButton_14"))
        self.horizontalLayout_6.addWidget(self.pushButton_14)
        self.pushButton_15 = QtGui.QPushButton(self.horizontalWidget9)
        self.pushButton_15.setMaximumSize(QtCore.QSize(16777215, 24))
        self.pushButton_15.setCheckable(True)
        self.pushButton_15.setObjectName(_fromUtf8("pushButton_15"))
        self.horizontalLayout_6.addWidget(self.pushButton_15)
        self.gridLayout_8.addWidget(self.horizontalWidget9, 13, 0, 1, 2)
        self.gridLayout_3.addWidget(self.gridFrame1, 1, 0, 1, 2)
        self.gridFrame2 = QtGui.QFrame(self.centralwidget)
        self.gridFrame2.setMinimumSize(QtCore.QSize(0, 0))
        self.gridFrame2.setFrameShape(QtGui.QFrame.StyledPanel)
        self.gridFrame2.setObjectName(_fromUtf8("gridFrame2"))
        self.gridLayout_2 = QtGui.QGridLayout(self.gridFrame2)
        self.gridLayout_2.setMargin(6)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.pushButton_23 = QtGui.QPushButton(self.gridFrame2)
        self.pushButton_23.setMaximumSize(QtCore.QSize(16777215, 24))
        self.pushButton_23.setObjectName(_fromUtf8("pushButton_23"))
        self.gridLayout_2.addWidget(self.pushButton_23, 6, 1, 1, 1)
        self.pushButton_22 = QtGui.QPushButton(self.gridFrame2)
        self.pushButton_22.setMaximumSize(QtCore.QSize(16777215, 24))
        self.pushButton_22.setObjectName(_fromUtf8("pushButton_22"))
        self.gridLayout_2.addWidget(self.pushButton_22, 6, 0, 1, 1)
        self.pushButton_20 = QtGui.QPushButton(self.gridFrame2)
        self.pushButton_20.setMaximumSize(QtCore.QSize(16777215, 24))
        self.pushButton_20.setObjectName(_fromUtf8("pushButton_20"))
        self.gridLayout_2.addWidget(self.pushButton_20, 5, 0, 1, 1)
        self.pushButton_21 = QtGui.QPushButton(self.gridFrame2)
        self.pushButton_21.setMaximumSize(QtCore.QSize(16777215, 24))
        self.pushButton_21.setObjectName(_fromUtf8("pushButton_21"))
        self.gridLayout_2.addWidget(self.pushButton_21, 5, 1, 1, 1)
        self.pushButton_17 = QtGui.QPushButton(self.gridFrame2)
        self.pushButton_17.setMaximumSize(QtCore.QSize(16777215, 24))
        self.pushButton_17.setObjectName(_fromUtf8("pushButton_17"))
        self.gridLayout_2.addWidget(self.pushButton_17, 1, 1, 1, 1)
        self.pushButton_16 = QtGui.QPushButton(self.gridFrame2)
        self.pushButton_16.setMaximumSize(QtCore.QSize(16777215, 24))
        self.pushButton_16.setObjectName(_fromUtf8("pushButton_16"))
        self.gridLayout_2.addWidget(self.pushButton_16, 1, 0, 1, 1)
        self.pushButton_18 = QtGui.QPushButton(self.gridFrame2)
        self.pushButton_18.setMaximumSize(QtCore.QSize(16777215, 24))
        self.pushButton_18.setObjectName(_fromUtf8("pushButton_18"))
        self.gridLayout_2.addWidget(self.pushButton_18, 2, 0, 1, 1)
        self.pushButton_19 = QtGui.QPushButton(self.gridFrame2)
        self.pushButton_19.setMaximumSize(QtCore.QSize(16777215, 24))
        self.pushButton_19.setObjectName(_fromUtf8("pushButton_19"))
        self.gridLayout_2.addWidget(self.pushButton_19, 2, 1, 1, 1)
        self.cellListTable = QtGui.QTableWidget(self.gridFrame2)
        self.cellListTable.setMaximumSize(QtCore.QSize(16777215, 115))
        self.cellListTable.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 255);"))
        self.cellListTable.setRowCount(4)
        self.cellListTable.setObjectName(_fromUtf8("cellListTable"))
        self.cellListTable.setColumnCount(5)
        item = QtGui.QTableWidgetItem()
        self.cellListTable.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.cellListTable.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.cellListTable.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.cellListTable.setHorizontalHeaderItem(3, item)
        item = QtGui.QTableWidgetItem()
        self.cellListTable.setHorizontalHeaderItem(4, item)
        self.cellListTable.horizontalHeader().setStretchLastSection(True)
        self.cellListTable.verticalHeader().setVisible(False)
        self.cellListTable.verticalHeader().setDefaultSectionSize(22)
        self.gridLayout_2.addWidget(self.cellListTable, 4, 0, 1, 2)
        self.label_25 = QtGui.QLabel(self.gridFrame2)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_25.setFont(font)
        self.label_25.setStyleSheet(_fromUtf8("background-color: rgb(0, 196, 255);\n"
""))
        self.label_25.setObjectName(_fromUtf8("label_25"))
        self.gridLayout_2.addWidget(self.label_25, 0, 0, 1, 2)
        self.pushButton_24 = QtGui.QPushButton(self.gridFrame2)
        self.pushButton_24.setMaximumSize(QtCore.QSize(16777215, 24))
        self.pushButton_24.setObjectName(_fromUtf8("pushButton_24"))
        self.gridLayout_2.addWidget(self.pushButton_24, 7, 0, 1, 1)
        self.pushButton_25 = QtGui.QPushButton(self.gridFrame2)
        self.pushButton_25.setMaximumSize(QtCore.QSize(16777215, 24))
        self.pushButton_25.setObjectName(_fromUtf8("pushButton_25"))
        self.gridLayout_2.addWidget(self.pushButton_25, 7, 1, 1, 1)
        self.gridLayout_3.addWidget(self.gridFrame2, 2, 0, 1, 2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 546, 25))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.label_2.setText(_translate("MainWindow", "Connection Panel", None))
        self.SM5_1PowerBtn.setText(_translate("MainWindow", "Switch On XYZ of Dev1", None))
        self.connectBtn.setText(_translate("MainWindow", "Connect SM-5 and C-843", None))
        self.SM5_2PowerBtn.setText(_translate("MainWindow", "Switch On XYZ of Dev2", None))
        self.label_3.setText(_translate("MainWindow", "Luigs&Neumann SM-5", None))
        self.label_4.setText(_translate("MainWindow", "Physik Instrumente C-843", None))
        self.label_7.setText(_translate("MainWindow", "C-843 Reference ", None))
        self.C843XYPowerBtn.setText(_translate("MainWindow", "Switch On XY", None))
        self.refLocationBtn.setText(_translate("MainWindow", "Saved Stage Location", None))
        self.refPositiveBtn.setText(_translate("MainWindow", "Positive Switch Limit", None))
        self.refNegativeBtn.setText(_translate("MainWindow", "Negative Switch Limit", None))
        self.C843ZPowerBtn.setText(_translate("MainWindow", "Switch On Z", None))
        self.label_13.setText(_translate("MainWindow", "set pos. (μm)", None))
        self.minMaxXLocationValueLabel.setText(_translate("MainWindow", ".", None))
        self.minMaxYLocationValueLabel.setText(_translate("MainWindow", ".", None))
        self.minMaxZLocationValueLabel.setText(_translate("MainWindow", ".", None))
        self.label_8.setText(_translate("MainWindow", "Move Panel", None))
        self.isXLocationValueLabel.setText(_translate("MainWindow", ".", None))
        self.isYLocationValueLabel.setText(_translate("MainWindow", ".", None))
        self.isZLocationValueLabel.setText(_translate("MainWindow", ".", None))
        self.label_22.setText(_translate("MainWindow", ".", None))
        self.label_21.setText(_translate("MainWindow", ".", None))
        self.label_20.setText(_translate("MainWindow", ".", None))
        self.label_24.setText(_translate("MainWindow", "Step (μm)", None))
        self.label_6.setText(_translate("MainWindow", "Speed", None))
        self.label_23.setText(_translate("MainWindow", "set pos. (μm)", None))
        self.label_9.setText(_translate("MainWindow", "max pos. (μm)", None))
        self.pushButton_9.setText(_translate("MainWindow", "Activate Controller", None))
        self.fineBtn.setText(_translate("MainWindow", "Fine", None))
        self.smallBtn.setText(_translate("MainWindow", "Small", None))
        self.MediumBtn.setText(_translate("MainWindow", "Medium", None))
        self.coarseBtn.setText(_translate("MainWindow", "Coarse", None))
        self.label_17.setText(_translate("MainWindow", "current pos. (μm)", None))
        self.label_18.setText(_translate("MainWindow", "Step (μm)", None))
        self.label_19.setText(_translate("MainWindow", "Speed", None))
        self.label.setText(_translate("MainWindow", "current pos. (μm)", None))
        self.pushButton_14.setText(_translate("MainWindow", "Track Stage with z-Movement", None))
        self.pushButton_15.setText(_translate("MainWindow", "Track Stage with xz-Movement", None))
        self.pushButton_23.setText(_translate("MainWindow", "Remove Item", None))
        self.pushButton_22.setText(_translate("MainWindow", "Record Depth", None))
        self.pushButton_20.setText(_translate("MainWindow", "Move to Item", None))
        self.pushButton_21.setText(_translate("MainWindow", "Update Item Location", None))
        self.pushButton_17.setText(_translate("MainWindow", "E2 MLI", None))
        self.pushButton_16.setText(_translate("MainWindow", "E1 MLI", None))
        self.pushButton_18.setText(_translate("MainWindow", "E1 PC", None))
        self.pushButton_19.setText(_translate("MainWindow", "E2 PC", None))
        item = self.cellListTable.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "#", None))
        item = self.cellListTable.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "type", None))
        item = self.cellListTable.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "New Column", None))
        item = self.cellListTable.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "depth", None))
        item = self.cellListTable.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "location", None))
        self.label_25.setText(_translate("MainWindow", "List of recorded Locations", None))
        self.pushButton_24.setText(_translate("MainWindow", "Save Locations", None))
        self.pushButton_25.setText(_translate("MainWindow", "Load Locations", None))

