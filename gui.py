# Author:           Andrew Derringer
# Last Modified:    4/2/2020
# Description:      PyQt5 application that generates customizable display of CAN data using MDF and DBC files.
#                   This application was made using data and specifications from Oregon State Univesity Global
#                   formula racing team.


from PyQt5 import QtWidgets, QtCore, QtGui
from asammdf import MDF

import numpy as np
import os
import sys
import time
import threading
import json

from Tab import Tab
from SteeringWheel import SteeringWheel
from Pedal import Pedal
from Worker import Worker
from LayoutPopup import LayoutPopup
from ImportPopup import ImportPopup


class main(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super(main, self).__init__(parent)

        self.channel_dict = {} # Dict of signals navigable by [group name][signal name]
        self.tab_list = [] # List of Tab class object currently displayed on GUI.
        self.mdf_extracted = None
        self.play_status = False # Play-button status to toggle between play and pause.

        self.workspace_file = ""
        self.dbc_path = ""
        self.mdf_path = ""

        # Apply startup characteristics for window.
        self.setWindowTitle("GFR Telemtry Data")
        self.setGeometry(0, 0, 1250, 750)

        # CentralWidget houses layout features within the app.
        self.centralWidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralWidget)

        # Section for adding toolbar drop-downs and subsections.
        self.buildToolbar()

        # Sections for placing all layouts and widgets.
        self.placeWidgets()

        # Holds instance of add tab popup.
        self.popup = None


    def popupTabLayout(self, prev_state=None, edit=None):
        # On "Add Tab" select generate Popup class object in seperate window. 
        self.popup = LayoutPopup(self.channel_dict, edit=edit)
        self.popup.main = self

        if type(prev_state) == Tab:
            self.popup.setTitle(prev_state.get_title())
            for plot in prev_state.get_plots():
                self.popup.addSignal(plot[0], plot[1])
        self.popup.show()


    def popupFileImport(self):
        self.popup = ImportPopup(self.dbc_path, self.mdf_path)
        self.popup.main = self
        self.popup.show()


    def buildToolbar(self):
        # Toolbar setup.
        tool_bar = self.menuBar() # Along top of screen.

        ##################################### File DropDown #######################################

        file_menu = tool_bar.addMenu("&File")

        # File drop down option - Import Data.
        import_data = QtGui.QAction("&Import Data", self)
        import_data.setShortcut("Ctrl+D")
        import_data.setStatusTip("Load mdf file and extract using dbc.")
        import_data.triggered.connect(self.popupFileImport)
        file_menu.addAction(import_data)

        file_menu.addSeparator()

        # File drop down option - Load Workspace.
        load_workspace = QtGui.QAction("&Load Workspace", self)
        load_workspace.setShortcut("Ctrl+W")
        load_workspace.setStatusTip("Load tab and graph setting from previous session.")
        load_workspace.triggered.connect(self.LoadWorkspace)
        file_menu.addAction(load_workspace)

        # File drop down option - Save Workspace.
        save_workspace = QtGui.QAction("&Save Workspace", self)
        save_workspace.setShortcut("Ctrl+S")
        save_workspace.setStatusTip("Save tab and graph setting for later use.")
        save_workspace.triggered.connect(self.saveWorkspace)
        file_menu.addAction(save_workspace)

        file_menu.addSeparator()

        # File drop down option - exit.
        exit_gui = QtGui.QAction("&Exit", self)
        exit_gui.setShortcut("Ctrl+Q")
        exit_gui.setStatusTip("&Leave the App")
        exit_gui.triggered.connect(self.closeApp)
        file_menu.addAction(exit_gui) 

        #################################### Layout DropDown ######################################

        layout_menu = tool_bar.addMenu("&Layout")

        # Layout drop down option - Add Display.
        add_tab = QtGui.QAction("&Add Display", self)
        add_tab.setShortcut("Ctrl+A")
        add_tab.setStatusTip("&Add tab with custom display")
        add_tab.triggered.connect(self.popupTabLayout)
        layout_menu.addAction(add_tab)

        # Layout drop down option - Edit Display.
        edit_tab = QtGui.QAction("&Edit Display", self)
        edit_tab.setShortcut("Ctrl+E")
        edit_tab.setStatusTip("&Edit selected tab Display.")
        edit_tab.triggered.connect(self.edit_display)
        layout_menu.addAction(edit_tab)

        # Layout drop down option - Remove Display.
        remove_tab = QtGui.QAction("&Remove Display", self)
        remove_tab.setShortcut("Ctrl+R")
        remove_tab.setStatusTip("&Remove Tab.")
        remove_tab.triggered.connect(self.close_display)
        layout_menu.addAction(remove_tab)


    def placeWidgets(self):

        ################################### Format Main Window ####################################

        # Create horizontal format for main widget subsections.
        self.horizontalSections = QtWidgets.QHBoxLayout()
        self.centralWidget.setLayout(self.horizontalSections)
        
        ################################ Main Window - Left Column ################################

        # Left subsection - Virtical Stacking Layout.
        self.left_vert_sec = QtWidgets.QVBoxLayout()
        self.horizontalSections.addLayout(self.left_vert_sec)

        # Button - "Add Tab".
        self.add_tab = QtWidgets.QPushButton("Add Tab")
        self.add_tab.clicked.connect(self.popupTabLayout)
        self.left_vert_sec.addWidget(self.add_tab)

        # Button - "Import Data".
        import_data = QtWidgets.QPushButton("Import Data")
        import_data.clicked.connect(self.popupFileImport)
        self.left_vert_sec.addWidget(import_data)

        # Collapsible Lists - Signals.
        self.channel_selectors = QtWidgets.QTreeWidget()
        # self.channel_selectors = CustomTree()
        # self.channel_selectors.setDragEnabled(True)
        # self.channel_selectors.setHeaderLabel("CAN Data")
        self.channel_selectors.setHeaderHidden(True)
        self.channel_selectors.setFixedWidth(200)
        self.left_vert_sec.addWidget(self.channel_selectors)

        ############################### Main Window - Middle Column ###############################

        # Middle subsection - Tabbed graphic data.
        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setMovable(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.horizontalSections.addWidget(self.tabs)

        ############################### Main Window - Right Column ################################

        # Right subsection - Virtical Stacking Layout.
        self.right_vert_sec = QtWidgets.QVBoxLayout()
        self.horizontalSections.addLayout(self.right_vert_sec)

        # Horizontal track buttons layout - Back-skip, play, pause, forward-skip.
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
        self.play_slider.setRange(0, 0)
        self.play_slider.valueChanged.connect(self.slider_moved)
        self.right_vert_sec.addWidget(self.play_slider)

        # Graphic - Steering Wheel
        self.steering_wheel = SteeringWheel(0)
        self.right_vert_sec.addWidget(self.steering_wheel)
        self.steering_wheel.setMaximumSize(200,200)

        # Horizontal Pedals layout - Brake and Gas
        self.pedal_horz_sec = QtWidgets.QHBoxLayout()
        self.right_vert_sec.addLayout(self.pedal_horz_sec)

        # Graphic - Brake Pedal
        self.brake_pedal = Pedal(max_y=10000)
        self.pedal_horz_sec.addWidget(self.brake_pedal)
        self.brake_pedal.setMaximumSize(100, 100)

        # Graphic - Gas Pedal
        self.gas_pedal = Pedal(max_y=100)
        self.pedal_horz_sec.addWidget(self.gas_pedal)
        self.gas_pedal.setMaximumSize(100, 100)


    def closeApp(self):
        # On "File Dropdown - Exit" select exit program.
        sys.exit()


    def setDataFiles(self, dbc="", mdf=""):
        self.dbc_path = dbc
        self.mdf_path = mdf


    def extractMDF(self):
        # Get user selected MDF file path and make extracted MDF object.
        mdf_obj = MDF(self.mdf_path) 
        self.mdf_extracted = mdf_obj.extract_can_logging([self.dbc_path])

        # Group names only exist in comment formatted as CAN#.group.signal.
        # Populate channel_dict by channel_dict[group] = [{signal: signal_object}, ...]
        for sig in self.mdf_extracted.iter_channels():
            for word in sig.comment.split():
                if word[0] != '<':
                    s = word.split(".")
                    if s[1] not in self.channel_dict:
                        self.channel_dict[s[1]] = {s[2]: sig}
                    else:
                        self.channel_dict[s[1]][s[2]] = sig
        
        # Populate tree widget with groups and signals.
        for group, signals in self.channel_dict.items():
            parent = QtWidgets.QTreeWidgetItem(self.channel_selectors, [group])
            for sig in signals:
                child = QtWidgets.QTreeWidgetItem(parent)
                child.setText(0, sig)

        # Render any graphs already present and grab data for pedals.
        self.render_graphs()
        self.load_pedal_data()
        self.load_steering_wheel()
    

    def load_pedal_data(self):
        # inter_x = [x * 0.1 for x in range(0, int(x[-1]))]
        # After MDf extracted store brake and gas pedal data in pedal object variables.
        brake_signal = self.mdf_extracted.get("BrkPres_Front")
        x = brake_signal.timestamps
        y = brake_signal.samples
        # inter_x = list(range(0, int(x[-1]), 0.1))
        inter_x = [x * 0.1 for x in range(0, int(x[-1]) * 10)]
        self.brake_pressure = np.interp(inter_x, x, y) # Interpolate to match play slider values.

        accel_signal = self.mdf_extracted.get("APPS1")
        x = accel_signal.timestamps
        y = accel_signal.samples
        # inter_x = list(range(0, int(x[-1]), 0.1))
        inter_x = [x * 0.1 for x in range(0, int(x[-1]) * 10)]
        self.accel_pressure = np.interp(inter_x, x, y)


    def load_steering_wheel(self):
        sta = self.mdf_extracted.get("STA")
        x = sta.timestamps
        y = sta.samples
        # inter_x = list(range(0, int(x[-1]), 0.1))
        inter_x = [x * 0.1 for x in range(0, int(x[-1]) * 10)]
        self.sta = np.interp(inter_x, x, y)


    def render_graphs(self):
        # If MDF loaded iterate through tabs and render each plot onto their graphs.
        if self.mdf_extracted != None:
            # Delete old tab wigets. Redraw leads to ugly behavior.
            for i in reversed(range(self.tabs.count())):
                self.tabs.removeTab(i)
            new_tabs = []
            # Create new tab widgets, add to new tab list.
            for tab_obj in self.tab_list:
                newTab = Tab(tab_obj.get_title(), self.play_slider)
                for plot in tab_obj.get_plots():
                    group = plot[0]
                    signal = plot[1]
                    try:
                        mdf_obj = self.channel_dict[group][signal]
                        if mdf_obj is not None:
                            newTab.add_plot(group, signal, mdf_obj.timestamps, mdf_obj.samples, mdf_obj.unit)
                    except Exception:
                        newTab.add_plot(group, signal)
                self.tabs.addTab(newTab.get_tab_widget(), newTab.get_title())
                new_tabs.append(newTab)
                newTab.render_multiplot()

            # Replace old tab list with new and redraw features.
            self.tab_list.clear()
            self.tab_list = new_tabs
            self.redraw_slider()


    def redraw_slider(self):
        max_timestamp = 0
        # Find the largest timestamp value to set slider range.
        for tab_obj in self.tab_list:
            if tab_obj.get_max_timestamp() > max_timestamp:
                max_timestamp = tab_obj.get_max_timestamp()
        self.play_slider.setRange(0, max_timestamp * 10) # Redraw slider.


    def redraw_graphics(self):
        i = self.play_slider.value()

        # Redraw brake_pedal.
        if i >= len(self.brake_pressure): # If slider value exceeds index range, set to max index.
            i = len(self.brake_pressure) - 1
        pressure = int(self.brake_pressure[i])
        if pressure > self.brake_pedal.get_max(): # If value exceeds graphic calculations set to max value.
            pressure = self.brake_pedal.get_max()
        self.brake_pedal.set_pressure(pressure) # Redraw.

        # The same process applied to gas_pedal.
        if i >= len(self.accel_pressure):
            i = len(self.accel_pressure) - 1
        pressure = int(self.accel_pressure[i]) - 200
        if pressure > self.gas_pedal.get_max():
            pressure = self.gas_pedal.get_max()
        self.gas_pedal.set_pressure(pressure)

        # The same process applied to steering_wheel.
        if i >= len(self.sta):
            i = len(self.sta) - 1
        self.steering_wheel.setSTA(self.sta[i])


    def slider_moved(self):
        # Iterate over tab objects and change their display line location to match the slider's value.
        print(self.play_slider.value())
        for tab_obj in self.tab_list:
            new_x = self.play_slider.value() / 10
            tab_obj.set_selected_x(new_x)

        # Redraw pedals to match new slider timestamp.
        self.redraw_graphics()
        

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


    def saveWorkspace(self):
        # On "Export Workspace" select get essential data from tab_list and save to JSON. 
        file_path = QtGui.QFileDialog.getSaveFileName(self, "Export Workspace", os.getcwd() + "/" + self.workspace_file, "JSON (*.json)")

        # Saved to dict formatted tab_data[tab title] = {group: [signal, ...], ...}
        tab_data = {}
        for tab in self.tab_list:
            title = tab.get_title()
            tab_data[title] = {}
            for plot in tab.get_plots():
                group = plot[0]
                signal = plot[1]
                if group not in tab_data[title]:
                    tab_data[title][group] = [signal]
                else:
                    tab_data[title][group].append(signal)
        
        # Write to file.
        try:
            with open(file_path[0], 'w') as fd:
                fd.write(json.dumps(tab_data, sort_keys=True, indent=4))
                fd.close()
            self.workspace_file = os.path.split(file_path[0])[1]
            print(self.workspace_file)
        except Exception:
            pass


    def LoadWorkspace(self):
        # On "Import Workspace" load JSON and generate tab objects in tab_list.
        file_path = QtWidgets.QFileDialog.getOpenFileName(self, 'Import Workspace', os.getcwd() + "/" + self.workspace_file, "JSON (*.json)")
 
        try:
            with open(file_path[0]) as fd:

                # Remove any old tabs. Clean slate.
                for i in reversed(range(self.tabs.count())):
                    self.tabs.removeTab(i)
                self.tab_list.clear()

                # Generate new tabs.
                tab_data = json.load(fd)
                for tab, groups in tab_data.items():
                    new_tab = Tab(tab, self.play_slider)
                    new_tab.add_plots(groups)
                    new_tab.render_multiplot()

                    self.tabs.addTab(new_tab.get_tab_widget(), new_tab.get_title())
                    self.tab_list.append(new_tab)
            self.workspace_file = os.path.split(file_path[0])[1]
        except Exception:
            pass
        
        # Display data immediately upon upload if MDF already uploaded.
        self.render_graphs()
        

    def close_tab(self, i):
        self.tab_list.pop(i)
        self.tabs.removeTab(i)
        self.redraw_slider()


    def close_display(self):
        self.close_tab(self.tabs.currentIndex())


    def edit_display(self):
        if len(self.tab_list) > 0:
            tab = self.tab_list[self.tabs.currentIndex()]
            self.popupTabLayout(prev_state=tab, edit=True)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWin = main()
    mainWin.show()
    sys.exit( app.exec_() )
