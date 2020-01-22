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
        self._x = x_vals # Applied to x-axis of pyqtplot.
        self._y = y_vals # Applied to y-axis of pyqtplot.
        self.title = sensor_name # Saved to apply as widget title in pyqt application.
        self.selected_x = None

        # Declare pyqt widgets needed to build graphing tab.
        self.tab = QtWidgets.QWidget()
        self._graph = pyqtgraph.PlotWidget()
        self._layout = QtWidgets.QVBoxLayout()

        # Combine pyqt objects.
        self._layout.addWidget(self._graph)
        self.tab.setLayout(self._layout)

        # Declare graph Features.
        self._graph_line = pyqtgraph.InfiniteLine(movable=True, angle=90, label='x={value:0.2f}', 
                       labelOpts={'position':0.1, 'color': (200,200,100), 'fill': (200,200,200,50)})
        self._graph.addItem(self._graph_line)
        self._graph.mouseReleaseEvent = self.line_change

        # Plot graph within the tab.
        self._plot = self._graph.plot(self._x, self._y)

    def line_change(self, event):
        mousepoint = self._graph.plotItem.vb.mapDeviceToView(event.pos())
        print(mousepoint.x() + 1)
        print(self._graph_line.value())
        self.selected_x = self._graph_line.value()

    def graph_clicked(self, event):
        mousepoint = self._graph.plotItem.vb.mapDeviceToView(event.pos())
        #if mousepoint.x() == self._graph_line.value():
        print(mousepoint.x())
        print(self._graph_line.value())
        #self._graph_line.setValue(mousepoint.x() - 7)
        #self.selected_x = mousepoint.x()

    def get_selected_x(self):
        return self.selected_x

    def get_tab_widget(self):
        return self.tab

    def get_title(self):
        return self.title

    def __repr__(self):
        return "Tab({})".format(self.title)

    def __str__(self):
        return "A tab widget containing a graph. Data represents the {} channel.\nx-vals:\n{}\ny-vals:\n{}".format(self.title, self._x, self._y)

    
