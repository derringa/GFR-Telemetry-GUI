import itertools
import pyqtgraph
import time
from PyQt5 import QtWidgets, QtCore, QtGui
#from QtWidgets import QApplication, QMainWindow, QWidget, QGroupBox, QSlider, QLabel, QVBoxLayout, QHBoxLayout, \
    #QPushButton, QFormLayout, QGridLayout, QTabWidget


class Tab:

    #id_iter = itertools.count()

    def __init__(self, sensor_name, x_vals, y_vals):
        #self.id = next(Tab.id_iter)
        self.title = sensor_name
        self.tab = QtWidgets.QWidget()

        self.graph = pyqtgraph.PlotWidget()
        #self.timeStamp = "00:00:00"
        self.x = x_vals
        self.y = y_vals

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.graph)
        self.graph.plot(self.x, self.y)
        self.tab.setLayout(layout)

    # def updateData(self, newX, newY):
    #     self.x.extend(newX)
    #     self.y.extend(newY)
    #     self.x = newX
    #     self.y = newY
    #     self.graph.plot(self.x, self.y)

    # def updateTimeStamp(self, newTime):
    #     self.timeStamp = newTime


