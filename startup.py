# This Python file uses the following encoding: utf-8

from PySide6.QtWidgets import QDialog, QDialogButtonBox
from client import Client
#from PySide6.QtGui import QAction


# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic startup.ui -o ui_startup.py
from ui_startup import Ui_Startup

class Startup(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.ui = Ui_Startup()
        self.ui.setupUi(self)
        self.changeButtonDefaults()


    def changeButtonDefaults(self):
        btnOk = self.ui.buttonBox.button(QDialogButtonBox.Ok)
        btnCancel = self.ui.buttonBox.button(QDialogButtonBox.Cancel)
        host = self.ui.host
        port = self.ui.port
        btnOk.setText('Connect')
        btnOk.setEnabled(False)

        btnCancel.setText('Cancel')


        host.textChanged.connect(lambda : btnOk.setEnabled(True) if str(host.text()) != '' else btnOk.setEnabled(False))
        btnOk.clicked.connect(lambda : self.parent.handleConnToHostBtnClick(host.text(), port.text()) if port.text() != '' else
        self.parent.handleConnToHostBtnClick(host.text(), Client.PORT))
