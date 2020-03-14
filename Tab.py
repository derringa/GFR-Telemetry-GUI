# Author:           Andrew Derringer
# Last Modified:    1/31/2020
# Description:      Tab class is build for pyqt5 to generate a tab object that is passed necessary information
#                   to plot graph without standard behavior of creating another application window.

import itertools
import numpy
import pyqtgraph
from PyQt5 import QtWidgets


class Tab:

    def __init__(self, title, play_slider, x_units='seconds'):
        # Tab data variables.
        self._plots = {}
        self._x = []
        self._x_units = x_units
        self.tab_title = title
        self.play_slider = play_slider # GUI timestamp slider referencable by each tab.

        # Declare pyqt widgets needed to build graphing tab.
        self.tab = QtWidgets.QWidget()
        self._graph = pyqtgraph.PlotWidget()
        self._colors = ['b', 'g', 'r', 'c', 'm', 'y', 'w']

        # Combine pyqt objects.
        self._layout = QtWidgets.QVBoxLayout()
        self._layout.addWidget(self._graph)
        self.tab.setLayout(self._layout)


    def interpolate_plots(self):
        # Check all timestamps in case that matching current _x was removed.
        for key, value in self._plots.items():
            if len(self._x) == 0:
                self._x = value['x_vals']
            elif len(value['x_vals']) < len(self._x) and len(value['x_vals']) != 0:
                self._x = value['x_vals']

        # After _x reassigned interpolate all signals by new _x.
        for key, value in self._plots.items():
            if len(value['y_vals']) == 0:
                value['inter_y_vals'] = value['y_vals']
            else:
                value['inter_y_vals'] = numpy.interp(self._x, value['x_vals'], value['y_vals'])


    def clear_plots(self):
        # Use stored plot and axis items to remove children items from main ViewBox.
        for key, value in self._plots.items():
            if value['plotAxis'] != None: 
                self._graph.plotItem.scene().removeItem(value['plotAxis'])
                self._graph.plotItem.layout.removeItem(value['plotAxis'])
                value['plotAxis'] = None
            if value['plotItem'] != None: 
                self._graph.plotItem.scene().removeItem(value['plotItem'])
                value['plotItem'] = None
            if value['color'] != None: 
                self._colors.append(value['color'])
                value['color'] = None


    def render_stackplot(self):
        self.interpolate_plots()

        # Main ViewBox Features.
        self._graph.plotItem.vb.setRange(xRange=(self._x[0], self._x[-1]))
        self._graph.plotItem.vb.setLimits(xMin=self._x[0] - 1, xMax=self._x[-1] + 1) # Set x value viewing limits in graph.
        self._graph.setLabel('bottom', self._x_units, color='white', **{'font-size': '12pt'})
        # x_axis = self._graph.plotItem.getAxis('bottom')
        # x_axis.setTickSpacing(60, 10) # 60 interval ticker for mintutes
        self._graph_line = pyqtgraph.InfiniteLine(pos=self.play_slider.value(), movable=True, angle=90, label='x={value:0.2f}', 
                       labelOpts={'position':0.1, 'color': (200,200,100), 'fill': (200,200,200,50)})
        self._graph.addItem(self._graph_line) # Add horizontal tracing line to graph.
        self._graph_line.sigPositionChanged.connect(self.line_change) # On line position change call member function line_change.


    def graph_features(self):
        # Main ViewBox Features.
        if len(self._x) != 0:
            self._graph.plotItem.vb.setRange(xRange=(self._x[0], self._x[-1]))
            self._graph.plotItem.vb.setLimits(xMin=self._x[0] - 1, xMax=self._x[-1] + 1) # Set x value viewing limits in graph.
        self._graph.setLabel('bottom', self._x_units, color='white', **{'font-size': '12pt'})
        # x_axis = self._graph.plotItem.getAxis('bottom')
        # x_axis.setTickSpacing(60, 10) # 60 interval ticker for mintutes
        self._graph_line = pyqtgraph.InfiniteLine(pos=self.play_slider.value(), movable=True, angle=90, label='x={value:0.2f}', 
                       labelOpts={'position':0.1, 'color': (200,200,100), 'fill': (200,200,200,50)})
        self._graph.addItem(self._graph_line) # Add horizontal tracing line to graph.
        self._graph_line.sigPositionChanged.connect(self.line_change) # On line position change call member function line_change.


    def render_multiplot(self):
        # Clear old plots and prepare data and features.
        # self.clear_plots()
        self.interpolate_plots()
        self.graph_features()

        # Add stacking ViewBox plots to graph.
        axis_count = 2
        plot_layout = self._graph.plotItem
        plot_layout.scene().removeItem(plot_layout.getAxis('left'))

        for key, value in self._plots.items():
            plot = pyqtgraph.ViewBox()
            plot_color = self._colors.pop()

            # Unique case for first added plot.
            if axis_count == 2:
                plot_layout.showAxis('right')
                plot_layout.getAxis('right').linkToView(plot)
                plot_layout.getAxis('right').setLabel(text=key, units=value['y_units'], **{'font-size': '12pt'})
                plot_layout.getAxis('right').setPen(pyqtgraph.mkPen(color=plot_color))
                value['plotAxis'] = plot_layout.getAxis('right') # Save in dict for easy object access.
            # All subsequent plots.
            else:
                axis = pyqtgraph.AxisItem('right')
                plot_layout.layout.addItem(axis, 2, axis_count)
                axis.linkToView(plot)
                axis.setLabel(text=key, units=value['y_units'], **{'font-size': '12pt'})
                axis.setPen(pyqtgraph.mkPen(color=plot_color))
                value['plotAxis'] = axis # Save in dict for easy object access.
            
            value['plotItem'] = plot # Save in dict for easy object access.
            value['color'] = plot_color

            # Link plot to main x-axis and and plot data.
            plot_layout.scene().addItem(plot)
            plot.setXLink(plot_layout)
            if len(self._x) == len(value['inter_y_vals']):
                plot.addItem(pyqtgraph.PlotCurveItem(self._x, value['inter_y_vals'], pen=plot_color))
            plot.setMouseEnabled(x=True, y=False)
            axis_count += 1

        # Manage plot scaling with updateViews function.
        self.updateViews()
        self._graph.plotItem.vb.sigResized.connect(self.updateViews)


    def updateViews(self):
        # On resizing event rescale plots to main ViewBox geometry.
        for key, value in self._plots.items():
            if value['plotItem'] != None:
                plot = value['plotItem']
                plot.setGeometry(self._graph.plotItem.vb.sceneBoundingRect())
                plot.linkedViewChanged(self._graph.plotItem.vb, plot.XAxis)


    def get_plots(self):
        for key, value in self._plots.items():
            yield key


    def add_plot(self, title, timestamps=None, samples=None, units=None):
        # Add or update signal to be displayed
        self._plots[title] = {
            'x_vals': timestamps,
            'y_vals': samples,
            'inter_y_vals': None,
            'y_units': units,
            'plotItem': None,
            'plotAxis': None,
            'color': None
        }

        if self._plots[title]['x_vals'] is None and self._plots[title]['y_vals'] is None:
            self._plots[title]['x_vals'] = []
            self._plots[title]['y_vals'] = []

        #print("Add Plot:\nTitle = {}\ntimestamps = {}\nsamples = {}\nunites = {}\ninter_samples = {}".format(title, self._plots[title]['x_vals'], self._plots[title]['y_vals'], self._plots[title]['y_units'], self._plots[title]['inter_y_vals']))


    def add_plots(self, plot_list):
        for title in plot_list:
            self.add_plot(title)


    def remove_plot(self, title):
        # Remove signal from plot list if present.
        value = self._plots[title]

        if value['plotItem'] != None: self._graph.plotItem.scene().removeItem(value['plotItem'])
        if value['plotAxis'] != None: self._graph.plotItem.scene().removeItem(value['plotAxis'])
        if value['color'] != None: self._colors.append(value['color'])
        
        self._plots.pop(title, None)


    def line_change(self, event):
        val = self._graph_line.value() # x-value location of line on graph.
        self.play_slider.setValue(val) # Change GUI slider position according to graph line.


    def get_selected_x(self):
        return self._graph_line.value()


    def set_selected_x(self, x):
        self._graph_line.setValue(x) # Allows GUI function calls to change line location.


    def get_max_timestamp(self):
        if len(self._x) != 0: return self._x[-1] # Return the largest x-value along the x-axis for GUI slider scaling.
        return 0


    def get_tab_widget(self):
        return self.tab


    def get_title(self):
        return self.tab_title


    def __repr__(self):
        return "Tab({})".format(self.tab_title)


    # def __str__(self):
    #     return "A tab widget containing a graph. Data represents the {} channel.\nx-vals:\n{}\ny-vals:\n{}".format(self.tab_title, self._x, self._y)


    # def __eq__(self, other):
    #     if self.tab_title != other.tab_title:
    #         return False

    #     if cmp(self._plots, other._plots) != 0:
    #         return False
        
    #     return True
    
