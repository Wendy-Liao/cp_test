#!/usr/bin/env python

import sys
import ConfigParser
import threading
import time
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import FirmwareVersion
import NAND


class MyThread(QThread):
    trigger = pyqtSignal(str)

    def __init__(self, parent=None):
        super(MyThread, self).__init__(parent)

    def setup(self, item_name):
        self.item_name = item_name

    def run(self):
        time.sleep(1)  # random sleep to imitate working
        self.trigger.emit(self.item_name)

class Main_UI(QWidget):
    def __init__(self, parent = None):
        super(Main_UI, self).__init__(parent)
        self.config = ConfigParser.ConfigParser()
        self.testlist = []
        self.buttons = []
        self.getTestList()
        self.CreateLayout()
        #self.Connect()
        self.setGeometry(200, 100, 1000, 500)
        #self.showMaximized()

    def getTestList(self):
        self.config.read('testlist.config')
        for each_section in self.config.sections():
            if self.config.get(each_section, 'enable') == 'true':
                self.testlist.append(each_section) 
        
    def CreateLayout(self):
        self.groupBox = QGroupBox(self)
        UI_layout = QGridLayout()
        button_layout = QGridLayout()
        info_layout = QHBoxLayout()
        #button_layout.setSpacing(0)
        #UI_layout.setSpacing(0)
        
        self.result = QTextEdit()

        self.deviceID = QLabel('Serial.No')
        self.deviceIDEdit = QLineEdit()
        info_layout.addWidget(self.deviceID)
        info_layout.addWidget(self.deviceIDEdit)
        test_all_Button = QPushButton("&TestAll")
        test_all_Button.setFixedSize(120,60)

        positions = [(i,j) for i in range(3) for j in range(3)]
        for position, item in zip(positions, self.testlist):
            width = 120
            height = 60
            button = QPushButton("&" + item)
            button.setFixedSize(width,height)
            self.buttons.append(button)
            button_layout.addWidget(button, *position)
        
        for item in self.testlist:
            index = self.config.get(item,'index')
            self.connect(self.buttons[int(index)],SIGNAL("clicked()"),lambda item_name=item:self.BtnActivity(item_name))
        
        UI_layout.addLayout(info_layout,0,0)
        UI_layout.addWidget(test_all_Button,1,1)
        UI_layout.addLayout(button_layout,2,0)
        UI_layout.addWidget(self.result,2,1)
        self.setLayout(UI_layout)

    def BtnActivity(self, item_name):
        if item_name == 'FirmwareVersion':
            self.getTestitem(item_name)
            self.test_item = FirmwareVersion.FirmwareVersion()
            self.test_item.show()
            self.StartThread()
        if item_name == 'NAND':
            self.getTestitem(item_name)
            self.test_item = NAND.NAND()
            self.test_item.show()
            self.StartThread()

    def getTestitem(self, item_name):
        self.item_name = item_name
        self.index = int(self.config.get(item_name, 'index'))

    def StartThread(self):
        self.test_item.show()
        thread = MyThread(self)    
        thread.trigger.connect(self.UpdateUI) 
        thread.setup(self.item_name)            
        thread.start()  

    def UpdateUI(self, item_name):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        if self.test_item.finished:    
            if(self.test_item.returncode == 0):
                if self.test_item.Pass:
                    self.buttons[self.index].setStyleSheet("background-color: rgb(0, 255, 0)")
                    self.result.append('Result:\n' + self.test_item.output)
                    self.result.append(timestamp + ' Done %s test' %item_name)
                else:
                    self.buttons[self.index].setStyleSheet("background-color: rgb(255, 0, 0)")
                    self.result.append('Result:\n' + self.test_item.err)
                    self.result.append(timestamp + ' Done %s test' %item_name)
            else:
                self.result.append('Exception:\n' + self.test_item.err)
                self.buttons[self.index].setStyleSheet("background-color: rgb(255, 0, 0)")
                self.result.append(timestamp + ' Done %s test' %item_name)
        else:
            self.result.append(timestamp + ' Start %s test' %item_name)
            self.StartThread()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_ui = Main_UI()
    main_ui.show()
    app.exec_()

