# Description: Main file for the GUI

# To generate the python file from the ui file, run the following command:
# pyside6-uic .\MainWidget.ui -o MainWidget.py


import sys
from PySide6 import QtWidgets

# Importing the midi_over_lan module
sys.path.append("..")
import midi_over_lan
from MainWidget import Ui_MainWidget


class MainWidget(QtWidgets.QWidget, Ui_MainWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


app = QtWidgets.QApplication(sys.argv)

widget = MainWidget()
widget.show()
app.exec()
