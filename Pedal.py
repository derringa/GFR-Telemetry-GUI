# Author:           Andrew Derringer
# Last Modified:    1/31/2020
# Description:      Pedal class generates a gas or brake pedal graphic whose angle or compression
#                   changes by the value passed to it compared to the user defined max.

import numpy
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.Qt import Qt

class Pedal(QtWidgets.QWidget):
    
    def __init__(self, comp=0, max_y=0):
        super().__init__()
        
        self._comp = comp
        self.max = max_y


    def set_pressure(self, comp):
        self._comp = comp
        self.repaint()
    

    def get_max(self):
        return self.max


    def paintEvent(self, e):
        canvas = QtGui.QPainter()
        canvas.begin(self)
        self.draw_pedal(canvas)
        self.draw_border(canvas)
        canvas.end()
        
        
    def draw_pedal(self, canvas):
      
        size = self.size()
        pen = QtGui.QPen(self.set_pen_color(), 5, Qt.SolidLine)
        canvas.setPen(pen)

        origin_x = 5
        origin_y = size.height() - 5
        hyp = 100
        theta = ((self.max - self._comp) / (self.max * 4)) * numpy.pi
        x = numpy.cos(theta) * hyp
        y = numpy.sin(theta) * hyp
        canvas.drawLine(origin_x, origin_y, origin_x + x, origin_y - y)
        

    def set_pen_color(self):
        if self._comp < self.max * 0.1:
            return QtGui.QColor(255, 255, 255)
        elif self._comp < self.max * 0.3:
            return QtGui.QColor(255, 204, 204)
        elif self._comp < self.max * 0.5:
            return QtGui.QColor(255, 153, 153)              
        elif self._comp < self.max * 0.7:
            return QtGui.QColor(255, 102, 102)
        elif self._comp < self.max * 0.9:
            return QtGui.QColor(255, 51, 51)
        else:  
            return QtGui.QColor(255, 0, 0)


    def draw_border(self, canvas):
        size = self.size()
        pen = QtGui.QPen(QtGui.QColor(0, 0, 0), 5, Qt.SolidLine)
        canvas.setPen(pen)

        canvas.drawLine(0, 0, 0, size.height())
        canvas.drawLine(0, 0, size.width(), 0)
        canvas.drawLine(size.width(), size.height(), 0, size.height())
        canvas.drawLine(size.width(), size.height(), size.width(), 0)