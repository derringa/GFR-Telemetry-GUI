# Author:           Andrew Derringer
# Last Modified:    1/22/2020
# Description:      Tab class is build for pyqt5 to generate a tab object that is passed necessary information
#                   to plot graph without standard behavior of creating another application window.

import itertools
import pyqtgraph
from PyQt5 import QtWidgets


class Tab:

    def __init__(self, sensor_name, x_vals, y_vals, play_slider):
        # Tab data variables.
        self._x = x_vals # Applied to x-axis of pyqtplot.
        self._y = y_vals # Applied to y-axis of pyqtplot.
        self.title = sensor_name # Saved to apply as widget title in pyqt application.
        self.play_slider = play_slider # GUI timestamp slider referencable by each tab.

        # Declare pyqt widgets needed to build graphing tab.
        self.tab = QtWidgets.QWidget()
        self._graph = pyqtgraph.PlotWidget()
        self._layout = QtWidgets.QVBoxLayout()

        # Combine pyqt objects.
        self._layout.addWidget(self._graph)
        self.tab.setLayout(self._layout)

        # Declare graph Features.
        self._graph.plotItem.vb.setLimits(xMin=self._x[0] - 1, xMax=self._x[-1] + 1) # Set x value viewing limits in graph.
        self._graph.plotItem.vb.setMouseEnabled(x=True, y=False)
        self._graph_line = pyqtgraph.InfiniteLine(pos=self.play_slider.value(), movable=True, angle=90, label='x={value:0.2f}', 
                       labelOpts={'position':0.1, 'color': (200,200,100), 'fill': (200,200,200,50)})
        self._graph.addItem(self._graph_line) # Add horizontal tracing line to graph.
        self._graph_line.sigPositionChanged.connect(self.line_change) # On line position change call member function line_change.

        # Plot graph within the tab.
        self._plot = self._graph.plot(self._x, self._y)


    def line_change(self, event):
        val = self._graph_line.value() # x-value location of line on graph.
        self.play_slider.setValue(val) # Change GUI slider position according to graph line.


    def get_selected_x(self):
        return self._graph_line.value()


    def set_selected_x(self, x):
        self._graph_line.setValue(x) # Allows GUI function calls to change line location.


    def get_max_timestamp(self):
        return self._x[-1] # Return the largest x-value along the x-axis for GUI slider scaling.


    def get_tab_widget(self):
        return self.tab


    def get_title(self):
        return self.title


    def __repr__(self):
        return "Tab({})".format(self.title)


    def __str__(self):
        return "A tab widget containing a graph. Data represents the {} channel.\nx-vals:\n{}\ny-vals:\n{}".format(self.title, self._x, self._y)


    def __eq__(self, other):
        return self.title == other.title
    
