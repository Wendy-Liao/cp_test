#!/usr/bin/env python

import sys
import subprocess
import time
import threading
import ConfigParser
from PyQt4.QtGui import *
from PyQt4.QtCore import *

class FirmwareVersion(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
   
        self.init()
        self.ui()
        self.run()

    def init(self):
        self.config = ConfigParser.ConfigParser()
        self.config.read('testlist.config')
        self.timer = QTimer(self)
        self.timeout = self.config.getint('FirmwareVersion', 'Timeout')
        self.timer.setSingleShot(False)
        self.timer.timeout.connect(self.update_msg)
        self.timer.start(1000)
        self.start = True
        self.finished = False
    
    def ui(self):
        self.setWindowTitle("FirmwareCheck!")
        self.messageLayout = QVBoxLayout()
        self.setGeometry(200, 100, 500, 500)
        self.msg = QTextEdit()
        self.time = QLabel('Time')
        self.messageLayout.addWidget(self.time)
        self.messageLayout.addWidget(self.msg)
        self.setLayout(self.messageLayout)
    
    def run(self):
        self.result = subprocess.Popen("adb shell ./home/flex/bin/fct1-main.sh  FCT.1.8.2 ", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (self.output, self.err) = self.result.communicate()
        self.returncode = self.result.wait()
        
    def update_msg(self):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
        self.time.setText('Time' + ' ' + str(self.timeout))
        if self.start:
            self.msg.setText(timestamp + ' Start doing test')
            self.start = False
        elif self.timeout == 0:
            if self.returncode == 0:
                self.msg.append(timestamp + self.output)
            else:
                self.msg.append(timestamp + self.err)
            self.msg.append(timestamp + ' End test')
        elif self.timeout == -1:
            if 'COMPLETE' in self.output:
                self.Pass = True
            else:
                self.Pass = False
            self.finished =  True
            self.timer.stop()
            self.close()
        self.timeout = self.timeout - 1 


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_ui = FirmwareVersion()
    main_ui.show()
    app.exec_()