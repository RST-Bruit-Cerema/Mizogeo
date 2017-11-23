# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\martin.schoreisz\.qgis2\python\plugins\Mizogeo\fenetre_menu_Assemblage.ui'
#
# Created: Fri Jun 02 15:51:11 2017
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

class Ui_Dialog_Assemblage(object):
    def setupUi(self, Dialog_Assemblage):
        Dialog_Assemblage.setObjectName(_fromUtf8("Dialog_Assemblage"))
        Dialog_Assemblage.setWindowModality(QtCore.Qt.ApplicationModal)
        Dialog_Assemblage.resize(800, 260)
        Dialog_Assemblage.setMaximumSize(QtCore.QSize(1600, 520))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri Light"))
        font.setPointSize(11)
        Dialog_Assemblage.setFont(font)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog_Assemblage)
        self.verticalLayout.setSpacing(30)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox_Dbf = QtGui.QGroupBox(Dialog_Assemblage)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri Light"))
        font.setPointSize(11)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.groupBox_Dbf.setFont(font)
        self.groupBox_Dbf.setObjectName(_fromUtf8("groupBox_Dbf"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.groupBox_Dbf)
        self.horizontalLayout.setSpacing(20)
        self.horizontalLayout.setContentsMargins(20, 12, 30, 15)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.line_Dbf = QtGui.QLineEdit(self.groupBox_Dbf)
        self.line_Dbf.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.line_Dbf.sizePolicy().hasHeightForWidth())
        self.line_Dbf.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        font.setKerning(True)
        self.line_Dbf.setFont(font)
        self.line_Dbf.setObjectName(_fromUtf8("line_Dbf"))
        self.horizontalLayout.addWidget(self.line_Dbf)
        self.Btn_dbf = QtGui.QToolButton(self.groupBox_Dbf)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Btn_dbf.sizePolicy().hasHeightForWidth())
        self.Btn_dbf.setSizePolicy(sizePolicy)
        self.Btn_dbf.setMinimumSize(QtCore.QSize(70, 30))
        self.Btn_dbf.setMaximumSize(QtCore.QSize(70, 30))
        self.Btn_dbf.setObjectName(_fromUtf8("Btn_dbf"))
        self.horizontalLayout.addWidget(self.Btn_dbf)
        self.verticalLayout.addWidget(self.groupBox_Dbf)
        self.groupBox_Sortie = QtGui.QGroupBox(Dialog_Assemblage)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri Light"))
        font.setPointSize(11)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.groupBox_Sortie.setFont(font)
        self.groupBox_Sortie.setObjectName(_fromUtf8("groupBox_Sortie"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.groupBox_Sortie)
        self.horizontalLayout_2.setSpacing(20)
        self.horizontalLayout_2.setContentsMargins(20, 12, 30, 15)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.line_Sortie = QtGui.QLineEdit(self.groupBox_Sortie)
        self.line_Sortie.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.line_Sortie.sizePolicy().hasHeightForWidth())
        self.line_Sortie.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.line_Sortie.setFont(font)
        self.line_Sortie.setAutoFillBackground(False)
        self.line_Sortie.setStyleSheet(_fromUtf8(""))
        self.line_Sortie.setObjectName(_fromUtf8("line_Sortie"))
        self.horizontalLayout_2.addWidget(self.line_Sortie)
        self.Btn_ChoixSortie = QtGui.QToolButton(self.groupBox_Sortie)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Btn_ChoixSortie.sizePolicy().hasHeightForWidth())
        self.Btn_ChoixSortie.setSizePolicy(sizePolicy)
        self.Btn_ChoixSortie.setMinimumSize(QtCore.QSize(70, 30))
        self.Btn_ChoixSortie.setMaximumSize(QtCore.QSize(70, 30))
        self.Btn_ChoixSortie.setObjectName(_fromUtf8("Btn_ChoixSortie"))
        self.horizontalLayout_2.addWidget(self.Btn_ChoixSortie)
        self.verticalLayout.addWidget(self.groupBox_Sortie)
        self.ButtonBox_Final = QtGui.QDialogButtonBox(Dialog_Assemblage)
        self.ButtonBox_Final.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Help|QtGui.QDialogButtonBox.Ok)
        self.ButtonBox_Final.setObjectName(_fromUtf8("ButtonBox_Final"))
        self.verticalLayout.addWidget(self.ButtonBox_Final)

        self.retranslateUi(Dialog_Assemblage)
        QtCore.QMetaObject.connectSlotsByName(Dialog_Assemblage)

    def retranslateUi(self, Dialog_Assemblage):
        Dialog_Assemblage.setWindowTitle(_translate("Dialog_Assemblage", "Assemblage des tables attributaires", None))
        self.groupBox_Dbf.setTitle(_translate("Dialog_Assemblage", "Dossier contenant les fichiers à assembler", None))
        self.line_Dbf.setToolTip(_translate("Dialog_Assemblage", "Copier/coller l'emplacement des fichiers N_BRUIT_ZBR.dbf et/ou N_BRUIT_CBS.dbf - dossier", None))
        self.line_Dbf.setPlaceholderText(_translate("Dialog_Assemblage", "Emplacement du dossier contenant les fichiers N_BRUIT_ZBR.dbf et/ou N_BRUIT_CBS.dbf", None))
        self.Btn_dbf.setToolTip(_translate("Dialog_Assemblage", "Rechercher le dossier contenant les fichiers .dbf - dossier", None))
        self.Btn_dbf.setText(_translate("Dialog_Assemblage", "...", None))
        self.groupBox_Sortie.setTitle(_translate("Dialog_Assemblage", "Dossier de stockage des fichiers assemblés", None))
        self.line_Sortie.setToolTip(_translate("Dialog_Assemblage", "Copier/coller l'emplacement où seront stockés les fichiers assemblés - dossier", None))
        self.line_Sortie.setPlaceholderText(_translate("Dialog_Assemblage", "Choisir le dossier recevant les fichiers assemblés", None))
        self.Btn_ChoixSortie.setToolTip(_translate("Dialog_Assemblage", "Rechercher le dossier de stockage des fichiers assemblés .dbf - dossier", None))
        self.Btn_ChoixSortie.setText(_translate("Dialog_Assemblage", "...", None))

