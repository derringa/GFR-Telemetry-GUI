# Author:           Andrew Derringer
# Last Modified:    1/17/2020
# Description:      PyQt5 application that generates customizable display of CAN data using MDF and DBC files.
#                   This application was made using data and specifications from Oregon State Univesity Global
#                   formula racing team.

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.Qt import Qt
from asammdf import MDF
import numpy as np
from numpy import sin, cos, pi
from enum import Enum
import sys
import pyqtgraph
from pyqtgraph import PlotWidget, plot
from Tab import Tab
from Worker import Worker
import time
import threading


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

        self.curr_tabs = [] # List of Tab class object currently present and displayed on GUI.
        self.channel_list = [] # List of channel names desired by user on next plot update.
        self.mdf_list = [] # List of available channels in MDF to crossreference with the DBC checklist.
        self.play_status = False # Play-button status to toggle between play and pause.

        # Apply startup characteristics for window.
        self.setWindowTitle("GFR Telemtry Data")
        self.setGeometry(0, 0, 1250, 750)

        # centralWidget houses layout features within the app.
        self.centralWidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralWidget)

        # Section for adding toolbar sections and subsections.
        self.build_toolbar()

        # Sections for placing all layouts and widgets.
        self.place_widgets()

        # holds instance of add tab popup so that its data.
        # is not cleaned up immediately upon close.
        self.popup = None


    # def tab_window(self):
    #     self.popup = popupWindow()
    #     self.popup.main = self
    #     self.popup.show()


    # def add_tab(self, item):
    #     #item.updateData(self.hour, self.temperature)
    #     self.tabs.addTab(item.tab, item.title)


    def build_toolbar(self):
        # Toolbar setup.
        self.statusBar() # Along bottom of screen.
        mainMenu = self.menuBar() # Along top of screen.

        # File drop down.
        fileMenu = mainMenu.addMenu("&File")

        # File drop down option - exit.
        extractAction = QtGui.QAction("&Exit", self)
        extractAction.setShortcut("Ctrl+Q") # Set key-board shortcut.
        extractAction.setStatusTip("&Leave the App")
        extractAction.triggered.connect(self.close_application)
        fileMenu.addAction(extractAction)  # add to file drop down.

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

        # Create horizontal format for main widget subsections.
        self.horizontalSections = QtWidgets.QHBoxLayout()
        self.centralWidget.setLayout(self.horizontalSections)
        
        ################################ Main Window - Left Column ################################

        # Left subsection - Virtical Stacking Layout.
        self.left_vert_sec = QtWidgets.QVBoxLayout()
        self.horizontalSections.addLayout(self.left_vert_sec)

        # Button - "Load DBC file".
        self.upload_dbc_file = QtWidgets.QPushButton("Load DBC File")
        self.upload_dbc_file.clicked.connect(self.load_dbc_file)
        self.left_vert_sec.addWidget(self.upload_dbc_file)

        # Button - "Load MDF file".
        self.upload_mdf_file = QtWidgets.QPushButton("Load MDF File")
        self.upload_mdf_file.setEnabled(False)
        self.upload_mdf_file.clicked.connect(self.load_mdf_file)
        self.left_vert_sec.addWidget(self.upload_mdf_file)

        #Channels - Checkbox list.
        self.channel_selectors = QtWidgets.QTreeWidget()
        self.channel_selectors.setHeaderHidden(True)
        self.channel_selectors.setFixedWidth(300)
        self.channel_selectors.itemChanged.connect(self.check_event)
        self.left_vert_sec.addWidget(self.channel_selectors)

        # Button - "Plot channels".
        self.plot_channels = QtWidgets.QPushButton("Plot Channels")
        self.plot_channels.setEnabled(False)
        self.plot_channels.clicked.connect(self.post_load_plots)
        self.left_vert_sec.addWidget(self.plot_channels)

        ############################### Main Window - Middle Column ###############################

        # Middle subsection - Tabbed graphic data.
        self.tabs = QtWidgets.QTabWidget()
        self.horizontalSections.addWidget(self.tabs)

        ############################### Main Window - Right Column ################################

        # Right subsection - Virtical Stacking Layout.
        self.right_vert_sec = QtWidgets.QVBoxLayout()
        self.horizontalSections.addLayout(self.right_vert_sec)

        # Horizontal Buttons layout - Back-skip, play, pause, forward-skip.
        self.play_horz_sec = QtWidgets.QHBoxLayout()
        self.right_vert_sec.addLayout(self.play_horz_sec)
   
        # Button - Track-Back.
        self.back_button = QtWidgets.QPushButton()
        self.back_button.setIcon(QtGui.QIcon("./images/rewind-button.png"))
        self.back_button.clicked.connect(self.track_back_buttons)
        self.play_horz_sec.addWidget(self.back_button)
    
        # Button - Play/Pause.
        self.play_button = QtWidgets.QPushButton()
        self.play_button.setIcon(QtGui.QIcon("./images/play-button.png"))
        self.play_button.clicked.connect(self.play_pause_toggle)
        self.play_horz_sec.addWidget(self.play_button)
     
        # Button - Track-Forward.
        self.forward_button = QtWidgets.QPushButton()
        self.forward_button.setIcon(QtGui.QIcon("./images/fast-forward-arrows.png"))
        self.forward_button.clicked.connect(self.track_forward_buttons)
        self.play_horz_sec.addWidget(self.forward_button)

        # Slider - Time Sequence
        self.play_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.play_slider.setFixedWidth(300)
        self.play_slider.valueChanged.connect(self.slider_moved)
        self.right_vert_sec.addWidget(self.play_slider)


    def close_application(self):
        print("Good-Bye!")
        sys.exit()


    def load_mdf_file(self):
        # Get user selected MDF file path and make MDF object.
        mf4_path = QtWidgets.QFileDialog.getOpenFileName(self, 'Select file', 'c:\\', "MDF (*.mf4)")
        mdf_obj = MDF(mf4_path[0]) 
        self.mdf_extracted = mdf_obj.extract_can_logging([self.dbc_path[0]]) # Extract data with dbc file path.

        # Collect name of all channels from MDF into a list.
        for ch in self.mdf_extracted:
            self.mdf_list.append(ch.name)

        # Delete any channel listed in DBC not also present in MDF list.
        delete_channels = []
        itr = QtWidgets.QTreeWidgetItemIterator(self.channel_selectors)
        while itr.value():
            if itr.value().childCount() == 0 and itr.value().text(0) not in self.mdf_list:
                delete_channels.append(itr.value())
            itr += 1
        for ch in delete_channels:
            parent = ch.parent()
            parent.removeChild(ch)
            
        # Activate the Plot Channel button only after MDF file is loaded and operated on.
        self.plot_channels.setEnabled(True)


    def load_dbc_file(self):
        self.dbc_path = QtWidgets.QFileDialog.getOpenFileName(self, 'Select file', 'c:\\', "DBC (*.dbc)")

        # Open file and add channel name to list under conditions.
        with open(self.dbc_path[0], 'r') as fd:
            group_dict = {}
            curr_group = ''
            for line in fd:
                line_list = line.split(None, 5) # Grab first 5 space delimited strings.
                if not line_list: # Disregard empty lines.
                    continue
                elif line_list[0] == 'BO_': # Grab channel group name.
                    curr_group = line_list[4]
                elif line_list[0] == 'SG_': # Grab channel names.
                    if group_dict.get(curr_group) == None: # If channel group not present then add.
                        group_dict[curr_group] = [line_list[1]]
                    else: # Else append new channel to existing group.
                        group_dict[curr_group].append(line_list[1])

            # Make tree widget items from dict.
            for (key, value) in group_dict.items():
                parent = QtWidgets.QTreeWidgetItem(self.channel_selectors, [key])
                for ch_name in value:
                    child = QtWidgets.QTreeWidgetItem(parent)
                    child.setText(0, ch_name)
                    child.setCheckState(0, Qt.Unchecked)

            fd.close()

        # Activate the Load MF4 File button only after DBC file is loaded and operated on.
        self.upload_mdf_file.setEnabled(True)
    

    def check_event(self, item, column):
        if item.checkState(column) == Qt.Unchecked:
            self.channel_list[:] = [ch for ch in self.channel_list if ch != item.text(0)]
        else:
            self.channel_list.append(item.text(0))


    def post_load_plots(self):
        displayed_tabs = []

        # Iterate through tabs and if no longer on desired channel list then remove them else add to current tabs list.
        for i in reversed(range(self.tabs.count())):
            tab_name = self.tabs.tabText(i)
            if tab_name not in self.channel_list: # If not present then remove tab and it's graph widget.
                self.tabs.removeTab(i) 
                self.curr_tabs[:] = [x for x in self.curr_tabs if x.get_title() != tab_name]
            else: # Else add to already displayed_tabs list.
                displayed_tabs.append(tab_name)

        # If channel doesn't have a tab then create tab with graph.
        for ch in self.channel_list:
            if ch not in displayed_tabs:
                ch_obj = self.mdf_extracted.get(ch)
                new_tab = Tab(ch, ch_obj.timestamps, ch_obj.samples, self.play_slider)
                self.curr_tabs.append(new_tab)
                self.tabs.addTab(new_tab.get_tab_widget(), new_tab.get_title())

        # Redraw slider's characteristics to new set of tabs and graphs.
        self.redraw_slider()


    def redraw_slider(self):
        max_timestamp = 0
        # Find the largest timestamp value to set slider range.
        for tab_obj in self.curr_tabs:
            if tab_obj.get_max_timestamp() > max_timestamp:
                max_timestamp = tab_obj.get_max_timestamp()
        self.play_slider.setRange(0, max_timestamp) # Redraw slider.


    def slider_moved(self):
        # Iterate over tab objects and change their display line location to match the slider's value.
        for tab_obj in self.curr_tabs:
            tab_obj.set_selected_x(self.play_slider.value())
        

    def generate_play_thread(self):
        # Declare and connect worker to thread process.
        self.worker = Worker()
        self.thread = QtCore.QThread(parent=self)
        self.worker.moveToThread(self.thread)

        # Assign methods for thread process and signaling to the GUI.
        self.thread.started.connect(self.worker.increment_track) # Run increment_track worker method on start.
        self.worker.intReady.connect(self.iterate_play) # When work intReady signal propogated call GUI iterate_play method.

        self.thread.start()


    def kill_play_thread(self):
        # When pause button is hit this is called from play_pause_toggle to kills the play thread process.
        self.worker.kill()


    def iterate_play(self, one_tick):
        # When thread process propogated intReady signal to GUI this process is called.
        self.play_slider.setValue(self.play_slider.value() + one_tick)


    def play_pause_toggle(self):
        # If paused then begin playing, status to true, change button icon to pause, and start a play thread.
        if self.play_status == False:
            self.play_status = True
            self.play_button.setIcon(QtGui.QIcon("./images/pause-symbol.png"))
            self.generate_play_thread()
        else: # Else kill thread to stop play process and change button icon to play.
            self.play_status = False
            self.play_button.setIcon(QtGui.QIcon("./images/play-button.png"))
            self.kill_play_thread()


    def track_back_buttons(self):
        # Go backward 10 ticks.
        self.play_slider.setValue(self.play_slider.value() - 10)


    def track_forward_buttons(self):
        # Go forward 10 ticks.
        self.play_slider.setValue(self.play_slider.value() + 10)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWin = main()
    mainWin.show()
    sys.exit( app.exec_() )
