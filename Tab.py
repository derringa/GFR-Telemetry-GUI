# Author:           Andrew Derringer
# Last Modified:    1/17/2020
# Description:      Tab class is build for pyqt5 to generate a tab object that is passed necessary information
#                   to plot graph without standard behavior of creating another application window.

import itertools
import pyqtgraph
from PyQt5 import QtWidgets


class Tab:

    def __init__(self, sensor_name, x_vals, y_vals):
        # Tab data variables.
        self.title = sensor_name # Saved to apply as widget title in pyqt application.
        self.x = x_vals # Applied to x-axis of pyqtplot.
        self.y = y_vals # Applied to y-axis of pyqtplot.

        # Declare pyqt widgets needed to build graphing tab.
        self.tab = QtWidgets.QWidget()
        self.graph = pyqtgraph.PlotWidget()
        self.layout = QtWidgets.QVBoxLayout()

        # Combine pyqt objects.
        self.layout.addWidget(self.graph)
        self.tab.setLayout(self.layout)

        # Plot graph within the tab.
        self.graph.plot(self.x, self.y)
