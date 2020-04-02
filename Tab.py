# Author:           Andrew Derringer
# Last Modified:    3/28/2020
# Description:      Tab class is build for pyqt5 to generate a tab object that is passed necessary information
#                   to plot graph without standard behavior of creating another application window.

import numpy
import pyqtgraph
from PyQt5 import QtWidgets


class Tab:

    def __init__(self, title, play_slider, x_units='seconds'):
        # Tab data variables.
        self._plots = []
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
        for plot in self._plots:
            if len(self._x) == 0:
                self._x = plot['x_vals']
            elif len(plot['x_vals']) < len(self._x) and len(plot['x_vals']) != 0:
                self._x = plot['x_vals']

        # After _x reassigned interpolate all signals by new _x.
        for plot in self._plots:
            if len(plot['y_vals']) == 0:
                plot['inter_y_vals'] = plot['y_vals']
            else:
                plot['inter_y_vals'] = numpy.interp(self._x, plot['x_vals'], plot['y_vals'])


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

        for plot_data in self._plots:
            plot = pyqtgraph.ViewBox()
            plot_color = self._colors.pop()

            # Unique case for first added plot.
            if axis_count == 2:
                plot_layout.showAxis('right')
                plot_layout.getAxis('right').linkToView(plot)
                plot_layout.getAxis('right').setLabel(text=plot_data['signal'], units=plot_data['y_units'], **{'font-size': '12pt'})
                plot_layout.getAxis('right').setPen(pyqtgraph.mkPen(color=plot_color))
                plot_data['plotAxis'] = plot_layout.getAxis('right') # Save in dict for easy object access.
            # All subsequent plots.
            else:
                axis = pyqtgraph.AxisItem('right')
                plot_layout.layout.addItem(axis, 2, axis_count)
                axis.linkToView(plot)
                axis.setLabel(text=plot_data['signal'], units=plot_data['y_units'], **{'font-size': '12pt'})
                axis.setPen(pyqtgraph.mkPen(color=plot_color))
                plot_data['plotAxis'] = axis # Save in dict for easy object access.
            
            plot_data['plotItem'] = plot # Save in dict for easy object access.
            plot_data['color'] = plot_color

            # Link plot to main x-axis and and plot data.
            plot_layout.scene().addItem(plot)
            plot.setXLink(plot_layout)
            if len(self._x) == len(plot_data['inter_y_vals']):
                plot.addItem(pyqtgraph.PlotCurveItem(self._x, plot_data['inter_y_vals'], pen=plot_color))
            plot.setMouseEnabled(x=True, y=False)
            axis_count += 1

        # Manage plot scaling with updateViews function.
        self.updateViews()
        self._graph.plotItem.vb.sigResized.connect(self.updateViews)


    def updateViews(self):
        # On resizing event rescale plots to main ViewBox geometry.
        for plot in self._plots:
            if plot['plotItem'] != None:
                plot = plot['plotItem']
                plot.setGeometry(self._graph.plotItem.vb.sceneBoundingRect())
                plot.linkedViewChanged(self._graph.plotItem.vb, plot.XAxis)


    def get_plots(self):
        # Provide group and signal for each signal being plotted.
        for plot in self._plots:
            yield (plot['group'], plot['signal'])


    def add_plot(self, group, signal, timestamps=None, samples=None, units=None):
        # Add or update signal to be displayed
        plot_dict = {
            'group': group,
            'signal': signal,
            'x_vals': timestamps,
            'y_vals': samples,
            'inter_y_vals': None,
            'y_units': units,
            'plotItem': None,
            'plotAxis': None,
            'color': None
        }

        if plot_dict['x_vals'] is None and plot_dict['y_vals'] is None:
            plot_dict['x_vals'] = []
            plot_dict['y_vals'] = []

        self._plots.append(plot_dict)


    def add_plots(self, plot_dict):
        # Receive batch of plots to be added and pass each to add_plot.
        for group, signal_list in plot_dict.items():
            for signal in signal_list:
                self.add_plot(group, signal)


    def line_change(self, event):
        val = self._graph_line.value() # x-value location of line on graph.
        self.play_slider.setValue(val) # Change GUI slider position according to graph line.


    def get_selected_x(self):
        return self._graph_line.value()


    def set_selected_x(self, x):
        self._graph_line.setValue(x) # Allows GUI function calls to change line location.


    def get_max_timestamp(self):
        if len(self._x) != 0: 
            return self._x[-1] # Return the largest x-value along the x-axis for GUI slider scaling.
        return 0


    def get_tab_widget(self):
        return self.tab


    def get_title(self):
        return self.tab_title

