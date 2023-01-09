# This Python file uses the following encoding: utf-8
import sys
import subprocess
from datetime import datetime
import threading
import time
from client import Client
from startup import Startup

from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtGui import QAction


# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
from ui_form import Ui_MainWindow

class MainWindow(QMainWindow):

    APP_RUNNING = True

    # connection actions that gets triggered on connection open and close respectively
    connOpen = None # initialized in setupAppActions()
    connClose = None # initialized in setupAppActions()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.APP_RUNNING = True
        self.CMD_RUNNING = False
        self.client = Client()
        self.setupButtons()
        self.setupAppActions()
        self.startUIAnimThreads()





    def startSvrRead(self):
        '''This function starts reading data from the Client'''
        while MainWindow.APP_RUNNING:
            data = self.client.recvData()
            if data != '': # If data receieved is not empty
                self.client.response = data
                self.dataRecvdAction.trigger() # Trigger data received action
                #self.CMD_RUNNING = False
                break # and break from loop

    def sendCommand(self, command):
        '''This function sends data to the Client'''
        self.client.sndData(command)

        recvThread = threading.Thread(target=self.startSvrRead)
        recvThread.daemon = True
        recvThread.start()

    def handleRunCmdBtnClick(self):
        command = self.ui.commandBox.text() # get the command to send from the command box
        self.sendCommand(command) # send command in command box
        self.ui.commandBox.setText('') # clear text in cmmand box

    def setupButtons(self): # setup handlers for all buttons in UI
#        self.dataRecvdAction = QAction('Action Triggered On Response From Client', self)
#        self.dataRecvdAction.triggered.connect(lambda : self.dispClientResponse(self.client.response))
        self.client.response = ''

        runBtn = self.ui.btnRunCommand
        runBtn.clicked.connect(lambda : self.handleRunCmdBtnClick())
        runBtn.setEnabled(False) # disable the run command button by default
        self.ui.commandBox.setEnabled(False) # disable the command box by default

        btnConn = self.ui.btnConnectToHost
        #btnConn.clicked.connect(lambda : self.handleConnToHostBtnClick())
        startup = Startup(self)
        btnConn.clicked.connect(lambda : startup.show())



    def handleConnToHostBtnClick(self, host=Client.HOST, port=Client.PORT):
        if Client.CUR_CONN_STATE == Client.CONN_STATE_DISCONNECTED:
            self.client.startComms(host, port)
            self.connStateChanged.trigger() # trigger connection state changed action
        elif Client.CUR_CONN_STATE == Client.CONN_STATE_CONNECTED:
            self.client.endComms()
            self.connStateChanged.trigger() # trigger connection state changed action
        elif Client.CUR_CONN_STATE == Client.CONN_STATE_REFUSED:
            self.client.startComms(host, port)
            self.connStateChanged.trigger() # trigger connection state changed action
        elif Client.CUR_CONN_STATE == Client.CONN_STATE_ABORTED:
            self.client.startComms(host, port)
            self.connStateChanged.trigger() # trigger connection state changed action
            pass
        elif Client.CUR_CONN_STATE == Client.CONN_STATE_TIMEOUT:
            self.client.startComms(host, port)
            self.connStateChanged.trigger() # trigger connection state changed action
        else: pass
        pass




    def dispServerResponse(self, text):
        dots = '-' * 163
        resp = text + '\n' + dots
        self.ui.commandOutput.append(resp)



    def showServerInfo(self):
        if Client.CUR_CONN_STATE == Client.CONN_STATE_CONNECTED:
            self.ui.serverInfoList.setMarkdown('') # clear Client info display
            server_info = self.client.server_info
            host = 'Host Name: %s running on %s %s (%s)' % (server_info['host_name'], server_info['os'], server_info['os_release'], server_info['bit'])
            cpu = 'Processor: %s' % server_info['cpu']
            cpu_speed = 'CPU Speed: %s' % server_info['cpu_speed']
            no_cores = 'No. Of Cores: %s' % server_info['cpu_core']
            ram = 'RAM: %s' % server_info['mem_total']
            infoList = [host, cpu, cpu_speed, no_cores, ram]
            for info in infoList:
                self.ui.serverInfoList.append(info + '\n')
        else:
            self.ui.serverInfoList.setMarkdown('') # clear Client info display



    def startUIAnimThreads(self):
        # Thread to update the display of the current time
        timeThread = threading.Thread(target=self.setupDateTimeDisplay)
        timeThread.daemon = True
        timeThread.start()



    def setupDateTimeDisplay(self):
        while MainWindow.APP_RUNNING:
            curTime = datetime.now()
            curTime = curTime.strftime('%A %x %I:%M:%S %p')
            self.ui.dateTimeLabel.setText(curTime)
            time.sleep(1)


    def setConnStatusBGColor(self):
        if Client.CUR_CONN_STATE == Client.CONN_STATE_CONNECTED:
            self.ui.svrConnStatus.setStyleSheet("font: 700 9pt Segoe UI;"
            "background-color: green;"
            "color: white")
        elif Client.CUR_CONN_STATE == Client.CONN_STATE_CONNECTING:
            self.ui.svrConnStatus.setStyleSheet("font: 700 9pt Segoe UI;"
            "background-color: yellow;"
            "color: white")
        elif Client.CUR_CONN_STATE == Client.CONN_STATE_DISCONNECTED \
        or Client.CUR_CONN_STATE == Client.CONN_STATE_REFUSED:
            self.ui.svrConnStatus.setStyleSheet("font: 700 9pt Segoe UI;"
            "background-color: red;"
            "color: white")
        else:
            pass

        pass

    def handleConnStateChanged(self): # handler for the connStateChanged action
        btnConn = self.ui.btnConnectToHost
        if Client.CUR_CONN_STATE == Client.CONN_STATE_DISCONNECTED:
            text = 'No active connection to %s on port - %s' % (self.client.HOST, self.client.PORT)
            self.ui.btnRunCommand.setEnabled(False) # disable the run command button
            self.ui.commandBox.setEnabled(False) # disable the command box
            self.ui.svrConnStatus.setText(text)
            self.setConnStatusBGColor()
            self.showServerInfo()
            btnConn.setText('Connect')
        elif Client.CUR_CONN_STATE == Client.CONN_STATE_CONNECTED:
            text = 'Connected to host %s on port - %s' % (self.client.HOST, self.client.PORT)
            self.ui.btnRunCommand.setEnabled(True) # enable the run command button
            self.ui.commandBox.setEnabled(True) # disable the command box
            self.ui.svrConnStatus.setText(text)
            self.setConnStatusBGColor()
            self.showServerInfo()
            btnConn.setText('Disconnect')
        elif Client.CUR_CONN_STATE == Client.CONN_STATE_CONNECTING:
            text = 'Connecting to host %s on port - %s' % (self.client.HOST, self.client.PORT)
            self.ui.btnRunCommand.setEnabled(False) # disable the run command button
            self.ui.commandBox.setEnabled(False) # disable the command box
            self.ui.svrConnStatus.setText(text)
            self.setConnStatusBGColor()
            self.showServerInfo()
            #self.ui.btnConnectToHost.setDisabled(True)
        elif Client.CUR_CONN_STATE == Client.CONN_STATE_REFUSED:
            text = 'Connection to %s was refused on port - %s' % (self.client.HOST, self.client.PORT)
            self.ui.btnRunCommand.setEnabled(False) # disable the run command button
            self.ui.commandBox.setEnabled(False) # disable the command box
            self.ui.svrConnStatus.setText(text)
            self.setConnStatusBGColor()
            self.showServerInfo()
            btnConn.setText('Connect')
        elif Client.CUR_CONN_STATE == Client.CONN_STATE_RESET:
            text = 'Connection reset, try again'
            self.ui.btnRunCommand.setEnabled(False) # disable the run command button
            self.ui.commandBox.setEnabled(False) # disable the command box
            self.ui.svrConnStatus.setText(text)
            self.setConnStatusBGColor()
            self.showServerInfo()
            btnConn.setText('Connect')
        elif Client.CUR_CONN_STATE == Client.CONN_STATE_ABORTED:
            text = 'Connection to %s was aborted' % self.client.HOST
            self.ui.btnRunCommand.setEnabled(False) # disable the run command button
            self.ui.commandBox.setEnabled(False) # disable the command box
            self.ui.svrConnStatus.setText(text)
            self.setConnStatusBGColor()
            self.showServerInfo()
            btnConn.setText('Connect')
        elif Client.CUR_CONN_STATE == Client.CONN_STATE_TIMEOUT:
            text = 'Connection to (%s) timed-out' % self.client.HOST
            self.ui.btnRunCommand.setEnabled(False) # disable the run command button
            self.ui.commandBox.setEnabled(False) # disable the command box
            self.ui.svrConnStatus.setText(text)
            self.setConnStatusBGColor()
            self.showServerInfo()
            btnConn.setText('Connect')
        else:
            pass

    def setupAppActions(self): # setup all actions in the app
        self.connStateChanged = QAction('Action To Be Triggered On Connection State Changed', self)
        self.connStateChanged.triggered.connect(lambda : self.handleConnStateChanged())

        self.dataRecvdAction = QAction('Action To Be Triggered On Response From Client', self)
        self.dataRecvdAction.triggered.connect(lambda : self.dispServerResponse(self.client.response))

def cleanUpApp(): # function to clean up app when about to close
    MainWindow.APP_RUNNING = False

    #Call function to close Client connection


def compileUI():
    cmd = 'pyside6-uic startup.ui -o ui_startup.py'
    subprocess.run(cmd)

if __name__ == "__main__":
    #compileUI()
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(cleanUpApp)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())

