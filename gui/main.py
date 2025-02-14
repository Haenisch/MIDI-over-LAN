"""MIDI over LAN GUI client."""

# pylint: disable=line-too-long
# pylint: disable=no-name-in-module
# pylint: disable=no-member
# pylint: disable=c-extension-no-member
# pylint: disable=pointless-string-statement

"""
The GUI client is a simple "MIDI over LAN" application that allows you to
select the MIDI output ports that you want to send over the network and the
MIDI input ports that you want to receive from the network.

The GUI has four sections:

    1. Outgoing Traffic: A list of local MIDI output ports that you want to send
       over the network.

    2. Incoming Traffic: A list of MIDI input ports that you received from the
       network and bind to local MIDI input ports.

    3. Statistics: Round-trip time statistics between various hosts.

    4. About: Information about the application.

The GUI is implemented using the PySide6 library, which is a Python binding, and
uses the Qt Designer to design the layout of the application.

There are two worker processes that run in the background:
    
    1. The sender process sends MIDI messages over the network to the specified
       hosts.
    
    2. The receiver process receives MIDI messages from the network and sends
       them to the specified local MIDI input ports.

The sender and receiver processes are implemented using the multiprocessing
library. The entire communication between the sender and receiver processes is
done using the multiprocessing.Queue class.

Written by: Christoph Hänisch
Last edited: 2025-02-14
License: LGPL-3.0 (see LICENSE file)
"""


import sys
from typing import List, Tuple

import mido
from PySide6 import QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidgetItem


# Importing the midi_over_lan module
sys.path.append('.')
sys.path.append('..')
import midi_over_lan

# To generate the python file from the ui file, run the following command:
# pyside6-uic .\MainWidget.ui -o MainWidget.py
from MainWidget import Ui_MainWidget


class MainWidget(QtWidgets.QWidget, Ui_MainWidget):
    """Main widget for the GUI."""

    def __init__(self):
        """Initialize the main widget."""
        super().__init__()
        self.setupUi(self)
        self.output_ports: List[Tuple[bool, str, str]] = []  # List of tuples (active, device_name, network_name)

        # Setup the table widget.
        self.tableWidget_LocalOutputPorts.clearSelection()
        self.tableWidget_LocalOutputPorts.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.tableWidget_LocalOutputPorts.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.tableWidget_LocalOutputPorts.setSortingEnabled(False)
        self.tableWidget_LocalOutputPorts.itemClicked.connect(self.toggle_active_output_port)
        self.tableWidget_LocalOutputPorts.itemChanged.connect(self.update_network_name)

        # Connect the buttons to the functions.
        self.pushButton_LocalOutputPorts_SelectAll.clicked.connect(self.select_all_output_ports)
        self.pushButton_LocalOutputPorts_UnselectAll.clicked.connect(self.unselect_all_output_ports)
        self.pushButton_LocalOutputPorts_Refresh.clicked.connect(self.refresh_output_ports)
        self.pushButton_LocalOutputPorts_Run.clicked.connect(self.run)
        self.pushButton_LocalOutputPorts_Stop.clicked.connect(self.stop)

        # Add the output ports to the list.
        self.refresh_output_ports()


    def add_output_port(self, active: bool, device_name: str, network_name: str):
        """Add an output port to the list of output ports."""
        # Skip if the port is already in the list.
        for port in self.output_ports:
            if port[1] == device_name:
                return
        self.output_ports.append((active, device_name, network_name))
        self.tableWidget_LocalOutputPorts.setRowCount(len(self.output_ports))
        row = len(self.output_ports) - 1
        item = QTableWidgetItem(device_name)
        item.setCheckState(Qt.Checked if active else Qt.Unchecked)
        item.setFlags(item.flags() & ~Qt.ItemIsEditable & ~Qt.ItemIsSelectable)
        self.tableWidget_LocalOutputPorts.setItem(row, 0, item)
        self.tableWidget_LocalOutputPorts.setItem(row, 1, QTableWidgetItem(network_name))


    def refresh_output_ports(self):
        """Refresh the list of output ports."""
        self.tableWidget_LocalOutputPorts.clearContents()
        self.output_ports = []
        for output_port in mido.get_output_names():
            output_port = output_port.split(':')[0]
            self.add_output_port(False, output_port, output_port)


    def run(self):
        """Start the sending process."""


    def select_all_output_ports(self):
        """Select all output ports."""
        for row in range(self.tableWidget_LocalOutputPorts.rowCount()):
            item = self.tableWidget_LocalOutputPorts.item(row, 0)
            self.output_ports[row] = (True, self.output_ports[row][1], self.output_ports[row][2])
            item.setCheckState(Qt.Checked)


    def stop(self):
        """Stop the sending process."""


    def toggle_active_output_port(self, item: QTableWidgetItem):
        """Toggle the active state of the output port."""
        row = item.row()
        column = item.column()
        if column == 0:
            device_name = self.output_ports[row][1]
            network_name = self.output_ports[row][2]
            item = self.tableWidget_LocalOutputPorts.item(row, 0)
            if item.checkState() == Qt.Checked:
                self.output_ports[row] = (False, device_name, network_name)
                item.setCheckState(Qt.Unchecked)
            else:
                self.output_ports[row] = (True, device_name, network_name)
                item.setCheckState(Qt.Checked)


    def unselect_all_output_ports(self):
        """Unselect all output ports."""
        for row in range(self.tableWidget_LocalOutputPorts.rowCount()):
            self.output_ports[row] = (False, self.output_ports[row][1], self.output_ports[row][2])
            item = self.tableWidget_LocalOutputPorts.item(row, 0)
            item.setCheckState(Qt.Unchecked)


    def update_network_name(self, item: QTableWidgetItem):
        """Update the network name of the output port."""
        row = item.row()
        column = item.column()
        if column == 1:
            active = self.output_ports[row][0]
            device_name = self.output_ports[row][1]
            network_name = item.text()
            self.output_ports[row] = (active, device_name, network_name)


def main():
    """Main function."""
    app = QtWidgets.QApplication(sys.argv)
    widget = MainWidget()
    widget.show()
    app.exec()


if __name__ == "__main__":
    main()
