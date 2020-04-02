# Author:           Andrew Derringer
# Last Modified:    4/1/2020
# Description:      PyQt5 application that generates a popup window for locating file and retrieving file path
#                   for MDF and DBC file.


from PyQt5 import QtWidgets, QtCore, QtGui

import os


class ImportPopup(QtWidgets.QMainWindow):
    
    main = None

    def __init__(self, dbc="", mdf="", parent=None):
        super(ImportPopup, self).__init__(parent)
        self.placeWidgets()

        self.dbc_path.setText(dbc)
        self.mdf_path.setText(mdf)


    def placeWidgets(self):
        self.setWindowTitle("Import CAN Data")
        centralWidget = QtWidgets.QWidget()
        self.setCentralWidget(centralWidget)

        ################################## Grid Layout - Sizing ###################################

        grid = QtWidgets.QGridLayout()
        centralWidget.setLayout(grid)

        grid.setVerticalSpacing(5)
        grid.setRowStretch(4, 1)
        grid.setColumnStretch(1, 0)
        grid.setColumnStretch(2, 1)
        grid.setColumnStretch(3, 0)
        grid.setColumnStretch(4, 0)

        grid.setColumnMinimumWidth(2, 400)
        grid.setRowMinimumHeight(4, 20)

        ################################## Grid Layout - Widgets ##################################

        grid.addWidget(QtWidgets.QLabel("Select Files:"), 1, 1, 1, 1)

        # DBC file path field.
        grid.addWidget(QtWidgets.QLabel("DBC:"), 2, 1, 1, 1)
        self.dbc_path = QtWidgets.QLineEdit()
        self.dbc_path.setMaximumWidth(600)
        grid.addWidget(self.dbc_path, 2, 2, 1, 2)

        # Select DBC file path button.
        get_dbc = QtWidgets.QPushButton("Select")
        get_dbc.setFixedWidth(65)
        get_dbc.clicked.connect(self.getDBC)
        grid.addWidget(get_dbc, 2, 4, 1, 1)

        # MDF file path field.
        grid.addWidget(QtWidgets.QLabel("MDF:"), 3, 1, 1, 1)
        self.mdf_path = QtWidgets.QLineEdit()
        self.mdf_path.setMaximumWidth(600)
        grid.addWidget(self.mdf_path, 3, 2, 1, 2)

        # Select MDF file path button.
        get_mdf = QtWidgets.QPushButton("Select")
        get_mdf.setFixedWidth(65)
        get_mdf.clicked.connect(self.getMDF)
        grid.addWidget(get_mdf, 3, 4, 1, 1)

        # Submit button.
        self.submit = QtWidgets.QPushButton("Submit")
        self.submit.setFixedWidth(65)
        self.submit.clicked.connect(self.passFiles)
        grid.addWidget(self.submit, 5, 3, 1, 1)

        # Cancel button.
        cancel = QtWidgets.QPushButton("Cancel")
        cancel.setFixedWidth(65)
        cancel.clicked.connect(self.close)
        grid.addWidget(cancel, 5, 4, 1, 1)



    def getDBC(self):
        # Get user selected DBC file path.
        file_return = QtWidgets.QFileDialog.getOpenFileName(self, 'Select file', os.getcwd(), "DBC (*.dbc)")
        self.dbc_path.setText(file_return[0])


    def getMDF(self):
        # Get user selected MDF file path.
        file_return = QtWidgets.QFileDialog.getOpenFileName(self, 'Select file', os.getcwd(), "MDF (*.mf4)")
        self.mdf_path.setText(file_return[0])


    def passFiles(self):
        if self.dbc_path.text() == "":
            self.error_window = QtWidgets.QErrorMessage()
            self.error_window.showMessage("Error: At least a DBC file must be selected.")
        else:
            self.main.setDataFiles(self.dbc_path.text(), self.mdf_path.text())
            if self.mdf_path.text() != "":
                self.main.extractMDF()

        self.close()
