# Author:           Andrew Derringer
# Last Modified:    3/28/2020
# Description:      PyQt5 application that generates a popup window allowing the user to create and customize
#                   a Tab class object graph with multi-plot data.


from PyQt5 import QtWidgets, QtCore, QtGui

from Tab import Tab


MAX_PLOTS = 7


class LayoutPopup(QtWidgets.QMainWindow):
    
    main = None

    def __init__(self, signalList=None, addedDict=None, parent=None, edit=None):
        super(LayoutPopup, self).__init__(parent)

        self.signal_dict = signalList # Dict of available signals to add.
        self.added_dict = addedDict # Dict of signals already selected to plot.
        self.plot_count = 0
        self.edit = edit

        if self.signal_dict is None:
            self.signal_dict = {}
        if self.added_dict is None:
            self.added_dict = {}

        self.placeWidgets()


    def placeWidgets(self):
        self.setWindowTitle("Add Tab")
        centralWidget = QtWidgets.QWidget()
        self.setCentralWidget(centralWidget)

        ################################## Grid Layout - Sizing ###################################

        grid = QtWidgets.QGridLayout()
        centralWidget.setLayout(grid)

        grid.setVerticalSpacing(5)
        grid.setRowStretch(5, 1)
        grid.setColumnStretch(1, 0)
        grid.setColumnStretch(2, 1)
        grid.setColumnStretch(3, 0)
        grid.setColumnStretch(4, 0)
        grid.setColumnStretch(5, 2)
        grid.setColumnStretch(6, 0)
        grid.setColumnStretch(7, 1)
        grid.setColumnStretch(8, 2)
        grid.setColumnStretch(9, 0)
        grid.setColumnStretch(10, 0)

        grid.setColumnMinimumWidth(2, 200)
        grid.setColumnMinimumWidth(7, 200)

        ################################ Grid Layout - Top Section ################################

        grid.addWidget(QtWidgets.QLabel("Tab Features:"), 1, 1, 1, 1)

        # Tab Title Field.
        grid.addWidget(QtWidgets.QLabel("Title:"), 2, 1, 1, 1)
        self.title = QtWidgets.QLineEdit()
        self.title.setMaximumWidth(300)
        grid.addWidget(self.title, 2, 2, 1, 2)

        # Tab Type Dropdown.
        grid.addWidget(QtWidgets.QLabel("Type:"), 3, 1, 1, 1)
        self.type_select = QtWidgets.QComboBox()
        self.type_select.setMaximumWidth(150)
        self.type_select.addItem("Multi-Y Plot")
        grid.addWidget(self.type_select, 3, 2, 1, 2)

        ############################## Grid Layout - Middle Section ###############################

        grid.addWidget(QtWidgets.QLabel("Signal Select:"), 4, 1, 1, 1)

        # Tree Widget of Available Signals.
        self.add_box = QtWidgets.QTreeWidget()
        self.add_box.setHeaderLabel("Available Signals")
        self.populateTree(self.add_box, self.signal_dict)
        self.add_box.itemDoubleClicked.connect(self.existingSignal)
        grid.addWidget(self.add_box, 5, 1, 1, 5)

        # Tree Widget of Selected Signals.
        self.remove_box = QtWidgets.QTreeWidget()
        self.remove_box.setHeaderLabel("Applied Signals")
        self.populateTree(self.remove_box, self.added_dict)
        self.remove_box.itemDoubleClicked.connect(self.removeSignal)
        grid.addWidget(self.remove_box, 5, 6, 1, 5)

        ############################### Grid Layout - Bottom Section ##############################

        grid.addWidget(QtWidgets.QLabel("Custom Plot:"), 6, 1, 1, 1)

        # Custom Plot - Group Name Field.
        grid.addWidget(QtWidgets.QLabel("Group:"), 7, 1, 1, 1)
        self.group = QtWidgets.QLineEdit()
        self.group.setMaximumWidth(400)
        grid.addWidget(self.group, 7, 2, 1, 2)

        # Custom Plot - Signal Name Field.
        grid.addWidget(QtWidgets.QLabel("Signal:"), 8, 1, 1, 1)
        self.signal = QtWidgets.QLineEdit()
        self.signal.setMaximumWidth(400)
        grid.addWidget(self.signal, 8, 2, 1, 2)

        # Apply Custom Plot Button.
        apply_plot = QtWidgets.QPushButton("Apply")
        apply_plot.setFixedWidth(65)
        apply_plot.clicked.connect(self.customSignal)
        grid.addWidget(apply_plot, 8, 4, 1, 1)

        # Submit Tab Button.
        tab_submit = QtWidgets.QPushButton("Submit")
        tab_submit.setFixedWidth(65)
        tab_submit.clicked.connect(self.generateTab)
        grid.addWidget(tab_submit, 8, 9, 1, 1)

        # Cancel Tab Button.
        tab_cancel = QtWidgets.QPushButton("Cancel")
        tab_cancel.setFixedWidth(65)
        tab_cancel.clicked.connect(self.close)
        grid.addWidget(tab_cancel, 8, 10, 1, 1)


    def populateTree(self, tree, signals):
        for group, signals in signals.items():
            parent = QtWidgets.QTreeWidgetItem(tree, [group])
            parent.setFlags(parent.flags() & ~QtCore.Qt.ItemIsSelectable)
            for sig in signals:
                child = QtWidgets.QTreeWidgetItem(parent)
                child.setText(0, sig)
                if group in self.added_dict and sig in self.added_dict[group]:
                    child.setBackground(0, QtGui.QColor('gray'))


    def existingSignal(self, obj, col):
        # On signals add_box item double click send group and signal name to addSignal.

        # Ignore clicks on group name rows.
        if obj.childCount() != 0:
            return

        sig_name = obj.text(col)
        grp_name = obj.parent().text(0)

        self.addSignal(grp_name, sig_name)


    def removeSignal(self, child, col):
        # On signals remove_box item double click remove signal and restore in add_box.

        # Ignore clicks on group name rows.
        if child.childCount() != 0:
            return

        sig_name = child.text(col)
        parent = child.parent()
        grp_name = parent.text(0)

        # Find equivalent item in add_box and restore white background.
        add_item = self.getItem(self.add_box, grp_name, sig_name)
        if add_item is not None:
            add_item.setBackground(0, QtGui.QColor('white'))

        # Remove from dict, remove signal row, and if group empty then remove group dropdown.
        self.added_dict[grp_name].remove(sig_name)
        parent.removeChild(child)
        if len(self.added_dict[grp_name]) == 0:
            self.added_dict.pop(grp_name)
            self.remove_box.takeTopLevelItem(self.remove_box.indexOfTopLevelItem(parent))

        self.plot_count -= 1
        

    def customSignal(self):
        grp_name = self.group.text()
        sig_name = self.signal.text()

        if grp_name == "" or sig_name == "":
            self.error_window = QtWidgets.QErrorMessage()
            self.error_window.showMessage("ERROR: Both group and signal must be provided.")
        else:
            self.addSignal(grp_name, sig_name)
            self.group.clear()
            self.signal.clear()


    def addSignal(self, grp_name, sig_name, obj=None):
        # Add signal to added_dict if not already present.
        if grp_name not in self.added_dict and self.plot_count <= MAX_PLOTS:
            self.added_dict[grp_name] = [sig_name]
        elif sig_name not in self.added_dict[grp_name] and self.plot_count <= MAX_PLOTS:
            self.added_dict[grp_name].append(sig_name)
        else:
            return

        # If group already in remove_box then just add child row, else add dropdown for group.
        parent = self.getItem(self.remove_box, grp_name)
        if parent == None:
            parent = QtWidgets.QTreeWidgetItem(self.remove_box)
            parent.setText(0, grp_name)
            parent.setFlags(parent.flags() & ~QtCore.Qt.ItemIsSelectable)


        child = QtWidgets.QTreeWidgetItem(parent)
        child.setText(0, sig_name)
        item = self.getItem(self.add_box, grp_name, sig_name)
        if item is not None:
            item.setBackground(0, QtGui.QColor('gray')) # Apply gray background to already selected signals.
        self.plot_count += 1


    def getItem(self, widget, group=None, signal=None):
        # Iterate through tree items, look for group and then for signal by names and return.
        itr = QtWidgets.QTreeWidgetItemIterator(widget)
        while itr.value():
            if itr.value().text(0) == group:
                if signal == None: # If signal name not provided just return group item.
                    return itr.value()
                else:
                    sub_itr = QtWidgets.QTreeWidgetItemIterator(itr.value())
                    while sub_itr.value():
                        if sub_itr.value().text(0) == signal:
                            return sub_itr.value() # Else return signal item.
                        sub_itr += 1
            itr += 1
        return None


    def setTitle(self, title):
        self.title.setText(title)


    def generateTab(self):
        self.error_window = QtWidgets.QErrorMessage()
        error_count = 0
        message = ""
        tab_idx = -1

        # Check empty fields.
        if self.title.text() == "":
            error_count += 1
            message += "ERROR {}: You must enter a title.".format(error_count)
        if len(self.added_dict) == 0:
            error_count += 1
            message += "ERROR {}: You must apply at least one signal.".format(error_count)

        # Check if tab name unique. If no check if intent is to edit,
        if self.title.text() in [tab.get_title() for tab in self.main.tab_list]:
            if self.edit == True:
                tab_idx = [idx if self.title.text() == tab.get_title() else -1 for idx, tab in enumerate(self.main.tab_list)]
                tab_idx = tab_idx[0]
            else:
                error_count += 1
                message += "ERROR {}: Tab title \"{}\" is already taken.".format(error_count, self.title.text())

        # If errors then present else add tab to main window and close.
        if error_count > 0:
            self.error_window.showMessage(message)
        else:
            newTab = Tab(self.title.text(), self.main.play_slider)
            newTab.add_plots(self.added_dict)
            newTab.render_multiplot()

            # If editing delete old tab and replace with new at same index. Else append.
            if tab_idx != -1:
                self.main.tabs.removeTab(tab_idx)
                self.main.tabs.insertTab(tab_idx, newTab.get_tab_widget(), newTab.get_title())
                self.main.tab_list.pop(tab_idx)
                self.main.tab_list.insert(tab_idx, newTab)
            else:
                self.main.tabs.addTab(newTab.get_tab_widget(), newTab.get_title())
                self.main.tab_list.append(newTab)

            self.main.render_graphs()
            self.close()