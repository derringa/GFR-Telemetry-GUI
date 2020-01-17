from PyQt5 import QtWidgets, QtCore, QtGui
from asammdf import MDF
#from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGroupBox, QSlider, QLabel, QVBoxLayout, QHBoxLayout, \
    #QPushButton, QFormLayout, QGridLayout, QTabWidget, QMessageBox, QInputDialog, QLineEdit, QLabel
#from PyQt5.QtCore import Qt, QSize
#from PyQt5.QtGui import QPainter, QBrush, QPen, QFont, QColor
from random import random
import numpy as np
from numpy import sin, cos, pi
from enum import Enum
import sys
import pyqtgraph
from pyqtgraph import PlotWidget, plot
from Tab import Tab


# class popupWindow(QtWidgets.QMainWindow):

#     main = None

#     def __init__(self, parent=None):
#         super(popupWindow, self).__init__(parent)

#         self.setWindowTitle("Add New Tab")
#         centralWidget = QtWidgets.QWidget()
#         self.setCentralWidget(centralWidget)

#         self.name = QtWidgets.QLineEdit()
#         self.type = QtWidgets.QLineEdit()

#         tabForm = QtWidgets.QFormLayout()
#         tabForm.addRow(QtWidgets.QLabel("Name:"), self.name)
#         tabForm.addRow(QtWidgets.QLabel("Type:"), self.type)

#         submit = QtWidgets.QPushButton("Submit")
#         submit.clicked.connect(self.generate_tab)

#         cancel = QtWidgets.QPushButton("Cancel")
#         cancel.clicked.connect(self.close)

#         tabForm.addRow(submit, cancel)
#         centralWidget.setLayout(tabForm)

#     def generate_tab(self):
#         newTab = Tab(self.name.text())
#         self.main.tabList.append(newTab)
#         print(newTab.title)
#         self.main.add_tab(newTab)
#         self.close()



class main(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(main, self).__init__(parent)

        self.channel_list = []
        self.mdf_list = []

        # Apply title and staring size and location
        # for window on startup
        self.setWindowTitle("GFR Telemtry Data")
        self.setGeometry(0, 0, 1250, 750)

        # centralWidget houses layout features
        # and smaller widgets within the app
        self.centralWidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralWidget)

        ################################################################
        # Static tool bar
        ################################################################

        # Tool bar setup
        self.statusBar()
        mainMenu = self.menuBar()

        # File drop down
        fileMenu = mainMenu.addMenu("&File")

        # File drop down option - exit
        extractAction = QtGui.QAction("&Exit", self)
        extractAction.setShortcut("Ctrl+Q")
        extractAction.setStatusTip("&Leave the App")
        extractAction.triggered.connect(self.close_application)
        fileMenu.addAction(extractAction)  # add to file drop down

        # View drop down
        # viewMenu = mainMenu.addMenu("&View")

        # View drop down option - add tab
        # addTab = QtGui.QAction("&Add Tab", self)
        # addTab.setShortcut("Ctrl+T")
        # addTab.setStatusTip("&Add tab with custom graph display")
        # addTab.triggered.connect(self.tab_window)
        # viewMenu.addAction(addTab) # add to view drop down

        ################################################################
        # Main Widget Layout
        ################################################################

        # Create horizontal format for main widget subsections
        self.horizontalSections = QtWidgets.QHBoxLayout()
        self.centralWidget.setLayout(self.horizontalSections)
        
        # Left subsection - Virtical Stacking Layout
        self.left_vert_sec = QtWidgets.QVBoxLayout()
        self.horizontalSections.addLayout(self.left_vert_sec)

        # Button - "Load dbc file"
        self.upload_dbc_file = QtWidgets.QPushButton("Load DBC File")
        self.upload_dbc_file.clicked.connect(self.get_dbc_file) # On click call member function get_dbc_file
        self.left_vert_sec.addWidget(self.upload_dbc_file)

        # Button - "Load mf4 file"
        self.upload_mf4_file = QtWidgets.QPushButton("Load MF4 File")
        self.upload_mf4_file.setEnabled(False)
        self.upload_mf4_file.clicked.connect(self.get_mf4_file) # On click call member function get_mf4_file
        self.left_vert_sec.addWidget(self.upload_mf4_file)

        #Channels - Checkbox list
        self.channel_selectors = QtWidgets.QListWidget()
        self.channel_selectors.setFixedWidth(300)
        self.channel_selectors.itemChanged.connect(self.manage_channels)
        self.left_vert_sec.addWidget(self.channel_selectors)

        # Button - "Plot channels"
        self.plot_channels = QtWidgets.QPushButton("Plot Channels")
        self.plot_channels.setEnabled(False)
        self.plot_channels.clicked.connect(self.load_plots) # On click call member function load_plots
        self.left_vert_sec.addWidget(self.plot_channels)

        # Right subsection - Tabbed graphic data
        # self.tabList = []
        self.tabs = QtWidgets.QTabWidget()
        self.horizontalSections.addWidget(self.tabs)

        # Add horizontal subsections to central widget


        # holds instance up add tab popup so that it data
        # is not cleaned up immediately upon close
        self.popup = None

    # def tab_window(self):
    #     self.popup = popupWindow()
    #     self.popup.main = self
    #     self.popup.show()

    # def add_tab(self, item):
    #     #item.updateData(self.hour, self.temperature)
    #     self.tabs.addTab(item.tab, item.title)

    def close_application(self):
        print("Good-Bye!")
        sys.exit()

    def get_mf4_file(self):
        mf4_path = QtWidgets.QFileDialog.getOpenFileName(self, 'Select file', 'c:\\', "MDF (*.mf4)")
        mdf_file = MDF(mf4_path[0])
        self.mdf_extracted = mdf_file.extract_can_logging([self.dbc_path[0]])
        for ch in self.mdf_extracted:
            self.mdf_list.append(ch.name)
        self.plot_channels.setEnabled(True)


    def get_dbc_file(self):
        self.dbc_path = QtWidgets.QFileDialog.getOpenFileName(self, 'Select file', 'c:\\', "DBC (*.dbc)")
        with open(self.dbc_path[0], 'r') as fd:
            for line in fd:
                line_list = line.split(None, 2)
                if not line_list:
                    continue
                elif line_list[0] == 'SG_':
                    item = QtWidgets.QListWidgetItem(line_list[1])
                    item.setCheckState(False)
                    #print(item.text()) # for testing
                    self.channel_selectors.addItem(item)
        self.upload_mf4_file.setEnabled(True)
    
    def manage_channels(self, item):
        if item.checkState() == False:
            self.channel_list[:] = [ch for ch in self.channel_list if ch != item.text()]
            print("Unchecked!")
        else:
            self.channel_list.append(item.text())
            print("Checked!")
        print(self.channel_list)

    def load_plots(self):
        curr_tabs = []
        for i in reversed(range(self.tabs.count())):
            tab_name = self.tabs.tabText(i)
            if tab_name not in self.channel_list:
                self.tabs.removeTab(i)
            else:
                curr_tabs.append(tab_name)

        for ch in self.channel_list:
            #print(ch)
            if ch in self.mdf_list and ch not in curr_tabs:
                obj_data = self.mdf_extracted.get(ch)
                new_tab = Tab(ch, obj_data.timestamps, obj_data.samples)
                self.tabs.addTab(new_tab.tab, new_tab.title)



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWin = main()
    mainWin.show()
    sys.exit( app.exec_() )
