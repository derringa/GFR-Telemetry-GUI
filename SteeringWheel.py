# Author:           Andrew Derringer
# Last Modified:    1/31/2020
# Description:      Pedal class generates a gas or brake pedal graphic whose angle or compression
#                   changes by the value passed to it compared to the user defined max.


import numpy
from PyQt5 import QtWidgets, QtCore, QtGui


ROTATION_RANGE = 90

class SteeringWheel(QtWidgets.QWidget):
    
    def __init__(self, sta=0, dimensions=200):
        super().__init__()
        # super(SteeringWheel, self).__init__(parent)
        self._rotation = self.translateToRotation(sta)     


    def setSTA(self, sta):
        self._rotation = self.translateToRotation(sta)
        self.repaint()
    

    def translateToRotation(self, sta):
        return (ROTATION_RANGE / 100) * sta


    def paintEvent(self, e):
        canvas = QtGui.QPainter(self)
        self.drawWheel(canvas)
        self.drawBorder(canvas)
        
        
    def drawWheel(self, canvas):
        width = self.size().width()
        height = self.size().height()

        transform = QtGui.QTransform().rotate(self._rotation)

        pic = QtGui.QPixmap("./images/steering-wheel.png")
        scaled = pic.scaled(width, height, QtCore.Qt.KeepAspectRatio)
        rotated = scaled.transformed(transform, QtCore.Qt.SmoothTransformation)
        
        x_offset = (rotated.width() - width) / 2
        y_offset = (rotated.height() - height) / 2
        cropped = rotated.copy(QtCore.QRect(x_offset, y_offset, width, height))

        canvas.drawPixmap(self.rect(), cropped)

        
    def drawBorder(self, canvas):
        size = self.size()
        pen = QtGui.QPen(QtGui.QColor(0, 0, 0), 5, QtCore.Qt.SolidLine)
        canvas.setPen(pen)

        canvas.drawLine(0, 0, 0, size.height())
        canvas.drawLine(0, 0, size.width(), 0)
        canvas.drawLine(size.width(), size.height(), 0, size.height())
        canvas.drawLine(size.width(), size.height(), size.width(), 0)
