"""MIDI over LAN GUI client."""

# pylint: disable=line-too-long
# pylint: disable=no-name-in-module
# pylint: disable=no-member
# pylint: disable=c-extension-no-member
# pylint: disable=pointless-string-statement
# pylint: disable=wrong-import-position
# pylint: disable=wrong-import-order

# The GUI client is a simple "MIDI over LAN" application that allows you to
# select the MIDI input ports that you want to send over the network and the
# MIDI input ports that you want to receive from the network.
#
# The GUI has four sections:
#
#     1. Outgoing Traffic: A list of local MIDI input ports that you want to send
#        over the network.
#
#     2. Incoming Traffic: A list of MIDI input ports that you received from the
#        network and bind to local MIDI output ports.
#
#     3. Statistics: Round-trip time statistics between various hosts.
#
#     4. About: Information about the application.
#
# The GUI is implemented using the PySide6 library, which is a Python binding, and
# uses the Qt Designer to design the layout of the application.
#
# There are two worker processes that run in the background:
#
#     1. The sender process sends MIDI messages over the network to the listening
#        hosts.
#
#     2. The receiver process receives MIDI messages from the network and sends
#        them to the specified local MIDI output ports.
#
# The sender and receiver processes are implemented using the multiprocessing
# library. The entire communication between the sender and receiver processes is
# done using the multiprocessing.Queue class.
#
# Written by: Christoph Hänisch
# Last edited: 2025-02-15
# License: LGPL-3.0 (see LICENSE file)


import multiprocessing
import queue
import sys
import time
from typing import List, Tuple

import mido
from PySide6 import QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidgetItem


# Importing the midi_over_lan module
sys.path.append('.')
sys.path.append('..')
import midi_over_lan
from midi_sender import MidiSender
from midi_receiver import MidiReceiver

# To generate the python file from the ui file, run the following command:
# pyside6-uic .\MainWidget.ui -o MainWidget.py
from MainWidget import Ui_MainWidget


class MainWidget(QtWidgets.QWidget, Ui_MainWidget):
    """Main widget for the GUI."""

    def __init__(self):
        """Initialize the main widget."""
        super().__init__()
        self.setupUi(self)
        self.input_ports: List[Tuple[bool, str, str]] = []  # List of tuples (active, device_name, network_name)

        # Setup the table widget.
        self.tableWidget_LocalInputPorts.clearSelection()
        self.tableWidget_LocalInputPorts.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.tableWidget_LocalInputPorts.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.tableWidget_LocalInputPorts.setSortingEnabled(False)
        self.tableWidget_LocalInputPorts.itemClicked.connect(self.toggle_active_input_port)
        self.tableWidget_LocalInputPorts.itemChanged.connect(self.update_network_name)

        # Connect the buttons to the functions.
        self.pushButton_LocalInputPorts_SelectAll.clicked.connect(self.select_all_input_ports)
        self.pushButton_LocalInputPorts_UnselectAll.clicked.connect(self.unselect_all_input_ports)
        self.pushButton_LocalInputPorts_Refresh.clicked.connect(self.refresh_input_ports)
        self.pushButton_LocalInputPorts_Run.clicked.connect(self.run)
        self.pushButton_LocalInputPorts_Stop.clicked.connect(self.stop)

        # Add the input ports to the list.
        self.refresh_input_ports()


    def add_input_port(self, active: bool, device_name: str, network_name: str):
        """Add an input port to the internal list of input ports."""
        # Skip if the port is already in the list.
        for port in self.input_ports:
            if port[1] == device_name:
                return
        self.input_ports.append((active, device_name, network_name))
        self.tableWidget_LocalInputPorts.setRowCount(len(self.input_ports))
        row = len(self.input_ports) - 1
        item = QTableWidgetItem(device_name)
        item.setCheckState(Qt.Checked if active else Qt.Unchecked)
        item.setFlags(item.flags() & ~Qt.ItemIsEditable & ~Qt.ItemIsSelectable)
        self.tableWidget_LocalInputPorts.setItem(row, 0, item)
        self.tableWidget_LocalInputPorts.setItem(row, 1, QTableWidgetItem(network_name))


    def refresh_input_ports(self):
        """Refresh the list of internal input ports."""
        self.tableWidget_LocalInputPorts.clearContents()
        self.input_ports = []
        for input_port in mido.get_input_names():
            input_port = input_port.split(':')[0]
            self.add_input_port(False, input_port, input_port)


    def run(self):
        """Start the sending process."""


    def select_all_input_ports(self):
        """Select all input ports."""
        for row in range(self.tableWidget_LocalInputPorts.rowCount()):
            item = self.tableWidget_LocalInputPorts.item(row, 0)
            self.input_ports[row] = (True, self.input_ports[row][1], self.input_ports[row][2])
            item.setCheckState(Qt.Checked)


    def stop(self):
        """Stop the sending process."""


    def toggle_active_input_port(self, item: QTableWidgetItem):
        """Toggle the active state of the input port."""
        row = item.row()
        column = item.column()
        if column == 0:
            device_name = self.input_ports[row][1]
            network_name = self.input_ports[row][2]
            item = self.tableWidget_LocalInputPorts.item(row, 0)
            if item.checkState() == Qt.Checked:
                self.input_ports[row] = (False, device_name, network_name)
                item.setCheckState(Qt.Unchecked)
            else:
                self.input_ports[row] = (True, device_name, network_name)
                item.setCheckState(Qt.Checked)


    def unselect_all_input_ports(self):
        """Unselect all input ports."""
        for row in range(self.tableWidget_LocalInputPorts.rowCount()):
            self.input_ports[row] = (False, self.input_ports[row][1], self.input_ports[row][2])
            item = self.tableWidget_LocalInputPorts.item(row, 0)
            item.setCheckState(Qt.Unchecked)


    def update_network_name(self, item: QTableWidgetItem):
        """Update the network name of the input port."""
        row = item.row()
        column = item.column()
        if column == 1:
            active = self.input_ports[row][0]
            device_name = self.input_ports[row][1]
            network_name = item.text()
            self.input_ports[row] = (active, device_name, network_name)


def main():
    """Main function."""

#    # Create the sender and receiver processes
#    sender_queue = multiprocessing.Queue()  # Queue for sending commands to the sender process
#    receiver_queue = multiprocessing.Queue()  # Queue for sending commands to the receiver process
#    result_queue = multiprocessing.Queue()  # Queue for receiving results from the sender and receiver processes
#    sender = MidiSender(sender_queue, result_queue)
#    receiver = MidiReceiver(receiver_queue, result_queue)
#    sender.start()
#    receiver.start()

    # Create the GUI
    app = QtWidgets.QApplication(sys.argv)
    widget = MainWidget()
    widget.show()
    app.exec()

 #   sender_queue.put('stop')
 #   receiver_queue.put('stop')
 #   sender.join()
 #   receiver.join()


if __name__ == "__main__":
    main()
