# Author:           Andrew Derringer
# Last Modified:    1/25/2020
# Description:      Traditional QThread worker class. Portable for proects by customizing init
#                   work and kill methods, and message signaling.
 
from PyQt5 import QtCore
import time

class Worker(QtCore.QThread):
    intReady = QtCore.pyqtSignal(int)

    def __init__(self,parent=None):
        super(Worker, self).__init__(parent)
        self._active = True # Do work toggle


    def increment_track(self):
        # While thread is asked to be active by parent emit int value 1 every second.
        while self._active == True:
            self.intReady.emit(1)
            time.sleep(0.1)


    def kill(self):
        # When called deactivate work method and wait for cleanup.
        self._active = False
        self.wait()