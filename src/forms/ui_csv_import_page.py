# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'csv_import_page.ui'
#
# Created: Thu Jun 27 10:21:34 2013
#      by: PyQt4 UI code generator 4.10.1
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

class Ui_WizardPage(object):
    def setupUi(self, WizardPage):
        WizardPage.setObjectName(_fromUtf8("WizardPage"))
        WizardPage.resize(646, 630)
        WizardPage.setMinimumSize(QtCore.QSize(500, 630))
        self.verticalLayout_2 = QtGui.QVBoxLayout(WizardPage)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.instructions = QtGui.QLabel(WizardPage)
        self.instructions.setWordWrap(True)
        self.instructions.setObjectName(_fromUtf8("instructions"))
        self.verticalLayout_2.addWidget(self.instructions)
        self.groupBox = QtGui.QGroupBox(WizardPage)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setMinimumSize(QtCore.QSize(0, 200))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.from_excel_chkbx = QtGui.QCheckBox(self.groupBox)
        self.from_excel_chkbx.setObjectName(_fromUtf8("from_excel_chkbx"))
        self.verticalLayout.addWidget(self.from_excel_chkbx)
        self.has_headers_chkbx = QtGui.QCheckBox(self.groupBox)
        self.has_headers_chkbx.setChecked(True)
        self.has_headers_chkbx.setObjectName(_fromUtf8("has_headers_chkbx"))
        self.verticalLayout.addWidget(self.has_headers_chkbx)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.delimter_lbl = QtGui.QLabel(self.groupBox)
        self.delimter_lbl.setObjectName(_fromUtf8("delimter_lbl"))
        self.horizontalLayout.addWidget(self.delimter_lbl)
        self.delimter_le = QtGui.QLineEdit(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.delimter_le.sizePolicy().hasHeightForWidth())
        self.delimter_le.setSizePolicy(sizePolicy)
        self.delimter_le.setMaximumSize(QtCore.QSize(20, 16777215))
        self.delimter_le.setObjectName(_fromUtf8("delimter_le"))
        self.horizontalLayout.addWidget(self.delimter_le)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_3.addWidget(self.label_2)
        self.quotechar_le = QtGui.QLineEdit(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.quotechar_le.sizePolicy().hasHeightForWidth())
        self.quotechar_le.setSizePolicy(sizePolicy)
        self.quotechar_le.setMaximumSize(QtCore.QSize(20, 16777215))
        self.quotechar_le.setObjectName(_fromUtf8("quotechar_le"))
        self.horizontalLayout_3.addWidget(self.quotechar_le)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.file_path_lbl = QtGui.QLabel(self.groupBox)
        self.file_path_lbl.setObjectName(_fromUtf8("file_path_lbl"))
        self.horizontalLayout_2.addWidget(self.file_path_lbl)
        self.select_file_btn = QtGui.QPushButton(self.groupBox)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/function_icon_set/function_icon_set/folder_48.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.select_file_btn.setIcon(icon)
        self.select_file_btn.setObjectName(_fromUtf8("select_file_btn"))
        self.horizontalLayout_2.addWidget(self.select_file_btn)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.verticalLayout_2.addWidget(self.groupBox)
        self.groupBox_2 = QtGui.QGroupBox(WizardPage)
        self.groupBox_2.setMinimumSize(QtCore.QSize(0, 120))
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.required_fmt_table = QtGui.QTableWidget(self.groupBox_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.required_fmt_table.sizePolicy().hasHeightForWidth())
        self.required_fmt_table.setSizePolicy(sizePolicy)
        self.required_fmt_table.setMaximumSize(QtCore.QSize(16777215, 70))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        self.required_fmt_table.setFont(font)
        self.required_fmt_table.setObjectName(_fromUtf8("required_fmt_table"))
        self.required_fmt_table.setColumnCount(0)
        self.required_fmt_table.setRowCount(0)
        self.horizontalLayout_4.addWidget(self.required_fmt_table)
        self.verticalLayout_2.addWidget(self.groupBox_2)
        self.preview_grp_box = QtGui.QGroupBox(WizardPage)
        self.preview_grp_box.setObjectName(_fromUtf8("preview_grp_box"))
        self.horizontalLayout_5 = QtGui.QHBoxLayout(self.preview_grp_box)
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.preview_table = QtGui.QTableWidget(self.preview_grp_box)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.preview_table.sizePolicy().hasHeightForWidth())
        self.preview_table.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        self.preview_table.setFont(font)
        self.preview_table.setObjectName(_fromUtf8("preview_table"))
        self.preview_table.setColumnCount(0)
        self.preview_table.setRowCount(0)
        self.horizontalLayout_5.addWidget(self.preview_table)
        self.verticalLayout_2.addWidget(self.preview_grp_box)
        self.delimter_lbl.setBuddy(self.delimter_le)
        self.label_2.setBuddy(self.delimter_le)
        self.file_path_lbl.setBuddy(self.select_file_btn)

        self.retranslateUi(WizardPage)
        QtCore.QMetaObject.connectSlotsByName(WizardPage)

    def retranslateUi(self, WizardPage):
        WizardPage.setWindowTitle(_translate("WizardPage", "WizardPage", None))
        WizardPage.setTitle(_translate("WizardPage", "Choose CSV file", None))
        self.instructions.setText(_translate("WizardPage", "Please select a csv file to import:\n"
"The CSV should match the format of the spreadsheet currently displayed under \"required CSV format\". Don\'t worry if the column titles are not the same, these can be changed later.\n"
"\n"
"Also, things will be OK if you don\'t have data for all the columns, however if you have data for a column to the right of a column for which you do not have data, the left hand column(s) must exist (but have blank cells).\n"
"\n"
"Additional columns will be treated as covariates.", None))
        self.groupBox.setTitle(_translate("WizardPage", "Import Options", None))
        self.from_excel_chkbx.setText(_translate("WizardPage", "csv exported from excel?", None))
        self.has_headers_chkbx.setText(_translate("WizardPage", "Has column labels?", None))
        self.delimter_lbl.setText(_translate("WizardPage", "Delimter:", None))
        self.delimter_le.setText(_translate("WizardPage", ",", None))
        self.label_2.setText(_translate("WizardPage", "Quote Character:", None))
        self.quotechar_le.setText(_translate("WizardPage", "\"", None))
        self.file_path_lbl.setText(_translate("WizardPage", "No file has been chosen.", None))
        self.select_file_btn.setText(_translate("WizardPage", "select csv file ...", None))
        self.groupBox_2.setTitle(_translate("WizardPage", "Required CSV format", None))
        self.preview_grp_box.setTitle(_translate("WizardPage", "Preview of imported data", None))

import icons_rc
