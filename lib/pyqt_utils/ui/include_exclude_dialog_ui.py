# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'lib/pyqt_utils/ui/include_exclude_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_IncludeExcludeDialog(object):
    def setupUi(self, IncludeExcludeDialog):
        IncludeExcludeDialog.setObjectName("IncludeExcludeDialog")
        IncludeExcludeDialog.resize(1103, 562)
        icon = QtGui.QIcon.fromTheme("list-remove")
        IncludeExcludeDialog.setWindowIcon(icon)
        self.verticalLayout = QtWidgets.QVBoxLayout(IncludeExcludeDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.splitter = QtWidgets.QSplitter(IncludeExcludeDialog)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.layoutWidget = QtWidgets.QWidget(self.splitter)
        self.layoutWidget.setObjectName("layoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.layoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.removeIncludeButton = QtWidgets.QToolButton(self.layoutWidget)
        icon = QtGui.QIcon.fromTheme("list-remove")
        self.removeIncludeButton.setIcon(icon)
        self.removeIncludeButton.setToolButtonStyle(QtCore.Qt.ToolButtonFollowStyle)
        self.removeIncludeButton.setObjectName("removeIncludeButton")
        self.gridLayout.addWidget(self.removeIncludeButton, 0, 3, 1, 1)
        self.label = QtWidgets.QLabel(self.layoutWidget)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.andIncludeButton = QtWidgets.QToolButton(self.layoutWidget)
        self.andIncludeButton.setObjectName("andIncludeButton")
        self.gridLayout.addWidget(self.andIncludeButton, 0, 1, 1, 1)
        self.orIncludeButton = QtWidgets.QToolButton(self.layoutWidget)
        self.orIncludeButton.setObjectName("orIncludeButton")
        self.gridLayout.addWidget(self.orIncludeButton, 0, 2, 1, 1)
        self.includeView = QtWidgets.QTreeView(self.layoutWidget)
        self.includeView.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.includeView.setRootIsDecorated(False)
        self.includeView.setObjectName("includeView")
        self.gridLayout.addWidget(self.includeView, 1, 0, 1, 4)
        self.layoutWidget1 = QtWidgets.QWidget(self.splitter)
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.layoutWidget1)
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_4 = QtWidgets.QLabel(self.layoutWidget1)
        self.label_4.setObjectName("label_4")
        self.gridLayout_3.addWidget(self.label_4, 0, 0, 1, 1)
        self.includeButton = QtWidgets.QToolButton(self.layoutWidget1)
        icon = QtGui.QIcon.fromTheme("go-previous")
        self.includeButton.setIcon(icon)
        self.includeButton.setToolButtonStyle(QtCore.Qt.ToolButtonFollowStyle)
        self.includeButton.setObjectName("includeButton")
        self.gridLayout_3.addWidget(self.includeButton, 0, 1, 1, 1)
        self.excludeButton = QtWidgets.QToolButton(self.layoutWidget1)
        icon = QtGui.QIcon.fromTheme("go-next")
        self.excludeButton.setIcon(icon)
        self.excludeButton.setToolButtonStyle(QtCore.Qt.ToolButtonFollowStyle)
        self.excludeButton.setObjectName("excludeButton")
        self.gridLayout_3.addWidget(self.excludeButton, 0, 2, 1, 1)
        self.possibleTagsWidget = QtWidgets.QListWidget(self.layoutWidget1)
        self.possibleTagsWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.possibleTagsWidget.setObjectName("possibleTagsWidget")
        self.gridLayout_3.addWidget(self.possibleTagsWidget, 1, 0, 1, 3)
        self.layoutWidget2 = QtWidgets.QWidget(self.splitter)
        self.layoutWidget2.setObjectName("layoutWidget2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.layoutWidget2)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_2 = QtWidgets.QLabel(self.layoutWidget2)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 0, 0, 1, 1)
        self.andExcludeButton = QtWidgets.QToolButton(self.layoutWidget2)
        self.andExcludeButton.setObjectName("andExcludeButton")
        self.gridLayout_2.addWidget(self.andExcludeButton, 0, 1, 1, 1)
        self.orExcludeButton = QtWidgets.QToolButton(self.layoutWidget2)
        self.orExcludeButton.setObjectName("orExcludeButton")
        self.gridLayout_2.addWidget(self.orExcludeButton, 0, 2, 1, 1)
        self.removeExcludeButton = QtWidgets.QToolButton(self.layoutWidget2)
        icon = QtGui.QIcon.fromTheme("list-remove")
        self.removeExcludeButton.setIcon(icon)
        self.removeExcludeButton.setToolButtonStyle(QtCore.Qt.ToolButtonFollowStyle)
        self.removeExcludeButton.setObjectName("removeExcludeButton")
        self.gridLayout_2.addWidget(self.removeExcludeButton, 0, 3, 1, 1)
        self.excludeView = QtWidgets.QTreeView(self.layoutWidget2)
        self.excludeView.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.excludeView.setRootIsDecorated(False)
        self.excludeView.setObjectName("excludeView")
        self.gridLayout_2.addWidget(self.excludeView, 1, 0, 1, 4)
        self.verticalLayout.addWidget(self.splitter)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_3 = QtWidgets.QLabel(IncludeExcludeDialog)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout.addWidget(self.label_3)
        self.searchLineEdit = QtWidgets.QLineEdit(IncludeExcludeDialog)
        self.searchLineEdit.setClearButtonEnabled(True)
        self.searchLineEdit.setObjectName("searchLineEdit")
        self.horizontalLayout.addWidget(self.searchLineEdit)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(IncludeExcludeDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.label_3.setBuddy(self.searchLineEdit)

        self.retranslateUi(IncludeExcludeDialog)
        self.buttonBox.accepted.connect(IncludeExcludeDialog.accept) # type: ignore
        self.buttonBox.rejected.connect(IncludeExcludeDialog.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(IncludeExcludeDialog)
        IncludeExcludeDialog.setTabOrder(self.searchLineEdit, self.includeView)
        IncludeExcludeDialog.setTabOrder(self.includeView, self.possibleTagsWidget)
        IncludeExcludeDialog.setTabOrder(self.possibleTagsWidget, self.excludeView)
        IncludeExcludeDialog.setTabOrder(self.excludeView, self.andIncludeButton)
        IncludeExcludeDialog.setTabOrder(self.andIncludeButton, self.orIncludeButton)
        IncludeExcludeDialog.setTabOrder(self.orIncludeButton, self.includeButton)
        IncludeExcludeDialog.setTabOrder(self.includeButton, self.excludeButton)
        IncludeExcludeDialog.setTabOrder(self.excludeButton, self.andExcludeButton)
        IncludeExcludeDialog.setTabOrder(self.andExcludeButton, self.orExcludeButton)

    def retranslateUi(self, IncludeExcludeDialog):
        _translate = QtCore.QCoreApplication.translate
        IncludeExcludeDialog.setWindowTitle(_translate("IncludeExcludeDialog", "Tag filter"))
        self.removeIncludeButton.setText(_translate("IncludeExcludeDialog", "Delete"))
        self.label.setText(_translate("IncludeExcludeDialog", "Include:"))
        self.andIncludeButton.setText(_translate("IncludeExcludeDialog", "AND"))
        self.orIncludeButton.setText(_translate("IncludeExcludeDialog", "OR"))
        self.label_4.setText(_translate("IncludeExcludeDialog", "Possible:"))
        self.includeButton.setText(_translate("IncludeExcludeDialog", "Include"))
        self.excludeButton.setText(_translate("IncludeExcludeDialog", "Exclude"))
        self.label_2.setText(_translate("IncludeExcludeDialog", "Exclude:"))
        self.andExcludeButton.setText(_translate("IncludeExcludeDialog", "AND"))
        self.orExcludeButton.setText(_translate("IncludeExcludeDialog", "OR"))
        self.removeExcludeButton.setText(_translate("IncludeExcludeDialog", "Delete"))
        self.label_3.setText(_translate("IncludeExcludeDialog", "&Search:"))