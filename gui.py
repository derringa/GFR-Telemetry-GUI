# Author:           Andrew Derringer
# Last Modified:    1/17/2020
# Description:      PyQt5 application that generates customizable display of CAN data using MDF and DBC files.
#                   This application was made using data and specifications from Oregon State Univesity Global
#                   formula racing team.

from PyQt5 import QtWidgets, QtCore, QtGui
from asammdf import MDF
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
        self.play_status = False

        # Apply startup characteristics for window
        self.setWindowTitle("GFR Telemtry Data")
        self.setGeometry(0, 0, 1250, 750)

        # centralWidget houses layout features within the app
        self.centralWidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralWidget)

        # Section for adding toolbar sections and subsections
        self.build_toolbar()

        # Sections for placing all layouts and widgets
        self.place_widgets()

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


    def build_toolbar(self):
        # Toolbar setup
        self.statusBar() # Along bottom of screen
        mainMenu = self.menuBar() # Along top of screen

        # File drop down
        fileMenu = mainMenu.addMenu("&File")

        # File drop down option - exit
        extractAction = QtGui.QAction("&Exit", self)
        extractAction.setShortcut("Ctrl+Q") # Set key-board shortcut
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


    def place_widgets(self):

        ################################### Format Main Window ####################################

        # Create horizontal format for main widget subsections
        self.horizontalSections = QtWidgets.QHBoxLayout()
        self.centralWidget.setLayout(self.horizontalSections)
        
        ################################ Main Window - Left Column ################################

        # Left subsection - Virtical Stacking Layout
        self.left_vert_sec = QtWidgets.QVBoxLayout()
        self.horizontalSections.addLayout(self.left_vert_sec)

        # Button - "Load dbc file"
        self.upload_dbc_file = QtWidgets.QPushButton("Load DBC File")
        self.upload_dbc_file.clicked.connect(self.load_dbc_file) # On click call member function load_dbc_file
        self.left_vert_sec.addWidget(self.upload_dbc_file)

        # Button - "Load MDF file"
        self.upload_mdf_file = QtWidgets.QPushButton("Load MDF File")
        self.upload_mdf_file.setEnabled(False)
        self.upload_mdf_file.clicked.connect(self.load_mdf_file) # On click call member function load_mdf_file
        self.left_vert_sec.addWidget(self.upload_mdf_file)

        #Channels - Checkbox list
        self.channel_selectors = QtWidgets.QListWidget()
        self.channel_selectors.setFixedWidth(300)
        self.channel_selectors.itemChanged.connect(self.check_event)
        self.left_vert_sec.addWidget(self.channel_selectors)

        # Button - "Plot channels"
        self.plot_channels = QtWidgets.QPushButton("Plot Channels")
        self.plot_channels.setEnabled(False)
        self.plot_channels.clicked.connect(self.post_load_plots) # On click call member function load_plots
        self.left_vert_sec.addWidget(self.plot_channels)

        ############################### Main Window - Middle Column ###############################

        # Middle subsection - Tabbed graphic data
        self.tabs = QtWidgets.QTabWidget()
        self.horizontalSections.addWidget(self.tabs)

        ############################### Main Window - Right Column ################################

        # Right subsection - Virtical Stacking Layout
        self.right_vert_sec = QtWidgets.QVBoxLayout()
        self.horizontalSections.addLayout(self.right_vert_sec)

        # Horizontal Buttons layout - Back-skip, play, pause, forward-skip
        self.play_horz_sec = QtWidgets.QVBoxLayout()
        self.right_vert_sec.addLayout(self.play_horz_sec)

        # Button - "Play"
        self.play_button = QtWidgets.QPushButton()
        self.play_button.setIcon(QtGui.QIcon("./images/play-button.png"))
        self.play_button.clicked.connect(self.play_pause_toggle) # On click call member function load_plots
        self.play_horz_sec.addWidget(self.play_button)


    def close_application(self):
        print("Good-Bye!")
        sys.exit()


    def load_mdf_file(self):
        # Get user selected MDF file path and generate an mdf object using asammdf library.
        mf4_path = QtWidgets.QFileDialog.getOpenFileName(self, 'Select file', 'c:\\', "MDF (*.mf4)") # get file path.
        mdf_file = MDF(mf4_path[0])  # generate mdf object using path string.
        self.mdf_extracted = mdf_file.extract_can_logging([self.dbc_path[0]]) # extract data with dbc file path string.

        # Collect name of all channels into a list.
        for ch in self.mdf_extracted:
            self.mdf_list.append(ch.name)

        # Compare list of DBC channels to those in MDF file and remove those not in both.
        for i in reversed(range(self.channel_selectors.count())):
            ch_name = self.channel_selectors.item(i).text()
            if ch_name not in self.mdf_list: 
                self.channel_selectors.takeItem(i) # Not present then delete from checkbox list.
                if ch_name in self.channel_list:
                    self.channel_list.remove(ch_name) # If already checked then also delete from selected channels list.

        # Activate the Plot Channel button only after MDF file is loaded and operated on.
        self.plot_channels.setEnabled(True)


    def load_dbc_file(self):
        # Get user slected DBC file path.
        self.dbc_path = QtWidgets.QFileDialog.getOpenFileName(self, 'Select file', 'c:\\', "DBC (*.dbc)")

        # Open file and add channel name to list under conditions.
        with open(self.dbc_path[0], 'r') as fd:
            for line in fd:
                line_list = line.split(None, 2) # grab first 2 space delimited strings.
                if not line_list: # disregard empty lines.
                    continue
                elif line_list[0] == 'SG_': # only work with lines whose first string is 'SG_'.
                    item = QtWidgets.QListWidgetItem(line_list[1]) # add second string to a checkbock widget list item.
                    item.setCheckState(False)
                    self.channel_selectors.addItem(item)

        # Activate the Load MF4 File button only after DBC file is loaded and operated on.
        self.upload_mdf_file.setEnabled(True)
    

    def check_event(self, item):
        # If changed checkbox is unchecked then remove from the desired channels list but if checked then add to list.
        if item.checkState() == False:
            self.channel_list[:] = [ch for ch in self.channel_list if ch != item.text()]
        else:
            self.channel_list.append(item.text())



    def post_load_plots(self):
        curr_tabs = [] # Temporary list of tabs already displayed to avoid reproducing on refresh.

        # Iterate through tabs and if no longer on desired channel list them remove them else add to current tabs list.
        for i in reversed(range(self.tabs.count())):
            tab_name = self.tabs.tabText(i)
            if tab_name not in self.channel_list: 
                self.tabs.removeTab(i) # Not present them delete.
            else:
                curr_tabs.append(tab_name) # Present then add to current tabs temp list.

        # If channel doesn't have a tab then create tab with graph.
        for ch in self.channel_list:
            if ch not in curr_tabs:
                obj_data = self.mdf_extracted.get(ch) # Get channel by specific name.
                new_tab = Tab(ch, obj_data.timestamps, obj_data.samples) # Generate tab object using mdf channel name and time and data values.
                self.tabs.addTab(new_tab.get_tab_widget(), new_tab.get_title()) # Add tab to widget.

    def play_pause_toggle(self):
        if self.play_status == False:
            self.play_button.setIcon(QtGui.QIcon("./images/pause-symbol.png"))
            self.play_status = True
        else:
            self.play_button.setIcon(QtGui.QIcon("./images/play-button.png"))
            self.play_status = False


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWin = main()
    mainWin.show()
    sys.exit( app.exec_() )
