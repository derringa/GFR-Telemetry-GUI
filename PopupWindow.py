from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.Qt import Qt
from asammdf import MDF

import numpy as np
import sys

from Tab import Tab


MAX_PLOTS = 7

class Popup(QtWidgets.QMainWindow):
    
    main = None

    def __init__(self, signalList=None, addedList=None, parent=None):
        super(Popup, self).__init__(parent)

        self._signalList = signalList
        self._addedList = addedList

        if self._signalList is None:
            self._signalList = {}
        if self._addedList is None:
            self._addedList = []

        self.place_widgets()


    def place_widgets(self):
        self.setWindowTitle("Add Tab")
        centralWidget = QtWidgets.QWidget()
        self.setCentralWidget(centralWidget)

        tabForm = QtWidgets.QFormLayout()
        tabForm.addRow(QtWidgets.QLabel("Tab Features:"))

        self.title = QtWidgets.QLineEdit()
        tabForm.addRow(QtWidgets.QLabel("Title:"), self.title)

        typeDropDown = QtWidgets.QComboBox()
        typeDropDown.addItem("Multi-Y Plot")
        tabForm.addRow(QtWidgets.QLabel("Type:"), typeDropDown)

        tabForm.addRow(QtWidgets.QLabel("Signals"))
        tabForm.addRow(QtWidgets.QLabel("Add:"), QtWidgets.QLabel("Remove:"))

        self.addBox = QtWidgets.QTreeWidget()
        self.addBox.setHeaderLabel("Available Signals")
        self.populate_tree(self.addBox, self._signalList)
        self.addBox.itemDoubleClicked.connect(self.add_signal)

        self.removeBox = QtWidgets.QTreeWidget()
        self.removeBox.setHeaderLabel("Applied Signals")
        self.populate_tree(self.removeBox, self._addedList)
        self.removeBox.itemDoubleClicked.connect(self.remove_signal)

        tabForm.addRow(self.addBox, self.removeBox)

        self.customSignal = QtWidgets.QLineEdit()
        self.customSignal.returnPressed.connect(self.add_custom_signal)
        customAdd = QtWidgets.QPushButton("Add")
        customAdd.clicked.connect(self.add_custom_signal)
        
        customLayout = QtWidgets.QHBoxLayout()
        customLayout.addWidget(self.customSignal)
        customLayout.addWidget(customAdd)
        tabForm.addRow(QtWidgets.QLabel("Custom Signal:"), customLayout)

        submit = QtWidgets.QPushButton("Submit")
        submit.clicked.connect(self.generate_tab)

        cancel = QtWidgets.QPushButton("Cancel")
        cancel.clicked.connect(self.close)

        tabForm.addRow(submit, cancel)
        centralWidget.setLayout(tabForm)


    def populate_tree(self, tree, signals):
        if type(signals) is dict:
            for (key, value) in signals.items():
                parent = QtWidgets.QTreeWidgetItem(tree, [key])
                parent.setFlags(parent.flags() & ~Qt.ItemIsSelectable)
                for sig in value:
                    child = QtWidgets.QTreeWidgetItem(parent)
                    child.setText(0, sig)
                    if sig in self._addedList:
                        # child.setFlags(child.flags() & ~Qt.ItemIsSelectable)
                        # child.setForeground(0, QtGui.QColor('gray'))
                        child.setBackground(0, QtGui.QColor('gray'))
                    # child.setCheckState(0, Qt.Unchecked)
        else:
            for sig in signals:
                child = QtWidgets.QTreeWidgetItem(tree)
                child.setText(0, sig)
                # child.setCheckState(0, Qt.Unchecked)


    def add_signal(self, obj, col):
        if obj.text(col) not in self._addedList and len(self._addedList) <= MAX_PLOTS:
            self._addedList.append(obj.text(col))
            child = QtWidgets.QTreeWidgetItem(self.removeBox)
            child.setText(0, obj.text(col))
            obj.setBackground(0, QtGui.QColor('gray'))


    def remove_signal(self, obj, col):
        # itr = QtWidgets.QTreeWidgetItemIterator(self.addBox)
        # while itr.value():
        #     if itr.value().text(0) == obj.text(col):
        #         itr.value().setBackground(0, QtGui.QColor('white'))
        #         break
        #     else:
        #         itr += 1
        
        addBox_item = self.get_item(self.addBox, obj.text(col))
        if addBox_item is not None:
            print("Changing back to white!")
            addBox_item.setBackground(0, QtGui.QColor('white'))

        self._addedList.remove(obj.text(col))
        self.removeBox.takeTopLevelItem(self.removeBox.indexOfTopLevelItem(obj))


    def add_custom_signal(self):
        # print(self.customSignal.text())
        if len(self._addedList) <= MAX_PLOTS and self.customSignal.text() not in self._addedList and self.customSignal.text() != "":
            self._addedList.append(self.customSignal.text())
            child = QtWidgets.QTreeWidgetItem(self.removeBox)
            child.setText(0, self.customSignal.text())

        addBox_item = self.get_item(self.addBox, self.customSignal.text())
        if addBox_item is not None:
            addBox_item.setBackground(0, QtGui.QColor('gray'))

        self.customSignal.clear()


    def get_item(self, widget, item_text):
        itr = QtWidgets.QTreeWidgetItemIterator(widget)
        while itr.value():
            if itr.value().text(0) == item_text:
                return itr.value()
            itr += 1
        return None


    def generate_tab(self):
        self.error_window = QtWidgets.QErrorMessage()
        error_count = 0
        message = ""
        if self.title.text() == "":
            error_count += 1
            message += "ERROR {}: You must enter a title.".format(error_count)
        if len(self._addedList) == 0:
            error_count += 1
            message += "ERROR {}: You must apply at least one signal.".format(error_count)
        
        if error_count > 0:
            self.error_window.showMessage(message)
        else:
            newTab = Tab(self.title.text(), self.main.play_slider)
            newTab.add_plots(self._addedList)
            newTab.render_multiplot()
            self.main.tabs.addTab(newTab.get_tab_widget(), newTab.get_title())
            self.main.tab_list.append(newTab)
            self.main.render_graphs()
            self.close()